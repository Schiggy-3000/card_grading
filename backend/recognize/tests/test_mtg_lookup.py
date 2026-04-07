import pytest
from unittest.mock import patch, MagicMock

SCRYFALL_NAMED_RESPONSE = {
    "name": "Black Lotus",
    "set": "lea",
    "set_name": "Limited Edition Alpha",
    "collector_number": "232",
    "finishes": ["nonfoil"],
    "lang": "en",
    "image_uris": {"normal": "https://cards.scryfall.io/normal/front/b/d/bd8fa327.jpg"},
    "prices": {"usd": "9999.99", "usd_foil": None},
    "prints_search_uri": "https://api.scryfall.com/cards/search?q=oracleid%3Aabc",
}

SCRYFALL_PRINTS_RESPONSE = {
    "data": [
        {
            "name": "Black Lotus",
            "set": "lea",
            "set_name": "Limited Edition Alpha",
            "collector_number": "232",
            "finishes": ["nonfoil"],
            "lang": "en",
            "image_uris": {"normal": "https://cards.scryfall.io/normal/front/alpha.jpg"},
            "prices": {"usd": "9999.99", "usd_foil": None},
        },
        {
            "name": "Black Lotus",
            "set": "leb",
            "set_name": "Limited Edition Beta",
            "collector_number": "232",
            "finishes": ["nonfoil"],
            "lang": "en",
            "image_uris": {"normal": "https://cards.scryfall.io/normal/front/beta.jpg"},
            "prices": {"usd": "3000.00", "usd_foil": None},
        },
    ],
    "has_more": False,
}

SCRYFALL_AUTOCOMPLETE_RESPONSE = {
    "data": ["Black Lotus", "Black Lotus (Oversized)"],
}


def _mock_get(url, **kwargs):
    resp = MagicMock()
    resp.raise_for_status = MagicMock()
    if "named" in url:
        resp.json.return_value = SCRYFALL_NAMED_RESPONSE
    elif "autocomplete" in url:
        resp.json.return_value = SCRYFALL_AUTOCOMPLETE_RESPONSE
    else:
        resp.json.return_value = SCRYFALL_PRINTS_RESPONSE
    return resp


def test_search_by_name_returns_candidates():
    from mtg_lookup import search_mtg
    with patch("mtg_lookup.requests.get", side_effect=_mock_get):
        results = search_mtg("Black Lotus")
    assert len(results) >= 1
    assert results[0]["name"] == "Black Lotus"


def test_candidate_schema_is_correct():
    from mtg_lookup import search_mtg
    with patch("mtg_lookup.requests.get", side_effect=_mock_get):
        results = search_mtg("Black Lotus")
    c = results[0]
    assert "name" in c
    assert "edition" in c
    assert "foil" in c
    assert "language" in c
    assert "collector_number" in c
    assert "image_url" in c
    assert "price_usd" in c
    assert "confidence" in c


def test_price_usd_is_float_or_none():
    from mtg_lookup import search_mtg
    with patch("mtg_lookup.requests.get", side_effect=_mock_get):
        results = search_mtg("Black Lotus")
    for r in results:
        assert r["price_usd"] is None or isinstance(r["price_usd"], float)


def test_results_capped_at_five():
    from mtg_lookup import search_mtg
    many_prints = {"data": [SCRYFALL_PRINTS_RESPONSE["data"][0]] * 20, "has_more": False}
    def mock_get(url, **kwargs):
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        resp.json.return_value = SCRYFALL_NAMED_RESPONSE if "named" in url else many_prints
        return resp
    with patch("mtg_lookup.requests.get", side_effect=mock_get):
        results = search_mtg("Black Lotus")
    assert len(results) <= 5


def test_zero_results_when_not_found():
    from mtg_lookup import search_mtg
    resp_404 = MagicMock()
    resp_404.raise_for_status.side_effect = Exception("404 Not Found")
    with patch("mtg_lookup.requests.get", return_value=resp_404):
        results = search_mtg("xyznonexistentcard")
    assert results == []
