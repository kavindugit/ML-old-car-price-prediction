
import streamlit as st
import warnings
import datetime
import os

# Add error handling for imports and file loading
try:
    from prediction_helper import predict
    st.success("✅ Prediction helper loaded successfully")
except Exception as e:
    st.error(f"❌ Error loading prediction helper: {str(e)}")
    st.stop()

warnings.filterwarnings("ignore", category=UserWarning)

st.set_page_config(page_title="🚗 Vehicle Price Prediction", layout="wide")

st.title("🚗 Vehicle Price Prediction")
st.write("Select vehicle details below and get an instant price prediction!")

# ---------------------------
# Brand Logos / Images
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
# Brand → Model Mapping (shortened here, extend as needed)
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
# UI Layout
# ---------------------------
col1, col2 = st.columns([1, 3])

with col1:
    brand = st.selectbox("Select Brand", brands)
    if brand in brand_images:
        st.image(brand_images[brand], width=120)

    models_for_brand = brand_model_mapping.get(brand, [])
    model = st.selectbox("Select Model", sorted(models_for_brand)) if models_for_brand else ""

    color = st.selectbox("Color", ["black", "blue", "red", "white", "silver", "grey", "other"])
    transmission_type = st.selectbox("Transmission Type", ["manual", "automatic", "semi-automatic"])
    fuel_type = st.selectbox("Fuel Type", ["petrol", "diesel", "electric", "hybrid", "lpg", "ethanol", "hydrogen"])

with col2:
    st.subheader("Vehicle Specifications")

    year = st.number_input("Manufacturing Year", min_value=1980, max_value=2025, step=1)

    reg_year = st.number_input("Registration Year", min_value=1980, max_value=2025, step=1)
    reg_month = st.selectbox("Registration Month", list(range(1, 13)),
                             format_func=lambda x: datetime.date(2000, x, 1).strftime("%B"))
    registration_date = datetime.date(reg_year, reg_month, 1)

    power_hp = st.number_input("Power (Horsepower, HP)", min_value=30, max_value=1500, step=5)

    if fuel_type.lower() == "electric":
        ev_range_km = st.number_input("EV Range (km)", min_value=50, max_value=1000, step=10)
        fuel_efficiency = 0
    elif fuel_type.lower() == "hybrid":
        fuel_efficiency = st.number_input("Fuel Efficiency (km/L)", min_value=1.0, max_value=50.0, step=0.1)
        ev_range_km = st.number_input("EV Range (km)", min_value=10, max_value=200, step=5)
    else:
        fuel_efficiency = st.number_input("Fuel Efficiency (km/L)", min_value=1.0, max_value=50.0, step=0.1)
        ev_range_km = 0

    mileage_in_km = st.number_input("Mileage (km)", min_value=0, max_value=500000, step=1000)
    currency = st.selectbox("Select Output Currency", ["EUR", "USD", "GBP", "LKR", "INR", "JPY"])

# ---------------------------
# Collect Inputs
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
    "currency": currency
}

# ---------------------------
# Prediction
# ---------------------------
if st.button("🔮 Predict Price"):
    if not model:
        st.error("❌ Please select a valid model for this brand before predicting.")
    else:
        converted_price, prediction_eur = predict(input_dict)
        st.success(f"💰 Predicted Vehicle Price: {converted_price:,.2f} {currency}")
        st.caption(f"(Base prediction in EUR: €{prediction_eur:,.2f})")
        st.balloons()

