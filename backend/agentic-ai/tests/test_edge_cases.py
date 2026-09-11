"""
test_edge_cases.py
Edge-case unit tests covering Java vs JavaScript word boundary, contradiction detection,
unmapped extra fields, requirement duration enforcement, and breakdown consistency.
"""

import sys, os
import pytest
from pydantic import ValidationError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.matching_config import MatchingConfig
from contracts.candidate import CandidateProfile, CandidateSkill, CandidateExperience
from contracts.job import JobProfile, JobRequirement
from matching.rules import classify_skill_match
from matching.pipeline import match_candidate_to_job
from nlp.evidence_retriever import retrieve_candidate_evidence
from matching.feature_filter import sanitize_pii_text


def test_contract_validation_errors():
    """Verify that invalid inputs raise Pydantic validation errors."""
    with pytest.raises(ValidationError):
        CandidateSkill(raw_skill="Python", confidence=7.0)

    with pytest.raises(ValidationError):
        MatchingConfig(mandatory_failure_policy="invalid_policy")


def test_unsupported_extra_fields_captured():
    """Verify that extra/unsupported fields (like professional_license) are captured into unmapped_fields."""
    data = {
        "candidate_id": "C_EXTRA",
        "name": "Jane Doe",
        "skills": [{"raw_skill": "Bookkeeping"}],
        "professional_license": "CPA License #12345",
        "years_in_field": 10
    }
    cand = CandidateProfile(**data)
    assert "professional_license" in cand.unmapped_fields
    assert cand.unmapped_fields["professional_license"] == "CPA License #12345"


def test_contradiction_detection():
    """Verify that negative statements ('I have no payroll experience') return status 'contradicted'."""
    cand = CandidateProfile(
        candidate_id="C_NEG",
        experiences=[CandidateExperience(role="Accountant", description="Handled general ledger but I have no payroll experience")]
    )
    status, passage, page, conf = retrieve_candidate_evidence("Payroll management", cand, req_skill="payroll")
    assert status == "contradicted"


def test_word_boundary_java_vs_javascript():
    """Verify that requirement 'Java' does NOT match candidate text containing 'JavaScript'."""
    cand = CandidateProfile(
        candidate_id="C_JS",
        skills=[CandidateSkill(raw_skill="JavaScript")]
    )
    status, passage, page, conf = retrieve_candidate_evidence("Java programming", cand, req_skill="Java")
    assert status != "satisfied"


def test_requirement_only_description_no_crash():
    """Verify that JobRequirement(description='Manage financial close') runs without NoneType lower crash."""
    job = JobProfile(
        job_id="J_FIN",
        title="Financial Analyst",
        requirements=[JobRequirement(description="Manage financial close", importance="must_have", weight=20.0)]
    )
    cand = CandidateProfile(
        candidate_id="C_FIN",
        skills=[CandidateSkill(raw_skill="Financial Close")]
    )
    res = match_candidate_to_job(cand, job)
    assert res.candidate_id == "C_FIN"
    assert res.raw_score > 0.0


def test_duration_requirement_enforced():
    """Verify that requirement-specific duration (e.g. 24 mos) yields partially_supported if candidate has less."""
    cand = CandidateProfile(
        candidate_id="C_DUR",
        experiences=[CandidateExperience(role="Accountant", duration_months=12, description="Managed bookkeeping and financial close")]
    )
    status, passage, page, conf = retrieve_candidate_evidence(
        requirement_text="Bookkeeping",
        candidate=cand,
        req_skill="Bookkeeping",
        min_duration_months=24
    )
    assert status == "partially_supported"


def test_rejection_score_breakdown_consistency():
    """Verify that rejected candidate gets overall_score=0.0 and score_breakdown=0.0 while preserving raw_score."""
    cand = CandidateProfile(
        candidate_id="C_REJECT",
        total_experience_months=6,
        skills=[CandidateSkill(raw_skill="Python")]
    )
    job = JobProfile(job_id="J_EXP", title="Senior Dev", min_experience_months=24, must_have_skills=["Python"])

    res = match_candidate_to_job(cand, job)
    assert res.mandatory_pass is False
    assert res.overall_score == 0.0
    assert res.score_breakdown.must_have == 0.0
    assert res.raw_score_breakdown.must_have > 0.0


def test_pii_tech_protection():
    """Verify that PII filter sanitizes names without stripping protected technical terms."""
    sanitized = sanitize_pii_text("Developed Python web apps for John Smith", name="John Smith")
    assert "John" not in sanitized
    assert "Smith" not in sanitized
    assert "Python" in sanitized
