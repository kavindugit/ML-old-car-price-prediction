# image_agent.py
from __future__ import annotations
import re
import requests
from requests.adapters import HTTPAdapter, Retry

WIKI_API = "https://en.wikipedia.org/w/api.php"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"

# -------- shared http session with retries + user-agent ----------
def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({
        # Wikimedia asks for a UA that identifies your app or email/domain
        "User-Agent": "VehiclePriceApp/1.0 (contact: your-email@example.com)"
    })
    retries = Retry(total=3, backoff_factor=0.3, status_forcelist=[429, 500, 502, 503, 504])
    s.mount("https://", HTTPAdapter(max_retries=retries))
    return s

# -------------------- helpers --------------------
def _year_score(title: str, year: int | None) -> int:
    """Higher is better. Prefer titles that contain the year or near years (±2)."""
    if not year:
        return 0
    years = [int(y) for y in re.findall(r"\b(19\d{2}|20\d{2})\b", title)]
    if not years:
        return -5  # small penalty if no year in title
    best_delta = min(abs(y - year) for y in years)
    # Reward close years, penalize far ones
    return 50 - best_delta if best_delta <= 2 else 10 - best_delta

def _norm(s: str) -> str:
    return s.replace("_", " ").strip()

# -------------------- wikipedia search paths --------------------
def _wikipedia_thumbnails(session: requests.Session, query: str, limit: int) -> list[dict]:
    """Use pageimages thumbnails from search results."""
    params = {
        "action": "query",
        "format": "json",
        "origin": "*",
        "generator": "search",
        "gsrsearch": query,
        "gsrlimit": limit,
        "prop": "pageimages",
        "piprop": "thumbnail",
        "pithumbsize": 900,
        "pilimit": limit,
    }
    r = session.get(WIKI_API, params=params, timeout=15)
    if r.status_code != 200:
        return []
    pages = r.json().get("query", {}).get("pages", {})
    out = []
    for p in pages.values():
        thumb = p.get("thumbnail", {}).get("source")
        if thumb:
            out.append({
                "thumb": thumb,
                "url": f"https://en.wikipedia.org/?curid={p['pageid']}",
                "title": p.get("title", "")
            })
    return out

def _wikipedia_page_images(session: requests.Session, title: str, limit: int) -> list[dict]:
    """
    Fetch images listed on a specific page (prop=images -> imageinfo).
    """
    # 1) get images file titles from the page
    r1 = session.get(WIKI_API, params={
        "action": "query", "format": "json", "origin": "*",
        "prop": "images", "titles": title, "imlimit": limit * 4
    }, timeout=15)
    if r1.status_code != 200:
        return []
    pages = r1.json().get("query", {}).get("pages", {})
    file_titles = []
    for p in pages.values():
        for im in p.get("images", []) or []:
            name = im.get("title", "")
            if name.lower().endswith((".jpg", ".jpeg", ".png")):
                file_titles.append(name)
    if not file_titles:
        return []

    # 2) get urls for those files
    r2 = session.get(WIKI_API, params={
        "action": "query", "format": "json", "origin": "*",
        "titles": "|".join(file_titles[:50]),
        "prop": "imageinfo", "iiprop": "url", "iiurlwidth": 1000
    }, timeout=20)
    if r2.status_code != 200:
        return []
    out = []
    for p in r2.json().get("query", {}).get("pages", {}).values():
        iinfo = (p.get("imageinfo") or [{}])[0]
        if not iinfo:
            continue
        thumb = iinfo.get("thumburl") or iinfo.get("url")
        url = iinfo.get("descriptionurl") or iinfo.get("url")
        if thumb and url:
            out.append({"thumb": thumb, "url": url, "title": p.get("title", "")})
    return out[:limit]

