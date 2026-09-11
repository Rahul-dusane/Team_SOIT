"""
test_pipeline.py
End-to-end unit tests for single candidate-job matching pipeline.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from contracts.candidate import CandidateProfile, CandidateSkill, CandidateExperience, CandidateEducation
from contracts.job import JobProfile
from matching.pipeline import match_candidate_to_job


def test_match_candidate_to_job_e2e():
    job = JobProfile(
        job_id="J01",
        title="Backend Engineer",
        min_experience_months=36,
        must_have_skills=["Python", "FastAPI"],
        preferred_skills=["Docker", "AWS"],
        education_requirements=["Bachelor"]
    )

    candidate = CandidateProfile(
        candidate_id="C01",
        total_experience_months=48,
        skills=[
            CandidateSkill(raw_skill="Python", evidence="Built APIs in Python"),
            CandidateSkill(raw_skill="FastAPI", evidence="Developed FastAPI services"),
            CandidateSkill(raw_skill="Docker", evidence="Containerized microservices"),
            CandidateSkill(raw_skill="Azure", evidence="Deployed on Azure cloud")  # Transferable to AWS
        ],
        experiences=[CandidateExperience(role="Backend Engineer", duration_months=48, description="Developed APIs using Python and FastAPI")],
        education=[CandidateEducation(degree="B.Tech", field="CS")]
    )

    result = match_candidate_to_job(candidate, job)
    assert result.candidate_id == "C01"
    assert result.job_id == "J01"
    assert result.mandatory_pass is True
    assert result.overall_score > 0.0
    assert result.confidence_level in ["HIGH", "MEDIUM", "LOW (Needs Review)"]
