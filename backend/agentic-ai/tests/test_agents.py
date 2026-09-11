"""Unit tests for Resume Agent, Job Agent, and Schemas."""

import sys
import os

# Add parent directory to path so tests can import app modules directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.schemas.candidate import CandidateProfile, Skill
from app.schemas.job import JobProfile, JobRequirement
from app.agents.resume_agent import extract_candidate_profile
from app.agents.job_agent import extract_job_profile


SAMPLE_RESUME = """
Alex Johnson
Email: alex.johnson@example.com | Phone: +1-555-0199
Summary: Backend Engineer with 4 years experience designing microservices.

Skills:
- Languages: Python, SQL
- Frameworks: FastAPI, Flask
- Databases: PostgreSQL, Redis
- Infrastructure: Docker, AWS ECS

Experience:
TechCorp (3 years / 36 months)
Backend Software Engineer
- Designed and maintained high-throughput REST APIs using Python and FastAPI.
- Optimized PostgreSQL queries and implemented Redis caching, reducing p99 latency by 35%.
- Packaged services into Docker containers and deployed onto AWS ECS.

StartupX (1 year / 12 months)
Junior Software Developer
- Implemented automated data ingestion scripts in Python.

Education:
B.S. in Computer Science, State University (Graduation 2021)
"""

SAMPLE_JD = """
Job Title: Senior Backend Engineer

About the Role:
We are looking for an experienced Backend Engineer to lead API development.

Required Qualifications (Must Have):
- Minimum 3 years of hands-on experience in backend engineering.
- Deep proficiency in Python and FastAPI.
- Production experience with relational databases (PostgreSQL).
- Hands-on experience with Kubernetes container orchestration.

Preferred Qualifications:
- Familiarity with Docker and container workflows.
- Experience with AWS cloud infrastructure.

Responsibilities:
- Architect distributed backend microservices.
- Lead database design and query tuning.
- Deploy and monitor applications in Kubernetes clusters.
"""


def test_resume_agent():
    print("\n--- Running test_resume_agent ---")
    profile = extract_candidate_profile("C01", SAMPLE_RESUME)
    assert isinstance(profile, CandidateProfile)
    assert profile.candidate_id == "C01"
    assert len(profile.skills) > 0
    assert profile.total_experience_months >= 36
    print(f"✓ Candidate Extracted: {profile.name}")
    print(f"✓ Total Experience: {profile.total_experience_months} months")
    print(f"✓ Extracted Skills ({len(profile.skills)}): {[s.name for s in profile.skills]}")


def test_job_agent():
    print("\n--- Running test_job_agent ---")
    job = extract_job_profile("J01", SAMPLE_JD)
    assert isinstance(job, JobProfile)
    assert job.job_id == "J01"
    assert len(job.must_have_skills) > 0
    assert job.min_experience_months >= 36
    print(f"✓ Job Title: {job.title}")
    print(f"✓ Must-Have Skills: {job.must_have_skills}")
    print(f"✓ Preferred Skills: {job.preferred_skills}")
    print(f"✓ Minimum Experience: {job.min_experience_months} months")


if __name__ == "__main__":
    test_resume_agent()
    test_job_agent()
    print("\n All agent unit tests passed!")

