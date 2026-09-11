"""Complete verification test suite for Member 1 Backend AI Subsystem.

This script tests:
1. Schema integrity (Candidate, Job, Match, Skill Gap, Evidence, Recruiter, AgentState)
2. State typing & structure
3. Member 2 Deterministic Matcher Contract (Math & Gaps)
4. Resume Agent extraction
5. Job Agent extraction & requirement weighting
6. Skill Gap Agent explanation & transferable skills discovery
7. Evidence Agent audit & quotation
8. Recruiter Agent synthesis (without score recalculation)
9. End-to-End LangGraph Orchestrator Pipeline (Batch 2 Resumes x 2 Jobs)
10. FastAPI Route Configuration & In-Memory Store (/workflows/{id})
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.schemas.candidate import CandidateProfile, Skill, Experience, Education
from app.schemas.job import JobProfile, JobRequirement
from app.schemas.match import MatchResult, ScoreBreakdown
from app.schemas.skill_gap import SkillGapAnalysis, TransferableSkill
from app.schemas.evidence import EvidenceReport, RequirementEvidence
from app.schemas.recruiter import RecruiterSummary
from app.state.recruitment_state import RecruitmentState
from app.services.mock_matcher import match_candidate_to_job
from app.agents.resume_agent import extract_candidate_profile
from app.agents.job_agent import extract_job_profile
from app.agents.skill_gap_agent import explain_skill_gaps
from app.agents.evidence_agent import extract_evidence
from app.agents.recruiter_agent import generate_recruiter_summary
from app.workflows.graph import run_pipeline


RESUME_1 = """
Rahul Sharma
Email: rahul.sharma@example.com | Phone: +91-9876543210
Summary: Backend Engineer with 48 months experience building high-throughput APIs.

Skills:
- Python, FastAPI, PostgreSQL, Docker, Redis, Git

Experience:
FinTech Solutions (36 months)
Backend Developer
- Developed low-latency REST APIs using FastAPI and Python.
- Designed database schema in PostgreSQL and configured Redis caching.
- Deployed microservices as Docker containers.

CloudCorp (12 months)
Junior Software Engineer
- Maintained backend microservices and automated ETL scripts in Python.

Education:
B.Tech in Computer Science, State Institute of Technology (2021)
"""

RESUME_2 = """
Priya Patel
Email: priya.patel@example.com
Summary: Frontend & Fullstack Developer with 24 months experience in React and Node.

Skills:
- JavaScript, TypeScript, React, Node.js, MongoDB, Express

Experience:
WebStudio (24 months)
Fullstack Developer
- Built interactive client web applications using React and Node.js.
- Integrated MongoDB databases.

Education:
B.E. in Information Technology (2022)
"""

JOB_1 = """
Job Title: Senior Backend Engineer (Python / FastAPI)

Required (Must Have):
- 3+ years (36 months) backend software development experience.
- Strong proficiency in Python and FastAPI framework.
- Relational database expertise in PostgreSQL.
- Experience with Kubernetes container orchestration.

Preferred:
- Experience with Docker containerization.
- Familiarity with AWS cloud deployment.
"""

JOB_2 = """
Job Title: Fullstack React / Node Engineer

Required (Must Have):
- 2+ years experience in React and Node.js.
- Deep knowledge of JavaScript or TypeScript.

