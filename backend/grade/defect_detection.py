"""
Classical OpenCV defect detection for card grading.
All scores are on an internal 1.0–10.0 scale.
"""
import base64
from typing import Dict, Tuple

import cv2
import numpy as np


def _decode(image_bytes: bytes) -> np.ndarray:
    arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image")
    return img


def _find_card_bbox(img: np.ndarray) -> Tuple[int, int, int, int]:
    """Segment card from background using HSV hue of corner pixels."""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, w = hsv.shape[:2]
    cs = min(h, w) // 10
    samples = np.vstack([
        hsv[0:cs, 0:cs].reshape(-1, 3),
        hsv[0:cs, w-cs:w].reshape(-1, 3),
        hsv[h-cs:h, 0:cs].reshape(-1, 3),
        hsv[h-cs:h, w-cs:w].reshape(-1, 3),
    ])
    bg_hue = int(np.median(samples[:, 0]))
    hr = 20
    mask = cv2.bitwise_not(cv2.inRange(
        hsv,
        np.array([max(0, bg_hue - hr), 40, 40]),
        np.array([min(179, bg_hue + hr), 255, 255]),
    ))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return 0, 0, w, h
    x, y, bw, bh = cv2.boundingRect(max(contours, key=cv2.contourArea))
    return x, y, bw, bh


def _score_centering(img: np.ndarray, bbox: Tuple) -> Tuple[float, str]:
    """Measure centering by comparing card border widths."""
    x, y, w, h = bbox
    ih, iw = img.shape[:2]
    left = x
    right = iw - (x + w)
    top = y
    bottom = ih - (y + h)

    def ratio_score(a: int, b: int) -> float:
        if a + b == 0:
            return 10.0
        ratio = min(a, b) / max(a, b) if max(a, b) > 0 else 1.0
        # 1.0 ratio → score 10, 0.5 ratio → score ~5
        return round(max(1.0, ratio * 10.0), 1)

    lr = ratio_score(left, right)
    tb = ratio_score(top, bottom)
    score = round((lr + tb) / 2, 1)
    if score >= 9.0:
        reason = "Centering is excellent — margins are nearly equal on all sides."
    elif score >= 7.0:
        reason = f"Centering is good. Left/right offset is minor (L:{left}px R:{right}px)."
    else:
        reason = f"Centering is off. Margins differ significantly (L:{left} R:{right} T:{top} B:{bottom}px)."
    return score, reason


def _score_corners(img: np.ndarray, bbox: Tuple) -> Tuple[float, str]:
    """Analyze sharpness of each corner region."""
    x, y, w, h = bbox
    card = img[y:y+h, x:x+w]
    cs = min(h, w) // 8
    gray = cv2.cvtColor(card, cv2.COLOR_BGR2GRAY)
    regions = {
        "top-left":     gray[0:cs, 0:cs],
        "top-right":    gray[0:cs, w-cs:w],
        "bottom-left":  gray[h-cs:h, 0:cs],
        "bottom-right": gray[h-cs:h, w-cs:w],
    }
    variances = {k: cv2.Laplacian(v, cv2.CV_64F).var() for k, v in regions.items() if v.size > 0}
    if not variances:
        return 5.0, "Could not analyze corners."
    avg_var = np.mean(list(variances.values()))
    # Higher variance = sharper corners = better condition
    # Empirically: very sharp ~5000+, worn ~500-2000, very worn <500
    if avg_var > 4000:
        score, reason = 9.0, "Corners appear sharp with minimal wear."
    elif avg_var > 2000:
        score, reason = 7.5, "Corners show light wear — edges are slightly softened."
    elif avg_var > 800:
        score, reason = 6.0, "Corners show moderate wear."
    else:
        score, reason = 4.0, "Corners show significant wear or rounding."
    return score, reason


def _score_edges(img: np.ndarray, bbox: Tuple) -> Tuple[float, str]:
    """Check card edges for nicks and discontinuities."""
    x, y, w, h = bbox
    card = cv2.cvtColor(img[y:y+h, x:x+w], cv2.COLOR_BGR2GRAY)
    strip = 8  # px strip from each edge
    edges_strips = [
        card[0:strip, :],          # top
        card[h-strip:h, :],        # bottom
        card[:, 0:strip],          # left
        card[:, w-strip:w],        # right
    ]
    variances = [cv2.Laplacian(s, cv2.CV_64F).var() for s in edges_strips if s.size > 0]
    avg_var = np.mean(variances) if variances else 0
    if avg_var < 500:
        score, reason = 9.5, "Edges are clean with no visible nicks or chips."
    elif avg_var < 1500:
        score, reason = 7.5, "Edges show minor irregularities."
    else:
        score, reason = 5.5, "Edges show significant nicks or roughness."
    return score, reason


def _score_surface(img: np.ndarray, bbox: Tuple) -> Tuple[float, str]:
    """Estimate surface scratches using Laplacian variance on central area."""
    x, y, w, h = bbox
    mx, my = int(w * 0.25), int(h * 0.25)
    card = img[y+my:y+h-my, x+mx:x+w-mx]
    if card.size == 0:
        return 5.0, "Could not analyze surface."
    gray = cv2.cvtColor(card, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    if variance > 6000:
        score, reason = 5.0, "Surface shows significant texture — likely scratches or print defects."
    elif variance > 3000:
        score, reason = 7.5, "Surface shows light scratching under close inspection."
    else:
        score, reason = 9.0, "Surface appears clean with minimal scratching."
    return score, reason


def _draw_bbox_b64(img: np.ndarray, bbox: Tuple[int, int, int, int]) -> str:
    """Draw bbox rectangle on image, return as base64 JPEG string."""
    x, y, w, h = bbox
    out = img.copy()
    cv2.rectangle(out, (x, y), (x + w, y + h), (0, 255, 0), 3)
    _, buf = cv2.imencode('.jpg', out, [cv2.IMWRITE_JPEG_QUALITY, 85])
    return base64.b64encode(bytes(buf)).decode()


def _analyze_side(img_bytes: bytes) -> Dict:
    """Analyze one card image side; return subgrades, reasoning, and bbox image."""
    img = _decode(img_bytes)
    bbox = _find_card_bbox(img)
    center_score, center_reason = _score_centering(img, bbox)
    corner_score, corner_reason = _score_corners(img, bbox)
    edge_score, edge_reason = _score_edges(img, bbox)
    surface_score, surface_reason = _score_surface(img, bbox)
    return {
        "subgrades": {
            "centering": center_score,
            "corners":   corner_score,
            "edges":     edge_score,
            "surface":   surface_score,
        },
        "reasoning": {
            "centering": center_reason,
            "corners":   corner_reason,
            "edges":     edge_reason,
            "surface":   surface_reason,
        },
        "bbox_image": _draw_bbox_b64(img, bbox),
    }


def analyze_with_reasoning(
    front_bytes: bytes, back_bytes: bytes
) -> Tuple[Dict, Dict]:
    """Return (front_result, back_result). Each dict has subgrades, reasoning, bbox_image."""
    return _analyze_side(front_bytes), _analyze_side(back_bytes)


def analyze(front_bytes: bytes, back_bytes: bytes) -> Dict[str, float]:
    """Return front subgrades only (backward-compatible convenience function)."""
    front, _ = analyze_with_reasoning(front_bytes, back_bytes)
    return front["subgrades"]
