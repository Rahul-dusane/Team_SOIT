"""
test_rules.py
Unit tests for 5-tier classification, experience ratio, and mandatory constraints.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from contracts.candidate import CandidateProfile, CandidateSkill
from contracts.job import JobProfile
from matching.rules import classify_skill_match, calculate_experience_fit, check_mandatory_requirements


def test_classify_skill_match_hierarchy():
    cand_skills = [
        CandidateSkill(raw_skill="Azure", normalized_skill="Azure"),
        CandidateSkill(raw_skill="Postgres", normalized_skill="PostgreSQL")
    ]

    match_aws = classify_skill_match("AWS", cand_skills)
    assert match_aws.match_type == "transferable"

    match_postgres = classify_skill_match("PostgreSQL", cand_skills)
    assert match_postgres.match_type == "exact"


def test_mandatory_constraints():
    job = JobProfile(
        job_id="J01",
        title="Senior Backend Engineer",
        min_experience_months=48,
        must_have_skills=["Python", "PostgreSQL"]
    )

    cand_pass = CandidateProfile(
        candidate_id="C01",
        total_experience_months=60,
        skills=[CandidateSkill(raw_skill="Python"), CandidateSkill(raw_skill="PostgreSQL")]
    )
    passed, failed = check_mandatory_requirements(cand_pass, job)
    assert passed is True
    assert len(failed) == 0

    cand_fail = CandidateProfile(
        candidate_id="C02",
        total_experience_months=24,
        skills=[CandidateSkill(raw_skill="Python")]
    )
    passed_f, failed_f = check_mandatory_requirements(cand_fail, job)
    assert passed_f is False
    assert len(failed_f) == 2  # Failed experience AND missing PostgreSQL
