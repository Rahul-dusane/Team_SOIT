"""
test_pipeline.py
Combined integration tests for candidate-job matching engine and LangGraph multi-agent recruitment pipeline.
"""

import sys
import os

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


def test_langgraph_full_pipeline():
    try:
        from app.workflows.graph import run_pipeline
        try:
            from tests.test_agents import SAMPLE_RESUME, SAMPLE_JD
        except ImportError:
            SAMPLE_RESUME = "Alex Johnson\nSkills: Python, FastAPI\nExperience: 4 years backend development"
            SAMPLE_JD = "Backend Engineer required. Python and FastAPI skills mandatory."

        resumes = {"C01": SAMPLE_RESUME}
        jobs = {"J01": SAMPLE_JD}

        result = run_pipeline(resume_texts=resumes, job_texts=jobs)

        assert result["workflow_status"] == "COMPLETED"
        assert "C01" in result["candidate_profiles"]
        assert "J01" in result["job_profiles"]
        assert len(result["match_results"]) > 0
    except ImportError:
        pass  # Skip if optional dependencies unavailable
