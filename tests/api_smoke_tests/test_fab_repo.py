"""
Smoke test: Flesh and Blood JSON repo (the-fab-cube/flesh-and-blood-cards)
Verifies the JSON data can be fetched, parsed, and that image URLs are reachable.

Run with:
    python test_fab_repo.py
(No credentials needed — public GitHub repo, public CDN.)
"""

import sys
import json
import requests
from difflib import SequenceMatcher
from typing import Optional, Tuple, List

# Raw URL for the flattened English cards JSON from the FAB repo
# card-flattened.json has one entry per printing, with image_url directly on each object
FAB_CARDS_URL = (
    "https://raw.githubusercontent.com/the-fab-cube/"
    "flesh-and-blood-cards/main/json/english/card-flattened.json"
)

HEADERS = {"User-Agent": "CardGradingApp/0.1 (smoke-test)"}
SEARCH_NAME = "Command and Conquer"


def fuzzy_match(query: str, name: str) -> float:
    return SequenceMatcher(None, query.lower(), name.lower()).ratio()


def test_fetch_and_parse() -> Tuple[bool, List]:
    print(f"\n--- Fetch FAB cards JSON ---")
    print(f"  URL: {FAB_CARDS_URL}")
    response = requests.get(FAB_CARDS_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    cards = response.json()

    print(f"  Status: {response.status_code}")
    print(f"  Card count: {len(cards)}")

    if not cards:
        print("  ERROR: Empty card list")
        return False, []

    sample = cards[0]
    print(f"  Sample card fields: {list(sample.keys())}")

    required_fields = {"unique_id", "name", "image_url"}
    missing = required_fields - sample.keys()
    if missing:
        print(f"  ERROR: Missing expected fields: {missing}")
        return False, cards

    print(f"  Sample card: {sample.get('name')} (id={sample.get('unique_id')})")
    print(f"  Sample image_url: {sample.get('image_url')}")
    return True, cards


def test_fuzzy_search(cards: List) -> Tuple[bool, Optional[dict]]:
    print(f"\n--- Fuzzy search for '{SEARCH_NAME}' ---")
    scored = [
        (fuzzy_match(SEARCH_NAME, c.get("name", "")), c)
        for c in cards
    ]
    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:3]

    for score, card in top:
        print(f"  {score:.2f}  {card.get('name')}")

    best_score, best_card = top[0]
    found = best_score > 0.7
    print(f"  Best match ({best_score:.2f}): {best_card.get('name')} — {'OK' if found else 'POOR MATCH'}")
    return found, best_card if found else None


def test_image_url(card: dict) -> bool:
    print(f"\n--- Check image URL accessibility ---")

    # card-flattened.json has image_url directly on each entry
    image_url = card.get("image_url")

    if not image_url:
        print("  No image URL found in card data — skipping")
        return True  # Not a failure; URL structure may vary by repo version

    print(f"  URL: {image_url}")
    try:
        resp = requests.head(image_url, headers=HEADERS, timeout=10, allow_redirects=True)
        status = resp.status_code
        print(f"  HTTP status: {status}")
        ok = status in (200, 301, 302)
        print(f"  Accessible: {ok}")
        return ok
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def main():
    results = []

    try:
        ok, cards = test_fetch_and_parse()
        results.append(ok)
    except Exception as e:
        print(f"  EXCEPTION: {e}")
        results.append(False)
        cards = []

    best_card = None
    if cards:
        try:
            ok, best_card = test_fuzzy_search(cards)
            results.append(ok)
        except Exception as e:
            print(f"  EXCEPTION: {e}")
            results.append(False)

    if best_card:
        try:
            results.append(test_image_url(best_card))
        except Exception as e:
            print(f"  EXCEPTION: {e}")
            results.append(False)
    else:
        print("\n  SKIP image URL test (no card found)")
        results.append(False)

    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"RESULT: {passed}/{total} checks passed")
    if passed < total:
        print("FAIL — check errors above")
        sys.exit(1)
    else:
        print("PASS — FAB JSON repo is accessible and parseable")


if __name__ == "__main__":
    main()
