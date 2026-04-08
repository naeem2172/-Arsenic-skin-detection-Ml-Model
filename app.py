"""
Arsenic Detection - Flask Dashboard (image-based)
With user registration, login, and prediction form.
"""
import os
from pathlib import Path

# Load .env from project root (must happen before reading env vars)
_env_path = Path(__file__).resolve().parent / ".env"
if _env_path.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_path)
    except ImportError:
        pass

from functools import wraps
from datetime import datetime

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash

import auth

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "arsenic-detection-secret-key-change-in-production")


def _api_error_json(status_code, error=None):
    """Return JSON for API errors so frontend never gets HTML."""
    return jsonify({"error": error or "An error occurred"}), status_code


@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/api/"):
        return _api_error_json(404, "Not found")
    return e.get_response(request.environ) if hasattr(e, "get_response") else (_api_error_json(404, "Not found")[0], 404)


@app.errorhandler(405)
def method_not_allowed(e):
    if request.path.startswith("/api/"):
        return _api_error_json(405, "Method not allowed")
    return e.get_response(request.environ) if hasattr(e, "get_response") else (_api_error_json(405, "Method not allowed")[0], 405)


@app.errorhandler(500)
def internal_error(e):
    app.logger.exception("Server error")
    if request.path.startswith("/api/"):
        return _api_error_json(500, str(e) if str(e) else "Internal server error")
    return _api_error_json(500, "Internal server error")


@app.context_processor
def inject_globals():
    return {
        "current_year": datetime.now().year,
        "user_logged_in": bool(session.get("user_email")),
    }


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user_email"):
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"error": "Please log in first.", "redirect": url_for("login")}), 401
            flash("Please log in to continue.", "info")
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated


# ============== MODEL ==============
# arsenic_skin_detection_advanced_model.h5: index 0=infected, index 1=not_infected (verified with IMG_1169)
# Arsenic image -> high prob_class_0 -> "Arsenic detected". No arsenic -> high prob_class_1 -> "No arsenic"
ARSENIC_INFECTED_CLASS = int(os.environ.get("ARSENIC_INFECTED_CLASS", os.environ.get("ARSENIC_CLASS_INDEX", "0")))
BASE_DIR = Path(__file__).resolve().parent
MODEL_FILE = "arsenic_skin_detection_advanced_model.h5"
_model_path = os.environ.get("ARSENIC_MODEL_PATH")
MODEL_PATH = Path(_model_path) if _model_path else (BASE_DIR / "models" / MODEL_FILE)
if not MODEL_PATH.is_absolute():
    MODEL_PATH = BASE_DIR / MODEL_PATH
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

_model = None


def _load_model():
    """Load model once. Returns model or None."""
    global _model
    if _model is not None:
        return _model
    if not MODEL_PATH.is_file():
        app.logger.warning(f"Model not found: {MODEL_PATH}")
        return None
    try:
        import tensorflow as tf
        _model = tf.keras.models.load_model(str(MODEL_PATH))
        app.logger.info(f"Model loaded from {MODEL_PATH}")
        return _model
    except Exception as e:
        app.logger.warning(f"Model load failed: {e}")
        return None


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[-1].lower() in ALLOWED_EXTENSIONS


def image_to_array(file_storage):
    from PIL import Image
    import numpy as np
    file_storage.seek(0)
    img = Image.open(file_storage).convert("RGB")
    return np.array(img)


def _preprocess_image(image_array):
    """Preprocess image to match notebook exactly: 128x128 RGB, /255, float32."""
    import numpy as np
    from PIL import Image
    img = Image.fromarray(np.asarray(image_array, dtype=np.uint8)).convert("RGB")
    img = img.resize((128, 128))  # Match notebook: default PIL resize
    X = np.array(img, dtype=np.float32) / 255.0
    return np.expand_dims(X, axis=0)


