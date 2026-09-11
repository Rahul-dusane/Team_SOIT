from fastapi.testclient import TestClient
from app import create_app

client = TestClient(create_app())


def test_health_check():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_match_endpoint_success():
    payload = {
        "resume_text": "Python developer with 4 years experience. Bachelor degree.",
        "job_description": "Looking for a Python developer with 3 years experience.",
        "job_title": "Python Developer",
    }
    resp = client.post("/api/match", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert "overall_score" in body
    assert 0.0 <= body["overall_score"] <= 1.0


def test_match_endpoint_rejects_empty_input():
    payload = {"resume_text": "", "job_description": ""}
    resp = client.post("/api/match", json=payload)
    assert resp.status_code == 400
