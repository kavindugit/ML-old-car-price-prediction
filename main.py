# ml-old-car-price-prediction/main.py
import streamlit as st
import re
import datetime
import warnings
from prediction_helper import predict
from vehical_agent import create_vehicle_insight_agent
from image_agent import fetch_model_images

warnings.filterwarnings("ignore", category=UserWarning)

# ---------------------------
# Page Configuration
# ---------------------------
st.set_page_config(
    page_title="🚗 Vehicle Price Prediction",
    page_icon="🚘",
    layout="wide"
)

# ---------------------------
# Header Section
# ---------------------------
st.title("🚗 Vehicle Price Prediction Dashboard")
st.markdown(
    "### Get an instant price prediction for any car model! "
    "Fill in the details below 👇"
)

# ---------------------------
# Brand Logos
# ---------------------------
brand_images = {
    # A
    "alfa-romeo": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Alfa_Romeo_Logo_2015.svg/512px-Alfa_Romeo_Logo_2015.svg.png",
    "aston-martin": "https://upload.wikimedia.org/wikipedia/en/thumb/7/7e/Aston_Martin_Lagonda_logo.svg/512px-Aston_Martin_Lagonda_logo.svg.png",
    "audi": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Audi_logo_detail.svg/512px-Audi_logo_detail.svg.png",

    # B
    "bentley": "https://upload.wikimedia.org/wikipedia/en/thumb/5/5d/Bentley_logo.svg/512px-Bentley_logo.svg.png",
    "bmw": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/BMW.svg/512px-BMW.svg.png",

    # C
    "cadillac": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Cadillac_logo2.svg/512px-Cadillac_logo2.svg.png",
    "chevrolet": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Chevrolet_logo.svg/512px-Chevrolet_logo.svg.png",
    "chrysler": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Chrysler_logo.svg/512px-Chrysler_logo.svg.png",
    "citroen": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Citroen_2022_logo.svg/512px-Citroen_2022_logo.svg.png",

    # D
    "dacia": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Dacia_logo_2021.svg/512px-Dacia_logo_2021.svg.png",
    "daewoo": "https://upload.wikimedia.org/wikipedia/en/thumb/5/5b/Daewoo_logo.svg/512px-Daewoo_logo.svg.png",
    "daihatsu": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/49/Daihatsu_logo.svg/512px-Daihatsu_logo.svg.png",
    "dodge": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/Dodge_logo.svg/512px-Dodge_logo.svg.png",

    # F
    "ferrari": "https://upload.wikimedia.org/wikipedia/en/thumb/4/4d/Ferrari-Logo.svg/512px-Ferrari-Logo.svg.png",
    "fiat": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/FIAT_logo.svg/512px-FIAT_logo.svg.png",
    "ford": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Ford_logo_flat.svg/512px-Ford_logo_flat.svg.png",

    # H / I
    "honda": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Honda-logo.svg/512px-Honda-logo.svg.png",
    "hyundai": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Hyundai_logo.svg/512px-Hyundai_logo.svg.png",
    "infiniti": "https://upload.wikimedia.org/wikipedia/en/thumb/4/4e/Infiniti_logo.svg/512px-Infiniti_logo.svg.png",
    "isuzu": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fb/Isuzu_logo.svg/512px-Isuzu_logo.svg.png",

    # J / K / L
    "jaguar": "https://upload.wikimedia.org/wikipedia/en/thumb/5/5e/Jaguar_logo_new.svg/512px-Jaguar_logo_new.svg.png",
    "jeep": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Jeep_logo.svg/512px-Jeep_logo.svg.png",
    "kia": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Kia_logo2.svg/512px-Kia_logo2.svg.png",
    "lada": "https://upload.wikimedia.org/wikipedia/en/thumb/2/29/Lada_logo.svg/512px-Lada_logo.svg.png",

    "lamborghini": "https://upload.wikimedia.org/wikipedia/en/thumb/8/8e/Lamborghini_Logo.svg/512px-Lamborghini_Logo.svg.png",
    "lancia": "https://upload.wikimedia.org/wikipedia/en/thumb/8/83/Lancia_Logo.svg/512px-Lancia_Logo.svg.png",
    "land-rover": "https://upload.wikimedia.org/wikipedia/en/thumb/8/8d/Land_Rover_logo.svg/512px-Land_Rover_logo.svg.png",

    # M
    "maserati": "https://upload.wikimedia.org/wikipedia/en/thumb/5/55/Maserati_logo.svg/512px-Maserati_logo.svg.png",
    "mazda": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/Mazda_logo.svg/512px-Mazda_logo.svg.png",
    "mercedes": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Mercedes-Logo.svg/512px-Mercedes-Logo.svg.png",

    # T
    "toyota": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9d/Toyota_logo.png/512px-Toyota_logo.png"
}


