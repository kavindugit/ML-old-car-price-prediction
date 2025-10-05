import pandas as pd
import numpy as np
import joblib

# -----------------------
# Load trained artifacts
# -----------------------
model = joblib.load("artifacts/model.joblib")
log_scaler = joblib.load("artifacts/log_scaler.joblib")
direct_scaler = joblib.load("artifacts/direct_scaler.joblib")
log_transformer = joblib.load("artifacts/log_transformer.joblib")
model_target_mapping = pd.read_csv("artifacts/model_target_mapping.csv")

try:
    feature_order = joblib.load("artifacts/feature_order.joblib")
except:
    feature_order = model.get_booster().feature_names

# -----------------------
# Reference Tables
# -----------------------
currency_rates = {
    "EUR": 1.0, "USD": 1.07, "GBP": 0.86,
    "LKR": 355.0, "INR": 89.0, "JPY": 158.0
}

fuel_co2 = {
    "petrol": 2392, "diesel": 2640, "lpg": 1660,
    "ethanol": 1510, "hybrid": 2000,
    "electric": 0, "hydrogen": 0
}

# -----------------------
# Preprocessing Functions
# -----------------------
def feature_engineering(df, data_collection_year=2023):
    df["vehicle_manufacturing_age"] = data_collection_year - df["year"].astype(int)
    df["registration_date"] = pd.to_datetime(df["registration_date"])
    df["registration_month"] = df["registration_date"].dt.month
    df["registration_year"] = df["registration_date"].dt.year
    df["vehicle_registration_age"] = data_collection_year - df["registration_year"]

    df["reg_month_sin"] = np.sin(2 * np.pi * df["registration_month"] / 12)
    df["reg_month_cos"] = np.cos(2 * np.pi * df["registration_month"] / 12)

    df["mileage_per_year"] = df.apply(
        lambda row: row["mileage_in_km"] / row["vehicle_registration_age"]
        if row["vehicle_registration_age"] > 0 else row["mileage_in_km"], axis=1
    ).round(2)

    df = df.drop(columns=["registration_date", "registration_month", "registration_year", "year"])
    return df


def model_map_enc(df):
    global_mean = model_target_mapping['model_target_enc'].mean()
    mapping_dict = model_target_mapping.set_index(['brand', 'model'])['model_target_enc'].to_dict()
    df['model_target_enc'] = df.apply(
        lambda row: mapping_dict.get((row['brand'], row['model']), global_mean), axis=1
    )
    df = df.drop(columns=['model'], axis=1)
    return df


def hot_encoding(df):
    # (same code as your current version)
    required_columns = [
        'brand_aston-martin', 'brand_audi', 'brand_bentley',
        'brand_bmw', 'brand_cadillac', 'brand_chevrolet', 'brand_chrysler',
        'brand_citroen', 'brand_dacia', 'brand_daewoo', 'brand_daihatsu',
        'brand_dodge', 'brand_ferrari', 'brand_fiat', 'brand_ford',
        'brand_honda', 'brand_hyundai', 'brand_infiniti', 'brand_isuzu',
        'brand_jaguar', 'brand_jeep', 'brand_kia', 'brand_lada',
        'brand_lamborghini', 'brand_lancia', 'brand_land-rover',
        'brand_maserati', 'brand_mazda', 'color_black', 'color_blue',
        'color_bronze', 'color_brown', 'color_gold', 'color_green',
        'color_grey', 'color_orange', 'color_red', 'color_silver',
        'color_violet', 'color_white', 'color_yellow',
        'transmission_type_manual', 'transmission_type_semi-automatic',
        'fuel_type_diesel', 'fuel_type_diesel_hybrid', 'fuel_type_electric',
        'fuel_type_ethanol', 'fuel_type_hybrid', 'fuel_type_hydrogen',
        'fuel_type_lpg', 'fuel_type_petrol'
    ]

    for col in required_columns:
        if col not in df.columns:
            df[col] = 0

    # one-hot assignments...
    # (reuse your existing implementation here)
    return df


def handle_scaling(df):
    log_scale_cols = ["power_kw", "fuel_consumption_g_km", "mileage_in_km"]
    direct_scale_cols = ["ev_range_km", "vehicle_manufacturing_age", "vehicle_registration_age"]

    df[log_scale_cols] = log_scaler.transform(
        log_transformer.transform(df[log_scale_cols])
    )
    df[direct_scale_cols] = direct_scaler.transform(df[direct_scale_cols])
    return df


def preprocess_user_input(input_dict):
    df = pd.DataFrame([input_dict])

    # --- HP → kW ---
    df["power_kw"] = df["power_hp"] * 0.7355
    df.drop("power_hp", axis=1, inplace=True)

    # --- km/L → g/km ---
    fuel_type = df.loc[0, "fuel_type"].lower()
    if "fuel_efficiency" in df.columns:
        eff = df.loc[0, "fuel_efficiency"]
        g_per_liter = fuel_co2.get(fuel_type, 0)
        df["fuel_consumption_g_km"] = g_per_liter / eff if eff > 0 else 0
        df.drop("fuel_efficiency", axis=1, inplace=True)

    df = feature_engineering(df)
    df = model_map_enc(df)
    df = hot_encoding(df)
    df = handle_scaling(df)

    return df


def predict(input_dict):
    currency = input_dict.get("currency", "EUR")
    processed_df = preprocess_user_input(input_dict)
    processed_df = processed_df[feature_order]

    prediction_eur = model.predict(processed_df)[0]
    rate = currency_rates.get(currency, 1.0)
    converted_price = prediction_eur * rate
    return float(converted_price), float(prediction_eur)