"""
test_edge_cases.py
Edge-case unit tests covering Java vs JavaScript, empty skills, zero experience, missing requirements.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from contracts.candidate import CandidateProfile, CandidateSkill
from contracts.job import JobProfile
from matching.rules import classify_skill_match
from matching.pipeline import match_candidate_to_job


def test_java_vs_javascript_edge_case():
    """Verify that Java is NOT matched to JavaScript as equivalent."""
    cand_skills = [CandidateSkill(raw_skill="JavaScript")]
    match_detail = classify_skill_match("Java", cand_skills)
    assert match_detail.match_type == "missing"
    assert match_detail.score == 0.0


def test_alias_edge_cases():
    cand_skills = [
        CandidateSkill(raw_skill="Postgres"),
        CandidateSkill(raw_skill="k8s"),
        CandidateSkill(raw_skill="Azure")
    ]

    m_postgres = classify_skill_match("PostgreSQL", cand_skills)
    assert m_postgres.match_type == "exact" or m_postgres.match_type == "equivalent"

    m_k8s = classify_skill_match("Kubernetes", cand_skills)
    assert m_k8s.match_type == "exact" or m_k8s.match_type == "equivalent"

    m_aws = classify_skill_match("AWS", cand_skills)
    assert m_aws.match_type == "transferable"


def test_empty_candidate_skills():
    cand = CandidateProfile(candidate_id="C_EMPTY", total_experience_months=0, skills=[])
    job = JobProfile(job_id="J_STD", title="Dev", must_have_skills=["Python"])

    res = match_candidate_to_job(cand, job)
    assert res.mandatory_pass is False
    assert res.features.must_have_coverage == 0.0