def wikimedia_svg_to_png(url: str, size: int = 512) -> str:
    """Convert a Wikimedia SVG URL to a PNG thumbnail URL."""
    m = re.match(r"(https://upload\.wikimedia\.org/wikipedia/(?:commons|en)/)([^/]+/[^/]+)/([^/]+\.svg)$", url)
    if not m:
        return url
    base, hashpath, filename = m.groups()
    return f"{base}thumb/{hashpath}/{filename}/{size}px-{filename}.png"
# ---------------------------
# Brand → Model Mapping (shortened for demo)
# ---------------------------
brand_model_mapping = { "alfa-romeo": [ "145","146","147","155","156","159","164","166","8c","alfa_6", "brera","giulia","giulietta","gt","gtv","mito",
                                        "spider","sportwagon", "stelvio","tonale" ],
                        "aston-martin": [ "db7","db9","db11","dbs","dbx","rapide","v8","vantage","vanquish","virage" ],
                        "audi": [ "50","80","a1","a2","a3","a4","a4_allroad","a5","a6","a6_allroad","a7","a8", "allroad","cabriolet","e-tron",
                                  "e-tron_gt","q2","q3","q4_e-tron","q5","q7","q8","q8_e-tron", "quattro","r8","rs","rs3","rs4","rs5","rs6","rs7",
                                  "rsq3","rsq8",
                                  "s1","s3","s4","s5","s6","s7","s8","sq2","sq5","sq7","sq8","tt","ttrs","tts" ],
                        "bentley": [ "arnage","azure","bentayga","brooklands","continental","continental_gt", "continental_gtc","flying_spur","mulsanne",
                                     "turbo_r" ],
                        "bmw": [ "114","116","118","120","123","125","128","130","135","140","1m_coupe", "214","216","218","220","223","225","228","230",
                                 "235","240", "316","318","320","323","325","328","330","335","340", "418","420","425","428","430","435","440", "518","520",
                                 "523","525","528","530","535","540","545","550", "620","630","635","640","645","650", "725","728","730","735","740","745",
                                 "750","760", "840","850", "active_hybrid_3","active_hybrid_7", "i3","i4","i5","i7","i8","ix","ix1","ix3", "m1","m2","m3","m4",
                                 "m5","m550","m6","m8","m850", "x1","x2","x2_m","x3","x3_m","x4","x4_m","x5","x5_m","x6","x6_m","x7","x7_m","xm", "z3","z3_m",
                                 "z4","z4_m","z8" ],
                        "cadillac": ["ats","bls","ct6","cts","eldorado","escalade","seville","srx","sts","xt4","xt5","xt6"],
                        "chevrolet": [ "2500","aveo","blazer","bolt","c1500","camaro","captiva","chevy_van","colorado", "corvette","cruze","express","kalos","matiz","orlando","silverado","spark", "suburban","trailblazer","trax" ],
                        "chrysler": ["200","pacifica","ram_van"],
                        "citroen": [ "ami","berlingo","c-crosser","c-elysée","c-zero","c1","c2","c3","c3_aircross","c3_picasso", "c35","c4","c4_aircross","c4_cactus","c4_picasso","c4_spacetourer", "c4_grand_picasso","c4_grand_spacetourer","c5","c5_aircross","c5_x", "c6","c8","ds","ds3","ds4","ds5","e-c4_electric",
                                     "e-c4_x","jumper","jumpy","nemo","spacetourer", "xantia","xsara","xsara_picasso","continental" ],
                        "dacia": ["dokker","duster","jogger","lodgy","logan","pick_up","sandero","spring"],
                        "daewoo": ["evanda","kalos","lacetti","lanos","matiz","nubira","rezzo","tacuma","espero"],
                        "daihatsu": ["applause","charade","copen","cuore","materia","move","sirion","terios","trevis","yrv"],
                        "dodge": ["avenger","caliber","challenger","charger","durango","grand_caravan","journey","nitro","ram"],
                        "ferrari": [ "296","348","360","430_scuderia","456","458","488","512","550","575","599","612","812", "california",
                                     "f12","f355","f430","f8_tributo","f8_spider","ff","gtc4_lusso", "mondial","portofino","roma","sf90_spider","sf90_stradale" ],
                        "fiat": [ "124_spider","500","500c","500e","500l","500x","595_abarth","bravo","croma", "doblo","ducato","e-doblo","fiorino","freemont",
                                  "fullback","grande_punto", "idea","linea","multipla","new_panda","panda","punto","punto_evo","qubo","scudo","sedici", "seicento",
                                  "stilo","strada","talento","tipo","ulysse" ],
                        "ford": [ "b-max","bronco","c-max","courier","crown","e-transit","ecosport","edge", "escort","expedition","explorer","f150","f250","f350","fiesta",
                                  "flex","focus", "focus_c-max","focus_cc","fusion","galaxy","gran_torino","grand_c-max", "grand_tourneo","ka","kuga","m","maverick","mondeo",
                                  "mustang","mustang_mach_e", "probe","puma","ranger","ranger_raptor","s-max","streetka","tourneo", "tourneo_connect","tourneo_courier",
                                  "tourneo_custom","tourneo_grand", "transit","transit_bus","transit_connect","transit_courier","transit_custom","windstar" ],
                        "honda": ["accord","civic","cr-v","e","hr-v","insight","jazz","nsx","odyssey","stream"],
                        "hyundai": [ "accent","atos","bayon","coupe","elantra","genesis","genesis_coupe","getz", "grand_santa_fe","h1","h350","i10","i20","i30","i40","ioniq","ioniq5","ioniq6", "ix20","ix35","ix55","kona","kona_electric","matrix","nexo","santa_fe","sonata", "staria","terracan","tucson","veloster" ],
                        "infiniti": ["ex30","ex35","ex37","fx","g37","m30","m35","m37","q30","q50","q60","q70","qx30","qx50","qx60","qx70","qx80"],
                        "isuzu": ["d-max","trooper"], "jaguar": ["e-pace","f-pace","f-type","i-pace","x-type","xe","xf","xj","xk","xkr"],
                        "jeep": ["avenger","cherokee","commander","compass","gladiator","grand_cherokee","patriot","renegade","wagoneer","wrangler"],
                        "kia": ["carens","carnival","ceed","ceed_sw","cerato","e-niro","ev6","joice","niro","opirus","optima","picanto","proceed","rio","sorento","soul","sportage","stinger","stonic","venga","xceed"],
                        "lada": ["111","4x4","granta","kalina","niva","nova","priora","taiga","urban","vesta"],
                        "lamborghini": ["aventador","diablo","gallardo","huracan","murciélago","urus"],
                        "lancia": ["dedra","delta","flavia","kappa","lybra","musa","phedra","thema","thesis","voyager","y","ypsilon","zeta"],
                        "land-rover": ["defender","discovery","discovery_sport","freelander","range_rover","range_rover_evoque","range_rover_sport","range_rover_velar"],
                        "maserati": ["3200","4200","coupe","ghibli","grancabrio","gransport","granturismo","grecale","levante","mc20","quattroporte","spyder"],
                        "mazda": ["2","3","5","6","bt-50","cx-3","cx-30","cx-5","cx-7","cx-9","mx-5","rx-8","tribute"]
                    }


