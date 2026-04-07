"""
Smoke test: Scryfall API
Verifies fuzzy search, autocomplete, and printings endpoints.

Run with:
    python test_scryfall_api.py
(No credentials needed — Scryfall requires no API key.)
"""

import sys
import time
import requests

BASE_URL = "https://api.scryfall.com"
HEADERS = {"User-Agent": "CardGradingApp/0.1 (smoke-test)"}


def get(path: str, params: dict = None) -> dict:
    time.sleep(0.1)  # respect Scryfall's ~10 req/s rate limit
    response = requests.get(f"{BASE_URL}{path}", params=params, headers=HEADERS, timeout=10)
    response.raise_for_status()
    return response.json()


def test_fuzzy_search() -> bool:
    print("\n--- GET /cards/named?fuzzy=black+lotus ---")
    data = get("/cards/named", {"fuzzy": "black lotus"})

    name = data.get("name")
    set_code = data.get("set")
    image_url = data.get("image_uris", {}).get("normal") or \
                (data.get("card_faces") or [{}])[0].get("image_uris", {}).get("normal")
    price_usd = data.get("prices", {}).get("usd")
    prints_uri = data.get("prints_search_uri")

    print(f"  Name:          {name}")
    print(f"  Set:           {set_code}")
    print(f"  Image URL:     {image_url}")
    print(f"  Price (USD):   {price_usd}")
    print(f"  Prints URI:    {prints_uri}")

    ok = all([name == "Black Lotus", image_url, prints_uri])
    print(f"  Check passed:  {ok}")
    return ok, prints_uri


def test_autocomplete() -> bool:
    print("\n--- GET /cards/autocomplete?q=black+lo ---")
    data = get("/cards/autocomplete", {"q": "black lo"})
    suggestions = data.get("data", [])
    print(f"  Suggestions ({len(suggestions)}): {suggestions[:5]}")
    found = any("Black Lotus" in s for s in suggestions)
    print(f"  'Black Lotus' in suggestions: {found}")
    return found


def test_printings(prints_uri: str) -> bool:
    print(f"\n--- Fetch prints_search_uri ---")
    time.sleep(0.1)
    response = requests.get(prints_uri, headers=HEADERS, timeout=10)
    response.raise_for_status()
    data = response.json()
    cards = data.get("data", [])
    editions = sorted({c.get("set_name", "?") for c in cards})
    print(f"  Total printings: {data.get('total_cards', '?')}")
    print(f"  Editions found: {editions[:8]}")

    has_alpha = any("Alpha" in e for e in editions)
    has_beta  = any("Beta" in e for e in editions)
    has_unl   = any("Unlimited" in e for e in editions)
    print(f"  Alpha: {has_alpha}  Beta: {has_beta}  Unlimited: {has_unl}")
    return has_alpha and has_beta and has_unl


def main():
    results = []

    try:
        ok, prints_uri = test_fuzzy_search()
        results.append(ok)
    except Exception as e:
        print(f"  EXCEPTION: {e}")
        results.append(False)
        prints_uri = None

    try:
        results.append(test_autocomplete())
    except Exception as e:
        print(f"  EXCEPTION: {e}")
        results.append(False)

    if prints_uri:
        try:
            results.append(test_printings(prints_uri))
        except Exception as e:
            print(f"  EXCEPTION: {e}")
            results.append(False)
    else:
        print("\n  SKIP printings test (no prints_uri from fuzzy search)")
        results.append(False)

    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"RESULT: {passed}/{total} checks passed")
    if passed < total:
        print("FAIL — check errors above")
        sys.exit(1)
    else:
        print("PASS — Scryfall API is working correctly")


if __name__ == "__main__":
    main()
