import pytest
from tests.conftest import mtg_front_bytes, mtg_back_bytes, fab_front_bytes


def test_analyze_returns_all_four_dimensions(mtg_front_bytes, mtg_back_bytes):
    from defect_detection import analyze
    result = analyze(mtg_front_bytes, mtg_back_bytes)
    assert "centering" in result
    assert "corners" in result
    assert "edges" in result
    assert "surface" in result


def test_scores_are_floats_in_1_to_10_range(mtg_front_bytes, mtg_back_bytes):
    from defect_detection import analyze
    result = analyze(mtg_front_bytes, mtg_back_bytes)
    for key, score in result.items():
        assert isinstance(score, float), f"{key} score is not a float"
        assert 1.0 <= score <= 10.0, f"{key} score {score} out of range"


def test_reasoning_returned_for_each_dimension(mtg_front_bytes, mtg_back_bytes):
    from defect_detection import analyze_with_reasoning
    scores, reasoning = analyze_with_reasoning(mtg_front_bytes, mtg_back_bytes)
    for dim in ("centering", "corners", "edges", "surface"):
        assert dim in reasoning
        assert isinstance(reasoning[dim], str)
        assert len(reasoning[dim]) > 0


def test_fab_card_also_works(fab_front_bytes, mtg_back_bytes):
    from defect_detection import analyze
    result = analyze(fab_front_bytes, mtg_back_bytes)
    assert all(1.0 <= v <= 10.0 for v in result.values())
