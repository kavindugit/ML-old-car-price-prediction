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

## Using the App
1. Choose a brand and model (brand logos render automatically).
2. Provide basic specs:
   - Manufacturing year; optionally a registration year/month
   - Power (HP), mileage (km)
   - Fuel type (petrol, diesel, electric, hybrid, etc.) and transmission
   - Fuel efficiency (km/L) or EV range where relevant
3. Select an output currency.
4. Click “Predict Price”. The app will:
   - Preprocess inputs and predict a base EUR price
   - Convert to your selected currency
   - Optionally generate a concise AI insights report (if OPENROUTER_API_KEY is set)
   - Fetch a gallery of images for the chosen brand/model/year


## How It Works (Overview)
Under the hood, prediction_helper.py performs feature engineering and applies the same transformations used during training:
- Derives vehicle age and cyclical month features
- Encodes brand and model (target encoding for model via model_target_mapping.csv)
- One-hot encodes categorical fields and aligns to feature_order.joblib
- Scales numeric features using log_scaler.joblib, log_transformer.joblib, and direct_scaler.joblib
- Runs the pre-trained model.joblib to obtain a price in EUR, then converts using a fixed lookup table

image_agent.py queries Wikipedia and Wikimedia Commons for high-quality thumbnails, ranking results by proximity to the selected year.

vehical_agent.py calls DeepSeek (via OpenRouter) to craft a short, markdown-formatted market insight report. This step is optional and requires OPENROUTER_API_KEY.


## Configuration
- Currency conversion rates are defined in prediction_helper.py under currency_rates.
- Image gallery size can be adjusted via the limit parameter in fetch_model_images.
- The Streamlit page title, emojis, and layout are configured at the top of main.py.

## Troubleshooting
- The app runs, but prediction fails: Ensure all files in artifacts/ exist and are readable.
- ImportError or version mismatch: Reinstall with pip install -r requirements.txt.
- Insights show an API error: Set a valid OPENROUTER_API_KEY in environment variables or .env.
- Images don’t appear: Wikipedia/Commons requests might throttle or have no matches for a rare model; try a different year/model.
- Streamlit cannot find files: Make sure you are running from the ML-old-car-price-prediction-main directory where main.py resides.


## Development Notes
- Notebooks in Notebooks/ document data cleaning and model training.
- If you change preprocessing, regenerate all relevant artifacts and update feature_order.joblib to match the trained pipeline.
- Follow the versions in requirements.txt for reproducibility.


## License
Add your preferred license here (e.g., MIT). Replace this section as needed.


## Acknowledgements
- Streamlit team for the excellent app framework
- Wikipedia and Wikimedia Commons contributors for open images
- OpenRouter and the DeepSeek model for optional insights
