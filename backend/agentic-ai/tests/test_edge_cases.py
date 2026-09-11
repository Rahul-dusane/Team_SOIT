"""
test_edge_cases.py
Edge-case unit tests covering Java vs JavaScript, low confidence gating, rejection breakdown consistency, and PII tech protection.
"""

import sys, os
import pytest
from pydantic import ValidationError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.matching_config import MatchingConfig
from contracts.candidate import CandidateProfile, CandidateSkill, CandidateExperience
from contracts.job import JobProfile
from matching.rules import classify_skill_match
from matching.pipeline import match_candidate_to_job
from matching.gap_engine import find_skill_gaps
from matching.feature_filter import sanitize_pii_text


def test_contract_validation_errors():
    """Verify that invalid inputs raise Pydantic validation errors."""
    with pytest.raises(ValidationError):
        # Confidence out of bounds (> 1.0)
        CandidateSkill(raw_skill="Python", confidence=7.0)

    with pytest.raises(ValidationError):
        # Invalid mandatory failure policy
        MatchingConfig(mandatory_failure_policy="invalid_policy")


def test_low_confidence_evidence_gating():
    """Verify that low evidence confidence (< 0.70) forces LOW (Needs Review) regardless of high score."""
    cand = CandidateProfile(
        candidate_id="C_LOW_CONF",
        skills=[CandidateSkill(raw_skill="Python", confidence=0.10)]
    )
    job = JobProfile(job_id="J_STD", title="Python Dev", must_have_skills=["Python"])

    res = match_candidate_to_job(cand, job)
    assert res.confidence_level == "LOW (Needs Review)"


def test_rejection_score_breakdown_consistency():
    """Verify that rejected candidate gets overall_score=0.0 and score_breakdown=0.0 while preserving raw_score."""
    cand = CandidateProfile(
        candidate_id="C_REJECT",
        total_experience_months=6,  # Below min 24 mos
        skills=[CandidateSkill(raw_skill="Python")]
    )
    job = JobProfile(job_id="J_EXP", title="Senior Dev", min_experience_months=24, must_have_skills=["Python"])

    res = match_candidate_to_job(cand, job)
    assert res.mandatory_pass is False
    assert res.overall_score == 0.0
    assert res.score_breakdown.must_have == 0.0
    assert res.raw_score_breakdown.must_have > 0.0


def test_related_mandatory_skill_lands_in_critical_gaps():
    """Verify that a mandatory skill matched as 'related' (MySQL vs PostgreSQL) lands in critical gaps."""
    cand = CandidateProfile(
        candidate_id="C_MYSQL",
        skills=[CandidateSkill(raw_skill="MySQL")]
    )
    job = JobProfile(job_id="J_PG", title="DBA", must_have_skills=["PostgreSQL"])

    res = match_candidate_to_job(cand, job)
    assert res.mandatory_pass is False
    assert "PostgreSQL" in res.skill_gaps.critical


def test_pii_tech_protection():
    """Verify that PII filter sanitizes names without stripping protected technical terms."""
    sanitized = sanitize_pii_text("Developed Python web apps for John Smith", name="John Smith")
    assert "John" not in sanitized
    assert "Smith" not in sanitized
    assert "Python" in sanitized  # Tech term preserved!
