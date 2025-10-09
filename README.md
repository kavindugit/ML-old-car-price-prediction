# ML Old Car Price Prediction

Predict used car prices with a modern Streamlit app powered by an XGBoost model and lightweight AI assistants. Enter details like brand, model, year, mileage, fuel, and transmission to get an instant estimate, market insights, and a visual gallery for the selected model.

### Highlights
- Fast, local inference with pre-trained XGBoost artifacts
- Streamlit UI with brand logos and curated brand→model lists
- Currency conversion (EUR, USD, GBP, LKR, INR, JPY)
- Optional DeepSeek-based market insights via OpenRouter
- Wikipedia/Commons image gallery for the chosen model and year


## Project Structure

ML-old-car-price-prediction-main/
  artifacts/
    direct_scaler.joblib
    feature_order.joblib
    log_scaler.joblib
    log_transformer.joblib
    model_target_mapping.csv
    model.joblib
  image_agent.py
  main.py
  prediction_helper.py
  requirements.txt
  runtime.txt
  vehical_agent.py
  Notebooks/
    data cleaning.ipynb
    Model_training.ipynb
    train_final.csv
    test_final.csv


- main.py: Streamlit app (UI, inputs, prediction trigger, insights, image gallery)
- prediction_helper.py: Preprocessing and model inference utilities
- image_agent.py: Fetches high-quality thumbnails from Wikipedia/Commons
- vehical_agent.py: AI market insights (DeepSeek via OpenRouter)
- artifacts/: Trained model and preprocessing assets required at runtime


## Quickstart

### 1) Requirements
- Python 3.10+ recommended
- Internet access (for images and optional insights)

### 2) Setup
bash
# From the repository root
cd ML-old-car-price-prediction-main
pip install -r requirements.txt


Optional: to enable AI market insights, set an OpenRouter API key.
bash
# PowerShell (Windows)
$Env:OPENROUTER_API_KEY = "sk-or-..."

# or create a .env file next to main.py
OPENROUTER_API_KEY=sk-or-...


### 3) Run the app
bash
streamlit run main.py

Then open the URL printed in the terminal (typically http://localhost:8501).
