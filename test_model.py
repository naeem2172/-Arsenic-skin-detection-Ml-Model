"""
Diagnostic script to verify arsenic model class mapping.
Run: python test_model.py [path_to_infected_image] [path_to_not_infected_image]

If you have the dataset, run:
  python test_model.py ArsenicSkinImageBD/Augmented/infected/IMG_1187_augmented_6.png ArsenicSkinImageBD/Augmented/not_infected/IMG_3352_augmented_5.png

Or with a single image:
  python test_model.py path/to/your/image.jpg

The script prints raw probabilities and suggests ARSENIC_INFECTED_CLASS (0 or 1).
"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "arsenic_skin_detection_advanced_model.h5"


def preprocess(path):
    import numpy as np
    from PIL import Image
    img = Image.open(path).convert("RGB").resize((128, 128))
    X = np.array(img, dtype=np.float32) / 255.0
    return np.expand_dims(X, axis=0)


def main():
    if not MODEL_PATH.exists():
        print(f"Model not found: {MODEL_PATH}")
        return 1

    import tensorflow as tf
    model = tf.keras.models.load_model(str(MODEL_PATH))

    images = []
    if len(sys.argv) >= 2:
        for p in sys.argv[1:]:
            path = Path(p)
            if path.exists():
                images.append((str(path), "user", preprocess(path)))
            else:
                print(f"File not found: {path}")
    else:
        # Try dataset paths from notebook
        infected = BASE_DIR / "ArsenicSkinImageBD" / "Augmented" / "infected"
        not_infected = BASE_DIR / "ArsenicSkinImageBD" / "Augmented" / "not_infected"
        for folder, label in [(infected, "infected"), (not_infected, "not_infected")]:
            if folder.exists():
                files = list(folder.glob("*.png"))[:1] or list(folder.glob("*.jpg"))[:1]
                if files:
                    images.append((str(files[0]), label, preprocess(files[0])))

    if not images:
        print("Usage: python test_model.py <infected_image> [not_infected_image]")
        print("Or place dataset in ArsenicSkinImageBD/Augmented/ and run without args.")
        return 1

    print("=" * 60)
    print("Arsenic Model Diagnostic")
    print("=" * 60)

    for path, expected_label, X in images:
        pred = model.predict(X, verbose=0)[0]
        p0, p1 = float(pred[0]), float(pred[1])
        argmax = 0 if p0 >= p1 else 1
        print(f"\nImage: {path}")
        print(f"  Expected (from path): {expected_label}")
        print(f"  prob_class_0: {p0:.4f}  prob_class_1: {p1:.4f}")
        print(f"  argmax -> class {argmax}")
        if expected_label == "infected":
            if p1 > p0:
                print(f"  -> Correct: class 1 = infected. Use ARSENIC_INFECTED_CLASS=1 (default)")
            else:
                print(f"  -> INVERTED: class 0 = infected. Add to .env: ARSENIC_INFECTED_CLASS=0")
        elif expected_label == "not_infected":
            if p0 > p1:
                print(f"  -> Correct: class 0 = not_infected. Use ARSENIC_INFECTED_CLASS=1 (default)")
            else:
                print(f"  -> INVERTED: class 1 = not_infected. Add to .env: ARSENIC_INFECTED_CLASS=0")

    print("\n" + "=" * 60)
    print("If infected images give HIGH prob_class_0, add to .env:")
    print("  ARSENIC_INFECTED_CLASS=0")
    print("Then restart the app.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
