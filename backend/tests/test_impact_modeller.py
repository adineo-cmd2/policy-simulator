import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services import impact_modeller

BANNED = [
    "corrupt", "stupid", "evil", "disaster", "tyranny", "fascist",
    "communist", "socialist", "radical", "extremist", "woke",
    "elite conspiracy", "steal", "destroy",
]

MAGNITUDES = {"high", "medium", "low", "unknown"}
DIRECTIONS = {"positive", "negative", "mixed"}
CONFIDENCES = {"high", "medium", "speculative"}

POLICY = "Cap annual rent increases at 3% in urban areas."


def _all_text(nodes):
    return " ".join(
        f"{n.get('title', '')} {n.get('detail', '')} {n.get('analogy', '')}"
        for n in nodes
    )


def test_housing_orders_present_with_parent_links():
    nodes = impact_modeller.model(POLICY, "Test City", "housing")
    orders = {n["order"] for n in nodes}
    assert {1, 2, 3} <= orders
    by_idx = {i: n for i, n in enumerate(nodes)}
    for i, n in enumerate(nodes):
        if n["order"] == 1:
            assert n["parent_idx"] is None
        else:
            p = n["parent_idx"]
            assert p is not None and p in by_idx
            assert by_idx[p]["order"] == n["order"] - 1


def test_values_in_fixed_sets_all_domains():
    for domain in [
        "housing", "healthcare", "taxation", "environment",
        "education", "labour", "trade", "general",
    ]:
        nodes = impact_modeller.model(POLICY, "Test City", domain)
        assert len(nodes) >= 3
        for n in nodes:
            assert n["magnitude"] in MAGNITUDES
            assert n["direction"] in DIRECTIONS
            assert n["confidence"] in CONFIDENCES


def test_banned_tokens_absent_all_domains():
    for domain in [
        "housing", "healthcare", "taxation", "environment",
        "education", "labour", "trade", "general",
    ]:
        nodes = impact_modeller.model(POLICY, "Test City", domain)
        text = _all_text(nodes).lower()
        for tok in BANNED:
            assert tok not in text, f"banned token {tok!r} in {domain}"


def test_general_fallback_works():
    nodes = impact_modeller.model(POLICY, "Test City", "nonsense-domain")
    orders = {n["order"] for n in nodes}
    assert {1, 2, 3} <= orders
    text = _all_text(nodes).lower()
    for tok in BANNED:
        assert tok not in text
