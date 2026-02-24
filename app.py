"""
Arsenic Detection - Flask Dashboard (image-based)
Run this app and integrate your trained model when ready.
"""
import os
from pathlib import Path

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload

# ============== MODEL INTEGRATION ==============
# Set this path when your model is trained (e.g. "models/arsenic_model.pkl")
MODEL_PATH = os.environ.get("ARSENIC_MODEL_PATH", "models/arsenic_model.pkl")
model = None

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[-1].lower() in ALLOWED_EXTENSIONS


def load_model():
    """Load the trained model. Call this when your model file is ready."""
    global model
    if not os.path.isfile(MODEL_PATH):
        return False
    try:
        import joblib
        model = joblib.load(MODEL_PATH)
        return True
    except Exception as e:
        app.logger.warning(f"Model load failed: {e}")
        return False


def image_to_array(file_storage):
    """Read uploaded image and return numpy array (RGB). Adapt preprocessing for your model."""
    from PIL import Image
    import numpy as np
    img = Image.open(file_storage).convert("RGB")
    return np.array(img)


def predict_arsenic(image_array):
    """
    Run prediction on image. Override to match your trained model (e.g. resize, normalize, predict).
    image_array: numpy array of shape (H, W, 3) RGB.
    """
    if model is None:
        return None
    try:
        import numpy as np
        # Example: flatten or resize to your model's expected input shape
        # X = image_array.reshape(1, -1)  # or preprocess and pass to model
        # return model.predict(X)[0]
        # Placeholder until you integrate: use your actual preprocessing and model.predict
        X = image_array.reshape(1, -1)
        return model.predict(X)[0]
    except Exception as e:
        app.logger.error(f"Prediction error: {e}")
        return None


# Try to load model on startup (no error if not present)
load_model()


@app.route("/")
def index():
    return render_template("index.html", model_loaded=model is not None)


@app.route("/predict", methods=["GET", "POST"])
def predict():
    if request.method == "GET":
        return render_template("predict.html", model_loaded=model is not None)
    # POST: image file upload
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image file provided."}), 400
        file = request.files["image"]
        if not file or file.filename == "":
            return jsonify({"error": "No image file selected."}), 400
        if not allowed_file(file.filename):
            return jsonify({"error": "Allowed formats: JPEG, PNG."}), 400
        image_array = image_to_array(file)
        result = predict_arsenic(image_array)
        if result is None:
            return jsonify({
                "error": "Model not loaded or prediction failed. Train and save your model, then restart the application."
            }), 503
        label = "Arsenic detected" if result else "No arsenic"
        return jsonify({"prediction": float(result), "label": label})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/status")
def status():
    return jsonify({"model_loaded": model is not None, "model_path": MODEL_PATH})


if __name__ == "__main__":
    Path("models").mkdir(exist_ok=True)
    app.run(debug=True, host="0.0.0.0", port=5000)
