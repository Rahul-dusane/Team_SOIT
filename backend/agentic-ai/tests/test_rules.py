"""
test_rules.py
Unit tests for 5-tier classification hierarchy, experience ratio, weighted skill coverage, and mandatory constraints.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from contracts.candidate import CandidateProfile, CandidateSkill
from contracts.job import JobProfile, JobRequirement
from matching.rules import classify_skill_match, calculate_skill_coverage, check_mandatory_requirements


def test_classify_skill_match_hierarchy():
    cand_skills = [
        CandidateSkill(raw_skill="Azure", normalized_skill="Azure"),
        CandidateSkill(raw_skill="Postgres", normalized_skill="PostgreSQL"),
        CandidateSkill(raw_skill="JavaScript", normalized_skill="JavaScript")
    ]

    # Known transferable locked to transferable (0.7 multiplier), not promoted to equivalent by embeddings
    match_aws = classify_skill_match("AWS", cand_skills)
    assert match_aws.match_type == "transferable"
    assert match_aws.score == 0.70

    # Known exact match
    match_postgres = classify_skill_match("PostgreSQL", cand_skills)
    assert match_postgres.match_type == "exact"
    assert match_postgres.score == 1.0

    # Explicitly unrelated skill pair rejected
    match_java = classify_skill_match("Java", cand_skills)
    assert match_java.match_type == "missing"
    assert match_java.score == 0.0


def test_individual_requirement_weights():
    cand_skills = [CandidateSkill(raw_skill="Python")]
    reqs = [
        JobRequirement(skill="Python", importance="must_have", weight=20.0),
        JobRequirement(skill="Docker", importance="preferred", weight=5.0)
    ]
    coverage, matches = calculate_skill_coverage(reqs, cand_skills)
    # Weighted coverage: (1.0 * 20 + 0.0 * 5) / (20 + 5) = 20 / 25 = 0.8
    assert coverage == 0.80


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
    assert len(failed_f) == 2
