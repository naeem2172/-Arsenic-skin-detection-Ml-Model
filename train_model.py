"""
Train the arsenic skin detection model and save to models/arsenic_skin_detection_advanced_model.h5
Run this script if the model is missing. Requires ~3.5GB dataset download from Google Drive.
"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
MODEL_PATH = MODELS_DIR / "arsenic_skin_detection_advanced_model.h5"
DATASET_ZIP = BASE_DIR / "ArsenicSkinImageBD.zip"
DATASET_DIR = BASE_DIR / "ArsenicSkinImageBD"
GOOGLE_DRIVE_ID = "1TT-Z1Y9ZLUheDwla31PvLlKeLDT8rJqT"


def create_placeholder_model():
    """
    Create a minimal ResNet50-based model with random weights.
    Use this when you don't have the dataset - predictions will be approximate.
    """
    print("Creating placeholder model (no training data required)...")
    try:
        import tensorflow as tf
        from tensorflow.keras.applications import ResNet50
        from tensorflow.keras.models import Model
        from tensorflow.keras import layers

        convolutional_base = ResNet50(
            weights="imagenet",
            include_top=False,
            input_shape=(128, 128, 3),
        )
        convolutional_base.trainable = False

        x = convolutional_base.output
        x = layers.Flatten()(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dense(128, activation="relu")(x)
        x = layers.Dropout(0.5)(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dense(64, activation="relu")(x)
        x = layers.Dropout(0.5)(x)
        x = layers.BatchNormalization()(x)
        predictions = layers.Dense(2, activation="softmax")(x)

        model = Model(inputs=convolutional_base.input, outputs=predictions)
        model.compile(
            optimizer="adam",
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"],
        )

        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        model.save(str(MODEL_PATH), save_format="h5")
        print(f"Placeholder model saved to {MODEL_PATH}")
        print("Note: This model has random classifier weights. Run full training for real predictions.")
        return True
    except Exception as e:
        print(f"Error creating placeholder model: {e}")
        return False


def download_dataset():
    """Download dataset from Google Drive using gdown."""
    if DATASET_ZIP.exists():
        print(f"Dataset already exists: {DATASET_ZIP}")
        return True
    try:
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "gdown"], check=True)
        import gdown
        print("Downloading dataset (~3.5GB) from Google Drive...")
        gdown.download(id=GOOGLE_DRIVE_ID, output=str(DATASET_ZIP), quiet=False)
        return DATASET_ZIP.exists()
    except Exception as e:
        print(f"Download failed: {e}")
        return False


def extract_dataset():
    """Extract the dataset zip."""
    if DATASET_DIR.exists() and (DATASET_DIR / "Augmented").exists():
        print("Dataset already extracted.")
        return True
    if not DATASET_ZIP.exists():
        return False
    import zipfile
    print("Extracting dataset...")
    with zipfile.ZipFile(DATASET_ZIP, "r") as z:
        z.extractall(BASE_DIR)
    return (DATASET_DIR / "Augmented" / "infected").exists()


def load_data():
    """Load and preprocess images (matches notebook pipeline)."""
    import numpy as np
    from PIL import Image

    infected_path = DATASET_DIR / "Augmented" / "infected"
    not_infected_path = DATASET_DIR / "Augmented" / "not_infected"

    if not infected_path.exists() or not not_infected_path.exists():
        return None, None

    data = []
    labels = []

    for img_file in os.listdir(infected_path):
        if img_file.lower().endswith((".png", ".jpg", ".jpeg")):
            img = Image.open(infected_path / img_file).convert("RGB")
            img = img.resize((128, 128), Image.LANCZOS)
            data.append(np.array(img))
            labels.append(1)

    for img_file in os.listdir(not_infected_path):
        if img_file.lower().endswith((".png", ".jpg", ".jpeg")):
            img = Image.open(not_infected_path / img_file).convert("RGB")
            img = img.resize((128, 128), Image.LANCZOS)
            data.append(np.array(img))
            labels.append(0)

    X = np.array(data) / 255.0
    y = np.array(labels)
    return X, y


def train_full_model():
    """Train the full model with the dataset."""
    import tensorflow as tf
    import numpy as np
    from sklearn.model_selection import train_test_split
    from tensorflow.keras.applications import ResNet50
    from tensorflow.keras.models import Model
    from tensorflow.keras import layers

    print("Loading data...")
    X, y = load_data()
    if X is None:
        return False

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("Building ResNet50 model...")
    convolutional_base = ResNet50(
        weights="imagenet",
        include_top=False,
        input_shape=(128, 128, 3),
    )
    convolutional_base.trainable = False

    x = convolutional_base.output
    x = layers.Flatten()(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dense(128, activation="relu")(x)
    x = layers.Dropout(0.5)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dense(64, activation="relu")(x)
    x = layers.Dropout(0.5)(x)
    x = layers.BatchNormalization()(x)
    predictions = layers.Dense(2, activation="softmax")(x)

    model = Model(inputs=convolutional_base.input, outputs=predictions)
    model.compile(
        optimizer=tf.keras.optimizers.RMSprop(learning_rate=2e-5),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    print("Training (this may take 15-30 minutes)...")
    model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=5,
        batch_size=32,
        verbose=1,
    )

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model.save(str(MODEL_PATH), save_format="h5")
    print(f"Model saved to {MODEL_PATH}")
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Train arsenic skin detection model")
    parser.add_argument(
        "--placeholder",
        action="store_true",
        help="Create placeholder model without training (no dataset needed)",
    )
    args = parser.parse_args()

    if args.placeholder:
        return 0 if create_placeholder_model() else 1

    if MODEL_PATH.exists():
        print(f"Model already exists at {MODEL_PATH}")
        print("Delete it first to retrain, or use --placeholder to create a minimal model.")
        return 0

    if not download_dataset():
        print("\nDataset download failed. Use --placeholder to create a minimal model instead:")
        print("  python train_model.py --placeholder")
        return 1

    if not extract_dataset():
        print("Dataset extraction failed.")
        return 1

    return 0 if train_full_model() else 1


if __name__ == "__main__":
    sys.exit(main())
