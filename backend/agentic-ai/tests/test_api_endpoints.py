"""
test_api_endpoints.py
Integration tests for FastAPI REST API endpoints using TestClient.
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_job_and_candidate_api_flow():
    # Create Job
    job_payload = {
        "job_id": "J_API_01",
        "title": "Senior FastAPI Developer",
        "min_experience_months": 36,
        "must_have_skills": ["Python", "FastAPI"],
        "requirements": [
            {"description": "Build high-throughput REST APIs", "skill": "FastAPI", "importance": "must_have", "weight": 20.0}
        ]
    }
    res_job = client.post("/api/v1/jobs", json=job_payload)
    assert res_job.status_code == 200
    assert res_job.json()["job_id"] == "J_API_01"

    # Get Jobs List
    res_jobs = client.get("/api/v1/jobs")
    assert res_jobs.status_code == 200
    assert len(res_jobs.json()) >= 1

    # Run Match API
    cand_payload = {
        "candidate_id": "C_API_01",
        "name": "Alex Developer",
        "total_experience_months": 48,
        "skills": [{"raw_skill": "Python"}, {"raw_skill": "FastAPI"}],
        "experiences": [{"role": "Backend Engineer", "duration_months": 48, "description": "Built REST APIs with FastAPI"}]
    }
    res_match = client.post("/api/v1/matches/run", json={"candidate": cand_payload, "job": job_payload})
    assert res_match.status_code == 200
    match_data = res_match.json()
    assert match_data["candidate_id"] == "C_API_01"
    assert match_data["overall_score"] > 0.0

    # Get Ranking
    res_rank = client.get("/api/v1/ranking?job_id=J_API_01")
    assert res_rank.status_code == 200
    rank_data = res_rank.json()
    assert rank_data["total_candidates"] >= 1
    assert rank_data["rankings"][0]["candidate_id"] == "C_API_01"

    # Get Detailed Match Breakdown
    res_detail = client.get("/api/v1/matches/J_API_01/C_API_01")
    assert res_detail.status_code == 200
    detail_data = res_detail.json()
    assert detail_data["match_id"] is not None
    assert "assessments" in detail_data
    assert "summary" in detail_data
    assert "agent_logs" in detail_data


def test_resume_upload_api():
    file_content = b"John Smith\nEmail: john@example.com\nSkills: Python, FastAPI, PostgreSQL, AWS\n5 years experience building cloud services."
    files = [("files", ("john_resume.txt", file_content, "text/plain"))]

    res_upload = client.post("/api/v1/resumes/upload", files=files)
    assert res_upload.status_code == 200
    upload_data = res_upload.json()
    assert upload_data["successful"] == 1
    assert upload_data["file_results"][0]["status"] in ["success", "duplicate"]
    cand_id = upload_data["file_results"][0]["candidate_id"]

    # Verify Candidate via API
    res_cand = client.get(f"/api/v1/candidates/{cand_id}")
    assert res_cand.status_code == 200
    assert res_cand.json()["name"] == "John Smith"


def test_get_match_by_candidate_no_match():
    # Candidate ID without calculated match record should return HTTP 200 with status "no_match"
    res = client.get("/api/v1/matches/CAND_UNSAVED_TEST")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "no_match"
    assert data["match"] is None

