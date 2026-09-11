"""
test_scorer.py
Unit tests for 100-point score calculator and breakdown.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from contracts.match import FeatureBreakdown
from matching.scorer import calculate_match_score


def test_score_calculation():
    features = FeatureBreakdown(
        must_have_coverage=1.0,
        preferred_coverage=1.0,
        experience_fit=1.0,
        role_similarity=1.0,
        semantic_similarity=1.0,
        education_match=1.0,
        project_relevance=1.0,
        domain_match=1.0
    )

    score, breakdown = calculate_match_score(features)
    assert score == 100.0
    assert breakdown.must_have == 30.0
    assert breakdown.experience == 20.0
    assert breakdown.preferred == 15.0