# -------------------- commons search paths --------------------
def _commons_search(session: requests.Session, query: str, limit: int) -> list[dict]:
    params = {
        "action": "query", "format": "json", "origin": "*",
        "generator": "search", "gsrnamespace": 6,  # files
        "gsrsearch": query, "gsrlimit": limit * 2,
        "prop": "imageinfo", "iiprop": "url", "iiurlwidth": 1000
    }
    r = session.get(COMMONS_API, params=params, timeout=20)
    if r.status_code != 200:
        return []
    pages = r.json().get("query", {}).get("pages", {})
    out = []
    for p in pages.values():
        iinfo = (p.get("imageinfo") or [{}])[0]
        if not iinfo:
            continue
        thumb = iinfo.get("thumburl") or iinfo.get("url")
        url = iinfo.get("descriptionurl") or iinfo.get("url")
        if thumb and url:
            out.append({"thumb": thumb, "url": url, "title": p.get("title", "")})
    return out[:limit]

def _commons_category_members(session: requests.Session, category: str, limit: int) -> list[dict]:
    """
    Try a category like 'Category:Toyota Corolla (E210)'.
    """
    params = {
        "action": "query", "format": "json", "origin": "*",
        "list": "categorymembers", "cmtitle": category,
        "cmnamespace": 6, "cmlimit": limit * 2
    }
    r = session.get(COMMONS_API, params=params, timeout=15)
    if r.status_code != 200:
        return []
    files = [m["title"] for m in r.json().get("query", {}).get("categorymembers", []) if m["title"].lower().endswith((".jpg", ".jpeg", ".png"))]
    if not files:
        return []
    r2 = session.get(COMMONS_API, params={
        "action": "query", "format": "json", "origin": "*",
        "titles": "|".join(files[:50]), "prop": "imageinfo",
        "iiprop": "url", "iiurlwidth": 1000
    }, timeout=20)
    if r2.status_code != 200:
        return []
    out = []
    for p in r2.json().get("query", {}).get("pages", {}).values():
        iinfo = (p.get("imageinfo") or [{}])[0]
        if not iinfo:
            continue
        thumb = iinfo.get("thumburl") or iinfo.get("url")
        url = iinfo.get("descriptionurl") or iinfo.get("url")
        if thumb and url:
            out.append({"thumb": thumb, "url": url, "title": p.get("title", "")})
    return out[:limit]

# -------------------- main entry --------------------
def fetch_model_images(brand: str, model: str, year: int | None = None, limit: int = 12) -> list[dict]:
    """
    Returns a list of {thumb, url, title}. Always tries multiple sources.
    Year is used for ranking (not filtering) so you still get results.
    """
    if not brand or not model:
        return []

    brand = _norm(brand)
    model = _norm(model)
    base = f"{brand} {model}"

    s = _session()
    seen = set()
    results: list[dict] = []

    # 1) Wikipedia thumbnails (fast)
    for q in [
        f'{base} car {year or ""}'.strip(),
        f"{base} (car)",
        f"{base} exterior",
        base,
    ]:
        for item in _wikipedia_thumbnails(s, q, limit):
            k = item["thumb"]
            if k not in seen:
                seen.add(k)
                results.append(item)
        if len(results) >= limit:
            break

    # 2) Wikipedia page images (from the best matching page title)
    if len(results) < limit:
        # try the main article title (best hit); fallback to base
        page_title = results[0]["title"] if results else base
        for item in _wikipedia_page_images(s, page_title, limit=(limit - len(results))):
            k = item["thumb"]
            if k not in seen:
                seen.add(k)
                results.append(item)

    # 3) Commons search
    if len(results) < limit:
        for q in [
            f'{base} {year or ""} front OR side',
            f"{base} car",
            base,
        ]:
            for item in _commons_search(s, q, limit=(limit - len(results))):
                k = item["thumb"]
                if k not in seen:
                    seen.add(k)
                    results.append(item)
            if len(results) >= limit:
                break

    # 4) Commons category guesses (helps for well-organized models)
    if len(results) < limit:
        guesses = [
            f"Category:{base}",
            f"Category:{brand} {model} (car)",
            f"Category:{brand} {model} (automobile)",
        ]
        for cat in guesses:
            for item in _commons_category_members(s, cat, limit=(limit - len(results))):
                k = item["thumb"]
                if k not in seen:
                    seen.add(k)
                    results.append(item)
            if len(results) >= limit:
                break

    # Rank by year proximity (do not filter)
    if year:
        results.sort(key=lambda x: _year_score(x.get("title", ""), year), reverse=True)

    return results[:limit]
