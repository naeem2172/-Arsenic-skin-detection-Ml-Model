# Arsenic Detection – Flask Dashboard

Flask web app with an interactive dashboard for your Arsenic detection ML model. Use it while the model is training; integrate the trained model when ready.

## Quick start

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the app**
   ```bash
   python app.py
   ```
   Open **http://localhost:5000** in your browser.

## Integrating your trained model

1. **Save your model** (e.g. in your training script):
   ```python
   import joblib
   joblib.dump(model, "models/arsenic_model.pkl")
   ```

2. **Put the file in place**  
   Save the pickle file as `models/arsenic_model.pkl` in this project (or set `ARSENIC_MODEL_PATH` to your path).

3. **Match feature order in `app.py`**  
   In `predict_arsenic()`, set `order` to your actual feature names in the same order as in training:
   ```python
   order = ["your_feature_1", "your_feature_2", ...]
   ```

4. **Optional: change input form**  
   In `templates/predict.html`, replace the placeholder "Feature 1" / "Feature 2" inputs with your real feature names and IDs so the form sends the same keys as in `order`.

5. **Restart the app**  
   The app loads the model at startup; after saving the pickle and updating `order`, restart `python app.py`.

## Project layout

- `app.py` – Flask app, model loading, and prediction endpoint
- `templates/` – Dashboard and Predict pages
- `static/` – CSS and JS for the dashboard
- `models/` – Put your saved model here (`arsenic_model.pkl`)

## API

- `GET /` – Dashboard
- `GET /predict` – Predict page (form)
- `POST /predict` – JSON body with feature keys → returns `{ "prediction": ..., "label": "..." }`
- `GET /api/status` – `{ "model_loaded": true/false, "model_path": "..." }`
