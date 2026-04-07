import threading
from difflib import SequenceMatcher
from typing import Dict, List, Optional

import requests

FAB_JSON_URL = (
    "https://raw.githubusercontent.com/the-fab-cube/"
    "flesh-and-blood-cards/main/json/english/card-flattened.json"
)
_THRESHOLD = 0.55  # minimum fuzzy match ratio to include a result

_cache: Optional[List[Dict]] = None
_lock = threading.Lock()


def _get_cards() -> List[Dict]:
    global _cache
    if _cache is None:
        with _lock:
            if _cache is None:
                resp = requests.get(FAB_JSON_URL, timeout=30)
                resp.raise_for_status()
                _cache = resp.json()
    return _cache


def _fuzzy(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _to_candidate(card: Dict, score: float) -> Dict:
    return {
        "name": card.get("name", ""),
        "edition": card.get("edition", ""),
        "foil": card.get("foiling", "") != "",
        "language": card.get("language", "EN"),
        "collector_number": card.get("id", card.get("printing_unique_id", "")),
        "image_url": card.get("image_url", ""),
        "price_usd": None,
        "confidence": round(score, 4),
    }


def search_fab(query: str) -> List[Dict]:
    """Return up to 5 candidate FAB cards matching query, sorted by confidence."""
    cards = _get_cards()
    scored = [
        (_fuzzy(query, c.get("name", "")), c)
        for c in cards
    ]
    scored = [(s, c) for s, c in scored if s >= _THRESHOLD]
    scored.sort(key=lambda x: x[0], reverse=True)
    seen_names = set()
    results = []
    for score, card in scored:
        name = card.get("name", "")
        if name not in seen_names:
            seen_names.add(name)
            results.append(_to_candidate(card, score))
        if len(results) == 5:
            break
    return results
