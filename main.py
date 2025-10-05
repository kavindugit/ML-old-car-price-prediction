import streamlit as st
import datetime
import warnings
from prediction_helper import predict


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
    "audi": "https://upload.wikimedia.org/wikipedia/commons/6/6f/Audi_logo_detail.svg",
    "bmw": "https://upload.wikimedia.org/wikipedia/commons/4/44/BMW.svg",
    "ford": "https://upload.wikimedia.org/wikipedia/commons/3/3e/Ford_logo_flat.svg",
    "hyundai": "https://upload.wikimedia.org/wikipedia/commons/4/44/Hyundai_logo.svg",
    "kia": "https://upload.wikimedia.org/wikipedia/commons/4/47/Kia_logo2.svg",
    "mazda": "https://upload.wikimedia.org/wikipedia/commons/6/60/Mazda_logo.svg",
    "mercedes": "https://upload.wikimedia.org/wikipedia/commons/9/90/Mercedes-Logo.svg",
    "toyota": "https://upload.wikimedia.org/wikipedia/commons/9/9d/Toyota_logo.png"
}

# ---------------------------
# Brand → Model Mapping (shortened for demo)
# ---------------------------
brand_model_mapping = {
    "audi": ["a1", "a3", "a4", "a5", "a6", "a7", "a8", "q3", "q5", "q7", "q8", "rs6"],
    "bmw": ["1_series", "3_series", "5_series", "7_series", "x1", "x3", "x5", "x7", "m3", "m4"],
    "ford": ["fiesta", "focus", "mondeo", "mustang", "kuga", "puma", "ranger"],
    "hyundai": ["i10", "i20", "i30", "kona", "tucson", "santa_fe", "ioniq", "staria"],
    "kia": ["rio", "ceed", "optima", "sportage", "stinger", "sorento", "niro", "ev6"],
    "mazda": ["2", "3", "6", "cx-3", "cx-5", "cx-9", "mx-5"],
    "mercedes": ["a_class", "c_class", "e_class", "s_class", "gla", "glc", "gle", "gls"],
    "toyota": ["corolla", "camry", "rav4", "yaris", "hilux", "chr", "land_cruiser"]
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

        if brand in brand_images:
            st.image(brand_images[brand], width=120)

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
            step=1,
            key="year_input"
        )

        reg_year = st.number_input(
            "Registration Year",
            min_value=1980,
            max_value=2025,
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
                step=0.1,
                key="fuel_eff"
            )
            ev_range_km = st.number_input(
                "EV Range (km)", min_value=10, max_value=200, step=5, key="ev_range"
            )
        else:
            fuel_efficiency = st.number_input(
                "Fuel Efficiency (km/L)",
                min_value=1.0,
                max_value=50.0,
                step=0.1,
                key="fuel_eff"
            )
            ev_range_km = 0

        mileage_in_km = st.number_input(
            "Mileage (km)", min_value=0, max_value=500000, step=1000, key="mileage"
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

       
# ---------------------------
# Footer
# ---------------------------
st.markdown("---")
st.caption("© 2025 Vehicle Price Predictor | Powered by Streamlit + XGBoost")
