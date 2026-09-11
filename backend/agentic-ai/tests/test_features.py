"""
test_features.py
Unit tests for candidate-job feature matrix calculation.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from contracts.candidate import CandidateProfile, CandidateSkill, CandidateExperience, CandidateEducation
from contracts.job import JobProfile
from matching.feature_engineering import build_features


def test_build_features():
    job = JobProfile(
        job_id="J01",
        title="Backend Engineer",
        description="Python FastAPI backend developer",
        min_experience_months=36,
        must_have_skills=["Python", "FastAPI"],
        preferred_skills=["Docker", "AWS"],
        education_requirements=["Bachelor"]
    )

    candidate = CandidateProfile(
        candidate_id="C01",
        total_experience_months=48,
        skills=[
            CandidateSkill(raw_skill="Python"),
            CandidateSkill(raw_skill="FastAPI"),
            CandidateSkill(raw_skill="Azure")
        ],
        experiences=[CandidateExperience(role="Backend Developer", duration_months=48, description="Built Python APIs with FastAPI")],
        education=[CandidateEducation(degree="B.Tech", field="Computer Science")]
    )

    features, matches = build_features(candidate, job)
    assert features.must_have_coverage == 1.0
    assert features.experience_fit == 1.0
    assert features.education_match == 1.0
    assert len(matches) == 4