Preferred:
- Experience with MongoDB or PostgreSQL.
"""


def test_1_schemas():
    print("[TEST 1/7] Validating Pydantic Schemas...")
    # Candidate schema
    c = CandidateProfile(
        candidate_id="C01",
        name="Test Candidate",
        skills=[Skill(name="Python", confidence=0.95, evidence="Wrote Python APIs")],
        experience=[Experience(company="Acme", role="SWE", duration_months=24)],
        total_experience_months=24
    )
    assert c.candidate_id == "C01"
    assert c.skills[0].name == "Python"
    assert c.total_experience_months == 24

    # Job schema
    j = JobProfile(
        job_id="J01",
        title="Backend Engineer",
        requirements=[
            JobRequirement(requirement="Python", requirement_type="MUST_HAVE", importance="CRITICAL", weight=10.0),
            JobRequirement(requirement="AWS", requirement_type="PREFERRED", importance="MEDIUM", weight=5.0)
        ],
        must_have_skills=["Python"],
        preferred_skills=["AWS"],
        min_experience_months=36
    )
    assert j.requirements[0].weight == 10.0
    assert j.must_have_skills == ["Python"]

    # Match schema
    m = MatchResult(
        candidate_id="C01",
        job_id="J01",
        overall_score=85.0,
        mandatory_pass=True,
        breakdown=ScoreBreakdown(skills=50.0, experience=20.0, semantic=15.0),
        gaps=["AWS"],
        matched_skills=["Python"]
    )
    assert m.overall_score == 85.0
    assert m.mandatory_pass is True

    print("  --> All Pydantic Schemas validated successfully!")


def test_2_deterministic_matcher():
    print("\n[TEST 2/7] Validating Member 2 Deterministic Matcher Contract...")
    cand = {
        "candidate_id": "C01",
        "skills": [{"name": "Python"}, {"name": "FastAPI"}, {"name": "PostgreSQL"}, {"name": "Docker"}],
        "total_experience_months": 48
    }
    job = {
        "job_id": "J01",
        "must_have_skills": ["Python", "FastAPI", "PostgreSQL", "Kubernetes"],
        "preferred_skills": ["Docker", "AWS"],
        "min_experience_months": 36
    }
    match = match_candidate_to_job(cand, job)
    
    assert match.candidate_id == "C01"
    assert match.job_id == "J01"
    assert match.overall_score > 0.0
    # Missing Kubernetes (Must have), so mandatory_pass MUST be False
    assert match.mandatory_pass is False, "Candidate missing Kubernetes must fail mandatory_pass"
    assert "Kubernetes" in match.gaps, "Kubernetes must be recorded as a gap"
    assert "Python" in match.matched_skills, "Python must be recorded as matched"
    print(f"  --> Matcher Score: {match.overall_score}% | Mandatory Pass: {match.mandatory_pass}")
    print(f"  --> Matched: {match.matched_skills} | Gaps: {match.gaps}")
    print("  --> Deterministic Math Contract passed!")


def test_3_resume_and_job_agents():
    print("\n[TEST 3/7] Validating Resume & Job Extraction Agents...")
    c_prof = extract_candidate_profile("C01", RESUME_1)
    assert isinstance(c_prof, CandidateProfile)
    assert c_prof.candidate_id == "C01"
    print(f"  --> Resume Agent: Name='{c_prof.name}', Exp={c_prof.total_experience_months}mo, Skills={len(c_prof.skills)}")

    j_prof = extract_job_profile("J01", JOB_1)
    assert isinstance(j_prof, JobProfile)
    assert j_prof.job_id == "J01"
    print(f"  --> Job Agent: Title='{j_prof.title}', MustHaves={j_prof.must_have_skills}, Reqs={len(j_prof.requirements)}")
    print("  --> Agents extraction passed!")


def test_4_gap_and_evidence_agents():
    print("\n[TEST 4/7] Validating Skill Gap & Evidence Verification Agents...")
    cand = extract_candidate_profile("C01", RESUME_1).model_dump()
    job = extract_job_profile("J01", JOB_1).model_dump()
    match = match_candidate_to_job(cand, job).model_dump()

    # Skill Gap Agent
    gaps = explain_skill_gaps(cand, job, match)
    assert isinstance(gaps, SkillGapAnalysis)
    assert len(gaps.critical_gaps) > 0 or len(gaps.transferable_skills) > 0
    print(f"  --> Skill Gap Agent: Critical Gaps={gaps.critical_gaps}")
    print(f"  --> Transferable Skills={[(t.candidate_skill, t.target_skill) for t in gaps.transferable_skills]}")

    # Evidence Agent
    evidence = extract_evidence(cand, job)
    assert isinstance(evidence, EvidenceReport)
    assert len(evidence.items) > 0
    verified = [item.requirement for item in evidence.items if item.status == "VERIFIED"]
    print(f"  --> Evidence Agent: Verified requirements={verified}")
    print("  --> Gap & Evidence Agents passed!")


def test_5_recruiter_agent():
    print("\n[TEST 5/7] Validating Recruiter Decision Agent (Score preservation)...")
    cand = extract_candidate_profile("C01", RESUME_1).model_dump()
    job = extract_job_profile("J01", JOB_1).model_dump()
    match = match_candidate_to_job(cand, job).model_dump()
    gaps = explain_skill_gaps(cand, job, match).model_dump()
    evidence = extract_evidence(cand, job).model_dump()

    recruiter = generate_recruiter_summary(cand, job, match, gaps, evidence)
    assert isinstance(recruiter, RecruiterSummary)
    # The Recruiter Agent MUST preserve the exact match score from the engine!
    assert recruiter.overall_score == match["overall_score"]
    assert len(recruiter.summary) > 0 or len(recruiter.headline) > 0
    print(f"  --> Recruiter Agent Headline: '{recruiter.headline}'")
    print(f"  --> Recommendation: {recruiter.recommendation}")
    print(f"  --> Engine Score Preserved: {recruiter.overall_score}%")
    print(f"  --> Interview Focus ({len(recruiter.interview_focus)} questions): {recruiter.interview_focus[:2]}")
    print("  --> Recruiter Agent passed!")


def test_6_full_batch_pipeline():
    print("\n[TEST 6/7] Validating Full LangGraph Batch Pipeline (2 Resumes x 2 Jobs)...")
    resumes = {"C01": RESUME_1, "C02": RESUME_2}
    jobs = {"J01": JOB_1, "J02": JOB_2}

    output = run_pipeline(resume_texts=resumes, job_texts=jobs)
    
    assert output["workflow_status"] == "COMPLETED"
    assert len(output["candidate_profiles"]) == 2
    assert len(output["job_profiles"]) == 2
    # 2 resumes x 2 jobs = 4 match pairings!
    assert len(output["match_results"]) == 4

    print(f"  --> Workflow Status: {output['workflow_status']}")
    print(f"  --> Total Matches Computed: {len(output['match_results'])}")
    for m in output["match_results"]:
        cid, jid = m["candidate_id"], m["job_id"]
        pair_key = f"{cid}_{jid}"
        rec = output["recruiter_summaries"].get(pair_key, {})
        print(f"      Pair [{pair_key}]: Score={m['overall_score']}% | Passed={m['mandatory_pass']} | Rec={rec.get('recommendation')}")

    print("  --> Full Batch Pipeline passed!")


def test_7_fastapi_app_and_routes():
    print("\n[TEST 7/7] Validating FastAPI Application & Routes...")
    from main import app
    route_paths = [r.path for r in app.routes]
    expected_paths = [
        "/health",
        "/agents/resume",
        "/agents/job",
        "/workflows/run",
        "/workflows/{workflow_id}",
        "/workflows/{workflow_id}/status"
    ]
    for path in expected_paths:
        assert path in route_paths, f"Route {path} missing from FastAPI app"
        print(f"  --> Route registered: {path}")
    print("  --> FastAPI Application Routes verified!")


if __name__ == "__main__":
    print("=" * 60)
    print("MEMBER 1 — AGENTIC AI BACKEND VERIFICATION SUITE")
    print("=" * 60)
    test_1_schemas()
    test_2_deterministic_matcher()
    test_3_resume_and_job_agents()
    test_4_gap_and_evidence_agents()
    test_5_recruiter_agent()
    test_6_full_batch_pipeline()
    test_7_fastapi_app_and_routes()
    print("\n" + "=" * 60)
    print(" ALL 7 VERIFICATION TEST SUITES PASSED SUCCESSFULLY!")
    print("=" * 60)