brands = sorted(brand_model_mapping.keys())

# ---------------------------
# Layout: Two-column structure
# ---------------------------
with st.container():
    st.subheader("🧾 Vehicle Information")

    col1, col2 = st.columns([1, 1.3])

    # --- Column 1: General info ---
    with col1:
        brand = st.selectbox("Select Brand", brands, key="brand_select")
         
        logo_url = brand_images.get(brand)
        if logo_url:
            if logo_url.endswith(".svg"):
                logo_url = wikimedia_svg_to_png(logo_url, 160)
            st.image(logo_url, width=120)    



        models_for_brand = brand_model_mapping.get(brand, [])
        model = st.selectbox(
            "Select Model",
            sorted(models_for_brand),
            key="model_select"
        )

        color = st.selectbox(
            "Color",
            ["black", "blue", "red", "white", "silver", "grey", "other"],
            key="color_select"
        )

        transmission_type = st.selectbox(
            "Transmission Type",
            ["manual", "automatic", "semi-automatic"],
            key="transmission_select"
        )

        fuel_type = st.selectbox(
            "Fuel Type",
            ["petrol", "diesel", "electric", "hybrid", "lpg", "ethanol", "hydrogen"],
            key="fuel_select"
        )

    # --- Column 2: Technical details ---
    with col2:
        st.subheader("⚙️ Specifications")

        year = st.number_input(
            "Manufacturing Year",
            min_value=1980,
            max_value=2025,
            value=2015,
            step=1,
            key="year_input"
        )
        skip_reg_year = st.checkbox("I don't know the registration year", value=True, key="skip_reg_year")
        
        if skip_reg_year:
    # Auto-derive registration year/month from manufacturing year
            reg_year = year
    # pick a sensible default month; you can change to current month if you prefer
            reg_month = 1
            st.caption("📌 Using manufacturing year as registration year (Jan) since you chose to skip it.")
        else:
    # If user wants to provide it, enforce >= manufacturing year
            reg_year_default = 2018 if 2018 >= year else year
            reg_year = st.number_input(
                "Registration Year",
                min_value=year,     # only enforced when user opts in
                max_value=2025,
                value=reg_year_default,
                step=1,
                key="reg_year_input"
            )
        reg_month = st.selectbox(
            "Registration Month",
            list(range(1, 13)),
            format_func=lambda x: datetime.date(2000, x, 1).strftime("%B"),
            key="reg_month_input"
        )
        registration_date = datetime.date(reg_year, reg_month, 1)

        power_hp = st.number_input(
            "Power (Horsepower, HP)",
            min_value=30,
            max_value=1500,
            value=120,
            step=5,
            key="power_hp_input"
        )

        if fuel_type.lower() == "electric":
            ev_range_km = st.number_input(
                "EV Range (km)", min_value=50, max_value=1000, step=10, key="ev_range"
            )
            fuel_efficiency = 0
        elif fuel_type.lower() == "hybrid":
            fuel_efficiency = st.number_input(
                "Fuel Efficiency (km/L)",
                min_value=1.0,
                max_value=50.0,
                value=20.0,
                step=0.1,
                key="fuel_eff"
            )
            ev_range_km = st.number_input(
                "EV Range (km)", min_value=10, max_value=200, value=50, step=5, key="ev_range"
            )
        else:
            fuel_efficiency = st.number_input(
                "Fuel Efficiency (km/L)",
                min_value=1.0,
                max_value=50.0,
                value=20.0,
                step=0.1,
                key="fuel_eff"
            )
            ev_range_km = 0

        mileage_in_km = st.number_input(
            "Mileage (km)", min_value=0, max_value=500000, step=1000, value=40000, key="mileage"
        )
        currency = st.selectbox(
            "Select Output Currency",
            ["EUR", "USD", "GBP", "LKR", "INR", "JPY"],
            key="currency"
        )

