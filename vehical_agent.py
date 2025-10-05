"""
🚗 Vehicle Insight Agent — DeepSeek V3.1 Advanced Edition (Free)
Delivers intelligent market insights, model comparisons, and recommendations
using the DeepSeek-V3.1 model via OpenRouter.
"""

import os
import streamlit as st
from dotenv import load_dotenv
import requests

# ----------------------------------------
# 🔑 API Key Loader
# ----------------------------------------
def _get_api_key():
    """Fetch API key from Streamlit secrets or .env"""
    try:
        if hasattr(st, "secrets") and "OPENROUTER_API_KEY" in st.secrets:
            return st.secrets["OPENROUTER_API_KEY"]
    except Exception:
        pass

    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("❌ OPENROUTER_API_KEY not found! Add it to .env or Streamlit secrets.")
    return api_key


# ----------------------------------------
# 🧠 DeepSeek Agent Function
# ----------------------------------------
def create_vehicle_insight_agent(brand: str, model: str, predicted_price: float = None):
    """
    Generates advanced, data-driven automotive insights using DeepSeek-V3.1.
    """

    if not brand or not model:
        return "⚠️ Brand or model not provided."

    price_context = (
        f"The estimated used market price for {brand.title()} {model.title()} is around €{predicted_price:,.0f}."
        if predicted_price
        else "No price data provided."
    )

    prompt = f"""
    You are an expert **automotive market strategist and car buying consultant**.
    You are preparing a detailed vehicle insight report for a customer who entered:

    - Brand: {brand.title()}
    - Model: {model.title()}
    - {price_context}

    Write an **engaging, well-structured, Markdown-formatted** report that is useful
    for car enthusiasts, first-time buyers, and used car investors.

    Your report must include:

    🚘 **1️⃣ Brand DNA & Reputation**
    - Summarize the brand’s history, identity, and reliability image.
    - Highlight innovation areas (EVs, design philosophy, safety standards).

    🚗 **2️⃣ Model Overview**
    - Describe production years, class, design, technology, and performance.
    - Include engine types, fuel options, comfort, and interior tech.

    🔍 **3️⃣ Same-Brand Model Comparison**
    - Compare the selected model with **3–5 other models** from {brand.title()}.
    - Show differences in size, price range, power, and purpose (e.g., family vs sport).
    - Give short recommendations for each (“Best for city driving”, “Best value for resale”, etc.).

    ⚖️ **4️⃣ Cross-Brand Market Rivals**
    - Compare {brand.title()} {model.title()} with **rival models from other brands**
      (like BMW, Audi, Toyota, Hyundai, etc.) that compete in the same segment.
    - Mention pros/cons or market advantages of each rival.

    💰 **5️⃣ Investment & Resale Value**
    - Discuss reliability, depreciation, and average resale potential (1–5 scale).
    - Give resale forecast in 2–3 years based on European market trends.

    🔋 **6️⃣ Innovation & Tech Features**
    - Mention noteworthy tech, sustainability focus, or EV versions.
    - Highlight new models with hybrid or electric options if available.

    🌍 **7️⃣ Global Market Trend**
    - Explain how demand for {brand.title()} vehicles is shifting globally.
    - Add a short comment about EV transition, fuel economy, and digital features.

    💡 **8️⃣ Expert Recommendation**
    - Give a 3-line buying advice summary for {brand.title()} {model.title()}.
    - Tailor it differently for:
        - First-time buyers
        - Family users
        - Car enthusiasts / collectors

    ⚙️ Keep tone: **professional, confident, but easy-to-read**.
    Use emojis and bold subheadings.
    Keep under **600 words**, use bullet points and short paragraphs.
    """

    try:
        api_key = _get_api_key()

        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://openrouter.ai",
            "X-Title": "Vehicle Market Insight Agent"
        }

        data = {
            "model": "deepseek/deepseek-chat",
            "messages": [{"role": "user", "content": prompt}]
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=90
        )

        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            return content.strip()
        else:
            return f"⚠️ DeepSeek API Error {response.status_code}: {response.text}"

    except Exception as e:
        return f"⚠️ DeepSeek Agent Error: {str(e)}"
