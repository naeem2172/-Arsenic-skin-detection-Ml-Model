"""User authentication with CSV storage."""
import csv
from pathlib import Path
from typing import Tuple

BASE_DIR = Path(__file__).resolve().parent
USERS_CSV = BASE_DIR / "data" / "users.csv"
PREDICTIONS_CSV = BASE_DIR / "data" / "predictions.csv"
REVIEWS_CSV = BASE_DIR / "data" / "reviews.csv"


def _ensure_data_dir():
    (BASE_DIR / "data").mkdir(parents=True, exist_ok=True)


def _init_users_csv():
    if not USERS_CSV.exists():
        _ensure_data_dir()
        with open(USERS_CSV, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["email", "password", "name"])


def _init_predictions_csv():
    if not PREDICTIONS_CSV.exists():
        _ensure_data_dir()
        with open(PREDICTIONS_CSV, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["timestamp", "name", "email", "phone", "blood_group", "address", "label", "probability"])


def register_user(email: str, password: str, name: str = "") -> Tuple[bool, str]:
    """Register a new user. Returns (success, message)."""
    _init_users_csv()
    email = (email or "").strip().lower()
    if not email:
        return False, "Email is required."
    if not password or len(password) < 4:
        return False, "Password must be at least 4 characters."

    with open(USERS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("email", "").lower() == email:
                return False, "Email already registered."

    with open(USERS_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([email, password, (name or "").strip()])
    return True, "Registration successful. Please log in."


def verify_user(email: str, password: str) -> Tuple[bool, str]:
    """Verify login. Returns (success, message)."""
    _init_users_csv()
    email = (email or "").strip().lower()
    if not email or not password:
        return False, "Email and password are required."

    with open(USERS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("email", "").lower() == email and row.get("password") == password:
                return True, "Login successful."
    return False, "Invalid email or password."


REVIEWS_HEADER = ["timestamp", "rating", "review_text"]


def _init_reviews_csv():
    """Ensure reviews CSV exists with correct format (timestamp, rating, review_text only)."""
    _ensure_data_dir()
    if not REVIEWS_CSV.exists():
        with open(REVIEWS_CSV, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(REVIEWS_HEADER)
    else:
        # Migrate old format: if header has extra columns, rewrite with new format
        with open(REVIEWS_CSV, "r", encoding="utf-8") as f:
            first = f.readline().strip()
        if first and first != ",".join(REVIEWS_HEADER):
            rows = []
            with open(REVIEWS_CSV, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    ts = r.get("timestamp", "")
                    rows.append((ts, r.get("rating", ""), r.get("review_text", "")))
            with open(REVIEWS_CSV, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(REVIEWS_HEADER)
                for ts, rating, text in rows:
                    w.writerow([ts, rating, text])


def save_review(rating: int, review_text: str = "") -> None:
    """Save review (rating 1-5 and optional text) to CSV. Only rating and review_text stored."""
    _init_reviews_csv()
    from datetime import datetime
    rating = max(1, min(5, int(rating)))
    row = [
        datetime.now().isoformat(),
        str(rating),
        (review_text or "").strip()[:2000],
    ]
    with open(REVIEWS_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(row)
        f.flush()


def save_prediction(user_data: dict, label: str, probability: float) -> None:
    """Save prediction result with user details to CSV."""
    _init_predictions_csv()
    from datetime import datetime
    row = [
        datetime.now().isoformat(),
        user_data.get("name", ""),
        user_data.get("email", ""),
        user_data.get("phone", ""),
        user_data.get("blood_group", ""),
        user_data.get("address", ""),
        label,
        str(probability),
    ]
    with open(PREDICTIONS_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(row)