def predict_arsenic(image_array):
    """Predict using trained model. Returns (prob_infected, predicted_class).
    predicted_class: ARSENIC_INFECTED_CLASS=infected, else=not_infected."""
    model = _load_model()
    if model is None:
        return None
    try:
        import numpy as np
        X = _preprocess_image(image_array)
        pred = model.predict(X, verbose=0)
        pred = np.squeeze(pred)
        if pred.ndim == 1 and len(pred) >= 2:
            probs = np.array(pred, dtype=np.float64)
            predicted_class = int(np.argmax(probs))  # Model's decision: which class has higher prob
            prob_infected = float(probs[ARSENIC_INFECTED_CLASS])
            return (prob_infected, predicted_class)
        if pred.ndim == 0:
            p = float(pred)
            return (p, ARSENIC_INFECTED_CLASS if p >= 0.5 else (1 - ARSENIC_INFECTED_CLASS))
        return (float(pred[0]), 0)
    except Exception as e:
        app.logger.error(f"Prediction error: {e}")
        return None


# Pre-load at startup
if _load_model():
    print(f"[OK] Model loaded: {MODEL_PATH}")
    print(f"[OK] Prediction: class {ARSENIC_INFECTED_CLASS}=Arsenic detected, class {1-ARSENIC_INFECTED_CLASS}=No arsenic")
else:
    print(f"[WARN] Model not found at {MODEL_PATH}")


# ============== AUTH ==============
@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_email"):
        return redirect(url_for("index"))
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        name = request.form.get("name", "").strip()
        ok, msg = auth.register_user(email, password, name)
        if ok:
            flash(msg, "success")
            return redirect(url_for("login"))
        flash(msg, "error")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_email"):
        return redirect(url_for("index"))
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        ok, msg = auth.verify_user(email, password)
        if ok:
            session["user_email"] = email
            next_url = request.args.get("next") or url_for("index")
            return redirect(next_url)
        flash(msg, "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user_email", None)
    return redirect(url_for("index"))


# ============== ROUTES ==============
@app.route("/")
def index():
    return render_template(
        "index.html",
        model_loaded=_load_model() is not None,
        chatbot_available=get_chatbot() is not None,
    )


