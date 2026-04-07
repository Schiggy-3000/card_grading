import pytest
from unittest.mock import patch, MagicMock
from tests.conftest import SAMPLE_FAB_DATA, SAMPLE_FAB_CARD


def test_search_returns_matching_card():
    from fab_lookup import search_fab
    with patch("fab_lookup._get_cards", return_value=SAMPLE_FAB_DATA):
        results = search_fab("Command and Conquer")
    assert len(results) >= 1
    assert results[0]["name"] == "Command and Conquer"


def test_search_returns_empty_for_no_match():
    from fab_lookup import search_fab
    with patch("fab_lookup._get_cards", return_value=SAMPLE_FAB_DATA):
        results = search_fab("zxqwerty nonexistent card name")
    assert results == []


def test_search_fuzzy_matches_partial_name():
    from fab_lookup import search_fab
    with patch("fab_lookup._get_cards", return_value=SAMPLE_FAB_DATA):
        results = search_fab("Command Conquer")  # missing "and"
    assert len(results) >= 1


def test_candidate_schema_is_correct():
    from fab_lookup import search_fab
    with patch("fab_lookup._get_cards", return_value=SAMPLE_FAB_DATA):
        results = search_fab("Command and Conquer")
    c = results[0]
    assert "name" in c
    assert "edition" in c
    assert "foil" in c
    assert "language" in c
    assert "collector_number" in c
    assert "image_url" in c
    assert c["price_usd"] is None  # FAB has no price


def test_results_capped_at_five():
    from fab_lookup import search_fab
    many_cards = [SAMPLE_FAB_CARD.copy() for _ in range(20)]
    with patch("fab_lookup._get_cards", return_value=many_cards):
        results = search_fab("Command and Conquer")
    assert len(results) <= 5
