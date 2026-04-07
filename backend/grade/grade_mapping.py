from typing import Dict, Optional, Union

# CGC grade labels indexed by grade value (half-point steps)
CGC_LABELS = {
    10.0: "Pristine",
    9.8: "Gem Mint",
    9.6: "Mint+",
    9.4: "Mint",
    9.2: "Near Mint/Mint+",
    9.0: "Near Mint/Mint",
    8.5: "Near Mint+",
    8.0: "Near Mint",
    7.5: "Very Fine/Near Mint",
    7.0: "Very Fine+",
    6.5: "Very Fine",
    6.0: "Fine/Very Fine",
    5.5: "Fine+",
    5.0: "Fine",
    4.5: "Very Good/Fine",
    4.0: "Very Good+",
    3.5: "Very Good",
    3.0: "Good/Very Good",
    2.5: "Good+",
    2.0: "Good",
    1.5: "Fair",
    1.0: "Poor",
}


def _internal_average(subgrades: Dict[str, float]) -> float:
    """Weighted average of sub-grades. Corners and surface weighted slightly higher."""
    weights = {"centering": 1.0, "corners": 1.2, "edges": 1.0, "surface": 1.2}
    total_w = sum(weights[k] for k in subgrades if k in weights)
    weighted = sum(subgrades[k] * weights[k] for k in subgrades if k in weights)
    return weighted / total_w if total_w > 0 else 5.0


def _round_half(value: float) -> float:
    return round(value * 2) / 2


def _round_tenth(value: float) -> float:
    return round(value, 1)


def map_to_standard(
    subgrades: Dict[str, float], standard: str
) -> Dict[str, Union[str, int, float, None, Dict]]:
    avg = _internal_average(subgrades)
    label: Optional[str] = None

    if standard == "psa":
        overall: Union[int, float] = max(1, min(10, round(avg)))
    elif standard == "bgs":
        overall = max(1.0, min(10.0, _round_half(avg)))
    elif standard == "cgc":
        raw = max(1.0, min(10.0, _round_half(avg)))
        # Find nearest CGC label
        nearest = min(CGC_LABELS.keys(), key=lambda g: abs(g - raw))
        overall = nearest
        label = CGC_LABELS[nearest]
    elif standard == "tag":
        overall = max(1.0, min(10.0, _round_tenth(avg)))
    else:
        raise ValueError(f"Unknown grading standard: {standard}")

    return {
        "standard": standard,
        "overall": overall,
        "label": label,
        "subgrades": subgrades,
    }
