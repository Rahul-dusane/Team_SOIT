"""
test_ranking.py
Unit tests for candidate ranking engine.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from contracts.match import MatchResult, FeatureBreakdown, ScoreBreakdown, SkillGaps
from matching.ranking import rank_candidates


def test_rank_candidates():
    fb = FeatureBreakdown()
    sb = ScoreBreakdown()
    sg = SkillGaps()

    m1 = MatchResult(candidate_id="C01", job_id="J01", overall_score=85.0, mandatory_pass=True, features=fb, score_breakdown=sb, skill_gaps=sg)
    m2 = MatchResult(candidate_id="C02", job_id="J01", overall_score=92.0, mandatory_pass=True, features=fb, score_breakdown=sb, skill_gaps=sg)
    m3 = MatchResult(candidate_id="C03", job_id="J01", overall_score=95.0, mandatory_pass=False, features=fb, score_breakdown=sb, skill_gaps=sg)

    ranked = rank_candidates([m1, m2, m3])
    # Mandatory pass should rank higher than mandatory fail
    assert ranked[0]["candidate_id"] == "C02"
    assert ranked[1]["candidate_id"] == "C01"
    assert ranked[2]["candidate_id"] == "C03"
