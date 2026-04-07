"""
Smoke test: OpenCV (opencv-python-headless)
Verifies the core classical CV operations used for card grading work on a real card image.

Run with:
    python test_opencv.py
(No credentials needed.)
"""

import sys
from pathlib import Path
from typing import Optional, Tuple
import cv2
import numpy as np

IMAGES_ROOT = Path(__file__).parent.parent.parent / "images"
TEST_IMAGE = IMAGES_ROOT / "MTG" / "Black_Lotus_Unlimited_Front.jpg"


def test_load_and_grayscale(img_bgr: np.ndarray) -> tuple[bool, np.ndarray]:
    print(f"\n--- Load image and convert to grayscale ---")
    h, w, c = img_bgr.shape
    print(f"  Image shape: {w}x{h} px, {c} channels")

    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    print(f"  Grayscale shape: {gray.shape}")
    return True, gray


def test_card_boundary(img_bgr: np.ndarray) -> Tuple[bool, Optional[tuple]]:
    """Detect card boundary by segmenting the colored background using HSV thresholding."""
    print(f"\n--- Detect card boundary (HSV background segmentation) ---")
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

    # Mask out the background by finding the dominant background color in the corners
    h, w = hsv.shape[:2]
    corner_size = min(h, w) // 10
    corners = [
        hsv[0:corner_size, 0:corner_size],
        hsv[0:corner_size, w-corner_size:w],
        hsv[h-corner_size:h, 0:corner_size],
        hsv[h-corner_size:h, w-corner_size:w],
    ]
    bg_samples = np.vstack([c.reshape(-1, 3) for c in corners])
    bg_hue = int(np.median(bg_samples[:, 0]))
    print(f"  Background hue estimate: {bg_hue} (red~0/180, green~60, blue~120)")

    # Mask pixels close to the background hue
    hue_range = 20
    lower = np.array([max(0, bg_hue - hue_range), 50, 50])
    upper = np.array([min(179, bg_hue + hue_range), 255, 255])
    bg_mask = cv2.inRange(hsv, lower, upper)
    card_mask = cv2.bitwise_not(bg_mask)

    # Find the largest contour in the card mask
    contours, _ = cv2.findContours(card_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        print("  ERROR: No contours found in card mask")
        return False, None

    largest = max(contours, key=cv2.contourArea)
    x, y, bw, bh = cv2.boundingRect(largest)
    area = cv2.contourArea(largest)
    img_area = h * w
    ratio = area / img_area
    print(f"  Card bounding box: x={x}, y={y}, w={bw}, h={bh}")
    print(f"  Card area ratio: {ratio:.2f} (expected >0.3)")
    ok = ratio > 0.3
    print(f"  Plausible card boundary: {ok}")
    return ok, (x, y, bw, bh)


def test_surface_scratch_signal(gray: np.ndarray, bbox: Optional[tuple]) -> bool:
    print(f"\n--- Surface analysis: Laplacian variance ---")
    if bbox:
        x, y, w, h = bbox
        # Crop to inner 60% of the detected card to avoid border/background
        margin_x = int(w * 0.2)
        margin_y = int(h * 0.2)
        roi = gray[y + margin_y: y + h - margin_y, x + margin_x: x + w - margin_x]
    else:
        roi = gray

    if roi.size == 0:
        print("  ERROR: Empty ROI after cropping")
        return False

    laplacian = cv2.Laplacian(roi, cv2.CV_64F)
    variance = laplacian.var()
    print(f"  Laplacian variance: {variance:.2f}")
    print(f"  (Higher = more texture/scratches; lower = smoother surface)")
    return variance > 0


def test_corner_detection(gray: np.ndarray, bbox: Optional[tuple]) -> bool:
    print(f"\n--- Corner region analysis ---")
    if bbox:
        x, y, w, h = bbox
        crop = gray[y:y+h, x:x+w]
    else:
        crop = gray

    corners = cv2.goodFeaturesToTrack(crop, maxCorners=50, qualityLevel=0.01, minDistance=10)
    if corners is None:
        print("  No strong corners detected")
        return False

    count = len(corners)
    print(f"  Strong feature points detected: {count}")

    # Sample the four actual card corners (top-left, top-right, bottom-left, bottom-right)
    h, w = crop.shape
    corner_size = min(h, w) // 6
    regions = {
        "top-left":     crop[0:corner_size, 0:corner_size],
        "top-right":    crop[0:corner_size, w-corner_size:w],
        "bottom-left":  crop[h-corner_size:h, 0:corner_size],
        "bottom-right": crop[h-corner_size:h, w-corner_size:w],
    }
    print(f"  Corner region edge sharpness (Laplacian variance):")
    for name, region in regions.items():
        if region.size > 0:
            sharpness = cv2.Laplacian(region, cv2.CV_64F).var()
            print(f"    {name}: {sharpness:.2f}")

    return count > 0


def main():
    if not TEST_IMAGE.exists():
        print(f"ERROR: Test image not found at {TEST_IMAGE}")
        sys.exit(1)

    print(f"Loading: {TEST_IMAGE}")
    img_bgr = cv2.imread(str(TEST_IMAGE))
    if img_bgr is None:
        print("ERROR: cv2.imread returned None — file may be corrupt or unreadable")
        sys.exit(1)

    results = []

    try:
        ok, gray = test_load_and_grayscale(img_bgr)
        results.append(ok)
    except Exception as e:
        print(f"  EXCEPTION: {e}")
        results.append(False)
        gray = None

    bbox = None
    if gray is not None:
        try:
            ok, bbox = test_card_boundary(img_bgr)
            results.append(ok)
        except Exception as e:
            print(f"  EXCEPTION: {e}")
            results.append(False)

        try:
            results.append(test_surface_scratch_signal(gray, bbox))
        except Exception as e:
            print(f"  EXCEPTION: {e}")
            results.append(False)

        try:
            results.append(test_corner_detection(gray, bbox))
        except Exception as e:
            print(f"  EXCEPTION: {e}")
            results.append(False)

    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"RESULT: {passed}/{total} checks passed")
    if passed < total:
        print("FAIL — check errors above")
        sys.exit(1)
    else:
        print("PASS — OpenCV is installed and all grading algorithms run correctly")


if __name__ == "__main__":
    main()
