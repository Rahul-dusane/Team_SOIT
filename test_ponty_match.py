import requests
import json

# Run match with Ponty
resp = requests.post(
    'http://localhost:8000/api/v1/matches/run',
    json={'candidate_id': 'CAND_E1D7D7A637', 'job_id': 'JOB_VERIFY_01'}
)
print(f'Status: {resp.status_code}')
result = resp.json()
print(f'Match ID: {result.get("match_id")}')
print(f'Candidate: {result.get("candidate_id")}')
print(f'Overall Score: {result.get("overall_score")}')
print(f'Status: {result.get("overall_status")}')
print(f'Decision: {result.get("decision")}')
print()

# Get match details
if result.get('match_id'):
    match_id = result['match_id']
    resp = requests.get(f'http://localhost:8000/api/v1/matches/{match_id}')
    match_detail = resp.json()
    print(f'\n=== FULL MATCH DETAIL ===')
    print(f'Overall Score: {match_detail.get("overall_score")}')
    print(f'Raw Score: {match_detail.get("raw_score_breakdown")}')
    print(f'Assessments: {len(match_detail.get("assessments", []))} items')
    for a in match_detail.get('assessments', [])[:3]:
        print(f'  - {a.get("description")}: {a.get("status")}')
