import time
from typing import Dict, List, Optional

import requests

SCRYFALL_BASE = "https://api.scryfall.com"
_HEADERS = {"User-Agent": "CardGradingApp/1.0"}


def _get(path: str, params: Optional[Dict] = None) -> Dict:
    time.sleep(0.1)  # respect Scryfall rate limit
    resp = requests.get(f"{SCRYFALL_BASE}{path}", params=params,
                        headers=_HEADERS, timeout=10)
    resp.raise_for_status()
    return resp.json()


def _image_url(card: Dict) -> str:
    uris = card.get("image_uris") or {}
    if not uris and card.get("card_faces"):
        uris = card["card_faces"][0].get("image_uris", {})
    return uris.get("normal", "")


def _price(card: Dict) -> Optional[float]:
    prices = card.get("prices", {})
    raw = prices.get("usd") or prices.get("usd_foil")
    return float(raw) if raw else None


def _to_candidate(card: Dict, confidence: float) -> Dict:
    finishes = card.get("finishes", [])
    return {
        "name": card.get("name", ""),
        "edition": card.get("set_name", card.get("set", "")),
        "foil": "foil" in finishes and "nonfoil" not in finishes,
        "language": card.get("lang", "en").upper(),
        "collector_number": card.get("collector_number", ""),
        "image_url": _image_url(card),
        "price_usd": _price(card),
        "confidence": round(confidence, 4),
    }


def search_mtg(query: str, confidence: float = 1.0) -> List[Dict]:
    """Fuzzy search MTG cards by name. Returns up to 5 candidates."""
    try:
        named = _get("/cards/named", {"fuzzy": query})
    except Exception:
        return []

    try:
        prints_url = named.get("prints_search_uri", "")
        if prints_url:
            time.sleep(0.1)
            resp = requests.get(prints_url, headers=_HEADERS, timeout=10)
            resp.raise_for_status()
            prints_data = resp.json().get("data", [])
        else:
            prints_data = [named]
    except Exception:
        prints_data = [named]

    return [_to_candidate(c, confidence) for c in prints_data[:5]]