# ---------------------------
# Input collection
# ---------------------------
input_dict = {
    "brand": brand,
    "model": model,
    "color": color,
    "registration_date": str(registration_date),
    "year": year,
    "power_hp": power_hp,
    "transmission_type": transmission_type,
    "fuel_type": fuel_type,
    "fuel_efficiency": fuel_efficiency,
    "mileage_in_km": mileage_in_km,
    "ev_range_km": ev_range_km,
    "currency": currency,
}

# ---------------------------
# Prediction Button
# ---------------------------
st.markdown("---")
st.subheader("💡 Predict Vehicle Price")

predict_btn = st.button("🔮 Predict Price", use_container_width=True)
if predict_btn:
    if not model:
        st.error("❌ Please select a valid model for this brand before predicting.")
    else:
        converted_price, prediction_eur = predict(input_dict)
        st.success(f"💰 Predicted Vehicle Price: **{converted_price:,.2f} {currency}**")
        st.caption(f"(Base prediction in EUR: €{prediction_eur:,.2f})")
        st.balloons()

        # --- Automatically generate Gemini insights ---
        with st.spinner("Analyzing latest market insights with Gemini AI..."):
            insights = create_vehicle_insight_agent(brand, model, prediction_eur)

        # --- Display AI-generated report ---
        st.markdown("### 🔍 Vehicle Market Insights")
        st.markdown(insights)

        st.markdown("### 🖼️ Model Gallery")

# 'brand', 'model', 'year' already exist from your form

images = fetch_model_images(brand=brand, model=model, year=year, limit=12)

if not images:
    st.info("No images found right now. Try a different model, brand, or year.")
else:
    cols = st.columns(3)
    caption = model.replace("_", " ").title()
    for i, item in enumerate(images):
        with cols[i % 3]:
            st.image(item["thumb"], caption=caption, use_container_width=True)

       
# ---------------------------
# Footer
# ---------------------------
st.markdown("---")
st.caption("© 2025 Vehicle Price Predictor | Powered by Streamlit + XGBoost")