@app.route("/predict", methods=["GET", "POST"])
@login_required
def predict():
    if request.method == "GET":
        return render_template(
            "predict.html",
            model_loaded=_load_model() is not None,
            user_email=session.get("user_email", ""),
        )

    # Review form: has rating + prediction_label (only review form sends these), no image file
    has_rating = request.form.get("rating")
    has_pred_label = request.form.get("prediction_label")
    has_image = request.files.get("image") and request.files["image"].filename
    if has_rating and has_pred_label and not has_image:
        return _handle_review_submit()

    try:
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        blood_group = request.form.get("blood_group", "").strip()
        address = request.form.get("address", "").strip()

        if not all([name, email, phone, blood_group, address]):
            return jsonify({"error": "Please fill all fields: Name, Email, Phone, Blood Group, Address."}), 400

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
                "error": f"Model not loaded. Place {MODEL_FILE} in the models/ folder. Path: {MODEL_PATH}"
            }), 503

        prob, predicted_class = result
        prob = float(prob)
        label = "Arsenic detected" if predicted_class == ARSENIC_INFECTED_CLASS else "No arsenic"

        user_data = {
            "name": name,
            "email": email,
            "phone": phone,
            "blood_group": blood_group,
            "address": address,
        }
        auth.save_prediction(user_data, label, prob)

        return jsonify({
            "prediction": prob,
            "label": label,
            "user": user_data,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def _handle_review_submit():
    """Shared logic for review form submission."""
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    try:
        if request.is_json:
            data = request.get_json(silent=True, force=True) or {}
        else:
            data = request.form or {}
        rating = int(data.get("rating") or 0)
        review_text = (data.get("review_text") or "").strip()

        if not 1 <= rating <= 5:
            if is_ajax:
                return jsonify({"error": "Please select a rating from 1 to 5 stars."}), 400
            flash("Please select a rating from 1 to 5 stars.", "error")
            return redirect(url_for("predict"))

        if not session.get("user_email"):
            if is_ajax:
                return jsonify({"error": "Please log in first.", "redirect": url_for("login")}), 401
            flash("Please log in to submit a review.", "error")
            return redirect(url_for("login"))

        auth.save_review(rating=rating, review_text=review_text)
        if is_ajax:
            return jsonify({"success": True, "message": "Thank you for your review!"})
        flash("Thank you for your review!", "success")
        return redirect(url_for("predict"))
    except ValueError as e:
        if is_ajax:
            return jsonify({"error": str(e)}), 400
        flash(str(e), "error")
        return redirect(url_for("predict"))
    except Exception as e:
        app.logger.exception("Review submit failed")
        if is_ajax:
            return jsonify({"error": str(e)}), 500
        flash("Server error. Please try again.", "error")
        return redirect(url_for("predict"))


@app.route("/review", methods=["POST"])
@app.route("/api/review", methods=["POST", "OPTIONS"])
def submit_review():
    """Save review (1-5 stars + optional text) directly to CSV. Form POST redirects; JSON returns JSON."""
    if request.method == "OPTIONS":
        return "", 204
    return _handle_review_submit()


@app.route("/api/status")
def status():
    return jsonify({
        "model_loaded": _load_model() is not None,
        "model_path": str(MODEL_PATH),
        "arsenic_infected_class": ARSENIC_INFECTED_CLASS,
    })


@app.route("/api/model-check")
def model_check():
    """Debug endpoint: path, file exists, load status."""
    exists = MODEL_PATH.is_file()
    model = _load_model()
    return jsonify({
        "path": str(MODEL_PATH),
        "file_exists": exists,
        "model_loaded": model is not None,
        "cwd": str(Path.cwd()),
    })


@app.route("/api/predict-probs", methods=["POST"])
@login_required
def predict_probs():
    model = _load_model()
    if model is None:
        return jsonify({"error": "Model not loaded", "path": str(MODEL_PATH)}), 503
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image"}), 400
        file = request.files["image"]
        if not file or not file.filename:
            return jsonify({"error": "No image"}), 400
        if not allowed_file(file.filename):
            return jsonify({"error": "Use JPEG or PNG"}), 400
        arr = image_to_array(file)
        X = _preprocess_image(arr)
        pred = model.predict(X, verbose=0)[0]
        probs = [float(p) for p in pred]
        # Suggest class swap if infected images give high prob_class_0
        other_class = 1 - ARSENIC_INFECTED_CLASS
        suggestion = None
        if probs[other_class] > probs[ARSENIC_INFECTED_CLASS]:
            suggestion = (
                f"If this image is infected but shows 'No arsenic', add to .env: "
                f"ARSENIC_INFECTED_CLASS={other_class}"
            )
        return jsonify({
            "probabilities": probs,
            "prob_class_0": probs[0],
            "prob_class_1": probs[1],
            "arsenic_infected_class": ARSENIC_INFECTED_CLASS,
            "current_label": "Arsenic detected" if probs[ARSENIC_INFECTED_CLASS] >= 0.5 else "No arsenic",
            "suggestion": suggestion,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ============== CHATBOT ==============
_chatbot = None


def get_chatbot():
    global _chatbot
    if _chatbot is None:
        try:
            import sys
            chatbot_path = BASE_DIR / "arsenic_awareness_chatbot"
            if chatbot_path.exists():
                sys.path.insert(0, str(BASE_DIR))
                from arsenic_awareness_chatbot.core.chatbot import ArsenicChatbot
                _chatbot = ArsenicChatbot()
            else:
                _chatbot = False
        except Exception as e:
            app.logger.warning(f"Chatbot load failed: {e}")
            _chatbot = False
    return _chatbot if _chatbot else None


@app.route("/chatbot")
@login_required
def chatbot_page():
    return render_template("chatbot.html", chatbot_available=get_chatbot() is not None)


@app.route("/chatbot/api/chat", methods=["POST"])
@login_required
def chatbot_api():
    bot = get_chatbot()
    if not bot:
        return jsonify({"error": "Chatbot not available."}), 503
    try:
        data = request.get_json() or {}
        message = (data.get("message") or "").strip()
        session_id = session.get("user_email", "default")
        if not message:
            return jsonify({"error": "Message is required"}), 400
        result = bot.chat(message, session_id=session_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    (BASE_DIR / "models").mkdir(exist_ok=True)
    (BASE_DIR / "data").mkdir(exist_ok=True)
    app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=False)
