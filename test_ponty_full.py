#!/usr/bin/env python
import requests
import json

print("=== FETCHING JOBS ===")
resp = requests.get('http://localhost:8000/api/v1/jobs')
jobs = resp.json()

for job in jobs:
    print(f"{job['job_id']}: {job['title']}")

print("\n=== CREATING CYBERSECURITY JOB ===")

cybersec_job = {
    "job_id": "JOB_CYBER_01",
    "title": "Cybersecurity Analyst & Penetration Tester",
    "description": "Conduct penetration testing and vulnerability assessments",
    "domain": ["Cybersecurity & Information Security"],
    "min_experience_months": 0,
    "must_have_skills": ["Penetration Testing", "Vulnerability Assessment"],
    "preferred_skills": ["CEH", "Ethical Hacking", "Network Security"],
    "education_requirements": [],
    "certifications": ["CEH"],
    "responsibilities": [],
    "requirements": [
        {
            "requirement_id": "REQ_CYBER_01",
            "description": "Hands-on experience in Penetration Testing",
            "skill": "Penetration Testing",
            "category": "competency",
            "importance": "must_have",
            "mandatory": True,
            "weight": 35.0,
            "minimum_duration_months": 0
        },
        {
            "requirement_id": "REQ_CYBER_02",
            "description": "Hands-on experience in Vulnerability Assessment",
            "skill": "Vulnerability Assessment",
            "category": "competency",
            "importance": "must_have",
            "mandatory": True,
            "weight": 35.0,
            "minimum_duration_months": 0
        },
        {
            "requirement_id": "REQ_CYBER_03",
            "description": "CEH Certification",
            "skill": "CEH",
            "category": "certification",
            "importance": "preferred",
            "mandatory": False,
            "weight": 20.0,
            "minimum_duration_months": 0
        }
    ]
}

resp = requests.post('http://localhost:8000/api/v1/jobs', json=cybersec_job)
print(f"Status: {resp.status_code}")
print(f"Response: {json.dumps(resp.json(), indent=2)}")

print("\n=== RUNNING PONTY MATCH ===")
resp = requests.post(
    'http://localhost:8000/api/v1/matches/run',
    json={'candidate_id': 'CAND_E1D7D7A637', 'job_id': 'JOB_CYBER_01'}
)
print(f"Status: {resp.status_code}")
result = resp.json()
print(f"Result: {json.dumps(result, indent=2)}")
