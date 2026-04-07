"""
Smoke test: Google Cloud Vision API
Verifies OCR and image properties on real card photos.

Run with:
    export GOOGLE_APPLICATION_CREDENTIALS="../../.credentials/card-grading-492013-2de49a09ec20.json"
    python test_vision_api.py
"""

import os
import sys
from pathlib import Path
from difflib import SequenceMatcher
from google.cloud import vision

IMAGES_ROOT = Path(__file__).parent.parent.parent / "images"

TEST_IMAGES = {
    "MTG Unlimited (front)": IMAGES_ROOT / "MTG" / "Black_Lotus_Unlimited_Front.jpg",
    "MTG Alpha (front)":     IMAGES_ROOT / "MTG" / "Black_Lotus_Alpha_Front.jpg",
    "MTG Beta (front)":      IMAGES_ROOT / "MTG" / "Black_Lotus_Beta_Front.jpg",
    "FAB Command and Conquer (front)": IMAGES_ROOT / "FAB" / "Command_and_Conquer_The_Hunted_Extended_Art_Rainbow_Foil_Front.png",
}


def load_image_bytes(path: Path) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def test_ocr(client: vision.ImageAnnotatorClient, label: str, path: Path) -> bool:
    print(f"\n--- TEXT_DETECTION: {label} ---")
    image = vision.Image(content=load_image_bytes(path))
    response = client.text_detection(image=image)

    if response.error.message:
        print(f"  ERROR: {response.error.message}")
        return False

    texts = response.text_annotations
    if not texts:
        print("  No text detected.")
        return False

    full_text = texts[0].description.strip()
    print(f"  Extracted text:\n    {repr(full_text[:200])}")

    # Exact match (works for either card)
    exact = "black lotus" in full_text.lower() or "command and conquer" in full_text.lower()
    # Fuzzy match on first line — OCR may misread characters on aged cards (e.g. "Lorus" for "Lotus")
    first_line = full_text.split("\n")[0].lower()
    expected = "command and conquer" if "fab" in label.lower() else "black lotus"
    similarity = SequenceMatcher(None, first_line, expected).ratio()
    fuzzy = similarity >= 0.75
    print(f"  Exact match: {exact}  |  Fuzzy match ({similarity:.2f} vs '{expected}'): {fuzzy}")
    # Pass if either exact or fuzzy matches — real OCR noise is expected on aged cards
    return exact or fuzzy


def test_image_properties(client: vision.ImageAnnotatorClient, path: Path) -> bool:
    print(f"\n--- IMAGE_PROPERTIES: Unlimited (front) ---")
    image = vision.Image(content=load_image_bytes(path))
    response = client.image_properties(image=image)

    if response.error.message:
        print(f"  ERROR: {response.error.message}")
        return False

    props = response.image_properties_annotation
    colors = props.dominant_colors.colors
    print(f"  Top dominant colors (RGB, score, pixel_fraction):")
    for c in colors[:5]:
        r, g, b = int(c.color.red), int(c.color.green), int(c.color.blue)
        print(f"    RGB({r:3d}, {g:3d}, {b:3d})  score={c.score:.3f}  fraction={c.pixel_fraction:.3f}")
    return len(colors) > 0


def main():
    creds_env = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_env:
        print("ERROR: GOOGLE_APPLICATION_CREDENTIALS is not set.")
        print("  Run: export GOOGLE_APPLICATION_CREDENTIALS=../../.credentials/card-grading-492013-2de49a09ec20.json")
        sys.exit(1)
    print(f"Using credentials: {creds_env}")

    client = vision.ImageAnnotatorClient()
    print("Vision API client created successfully.")

    results = []

    # OCR on all three editions
    for label, path in TEST_IMAGES.items():
        if not path.exists():
            print(f"  SKIP: {path} not found")
            results.append(False)
            continue
        results.append(test_ocr(client, label, path))

    # Image properties on Unlimited front
    unlimited_path = TEST_IMAGES["MTG Unlimited (front)"]
    if unlimited_path.exists():
        results.append(test_image_properties(client, unlimited_path))

    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"RESULT: {passed}/{total} checks passed")
    if passed < total:
        print("FAIL — check errors above")
        sys.exit(1)
    else:
        print("PASS — Vision API is working correctly")


if __name__ == "__main__":
    main()
