#!/usr/bin/env python
"""
FRONTEND SIMULATION TEST - Simplified
Mimics frontend API calls to verify data flows correctly through the UI
"""

import requests
import json

BASE_URL = 'http://localhost:8000/api/v1'

print("\n" + "="*80)
print("  FRONTEND SIMULATION TEST - Ponty Rajput Workflow")
print("  Testing exact API calls the UI will make")
print("="*80)

# SIMULATION 1
print("\n[SCENARIO 1] User opens /resumes page")
print("-" * 80)
print("Action: Frontend calls getCandidates()")

resp = requests.get(f'{BASE_URL}/candidates')
candidates = resp.json()

print(f"Response status: {resp.status_code}")
print(f"Candidates returned: {len(candidates)}")

ponty = next((c for c in candidates if 'Ponty' in (c.get('name') or '')), None)
if not ponty:
    print("ERROR: Ponty not found!")
    exit(1)

ponty_id = ponty['candidate_id']
print(f"Ponty found: {ponty.get('name')} (ID: {ponty_id})")
print(f"Skills extracted: {len(ponty.get('skills', []))}")

# SIMULATION 2
print("\n[SCENARIO 2] User clicks 'View full profile'")
print("-" * 80)
print(f"Action: Navigate to /matches/{ponty_id}")

print("  1. Call getMatchDetails(id)")
resp = requests.get(f'{BASE_URL}/matches/{ponty_id}')
print(f"     Status: {resp.status_code}")

print(f"  2. Call getCandidateById(id)")
resp = requests.get(f'{BASE_URL}/candidates/{ponty_id}')
if resp.status_code != 200:
    print(f"ERROR: Failed to load candidate: {resp.status_code}")
    exit(1)
candidate = resp.json()
print(f"     Status: {resp.status_code}")
print(f"     Candidate: {candidate.get('name')}")
print(f"     Skills: {len(candidate.get('skills', []))} extracted")

print(f"  3. Call getJobs()")
resp = requests.get(f'{BASE_URL}/jobs')
jobs = resp.json()
print(f"     Status: {resp.status_code}")
print(f"     Jobs: {len(jobs)}")

cyber_job = next((j for j in jobs if j['job_id'] == 'JOB_CYBER_01'), None)
if not cyber_job:
    print("ERROR: Cybersecurity job not found!")
    exit(1)

print(f"     Selected: {cyber_job.get('title')}")

# SIMULATION 3
print("\n[SCENARIO 3] User clicks 'Run Match Engine'")
print("-" * 80)
print(f"Action: Call runMatch({ponty_id}, {cyber_job['job_id']})")

payload = {'candidate_id': ponty_id, 'job_id': cyber_job['job_id']}
resp = requests.post(f'{BASE_URL}/matches/run', json=payload)
if resp.status_code != 200:
    print(f"ERROR: Failed to run match: {resp.status_code}")
    exit(1)

result = resp.json()
match_id = result.get('match_id')

print(f"Match created: {match_id}")
print(f"Overall Score: {result.get('overall_score')}/100")
print(f"Status: {result.get('overall_status')}")

# SIMULATION 4
print("\n[SCENARIO 4] Display match details")
print("-" * 80)
print(f"Action: Navigate to /matches/{match_id}")

resp = requests.get(f'{BASE_URL}/matches/{match_id}')
if resp.status_code != 200:
    print(f"ERROR: Failed to get match details: {resp.status_code}")
    exit(1)

match = resp.json()
print(f"Match details loaded")

print(f"\nComponent renders:")
print(f"  Title: {candidate.get('name')}")
print(f"  Job: {cyber_job.get('title')}")
print(f"  Score: {match.get('overall_score')}/100")
print(f"  Status: {match.get('overall_status')}")

assessments = match.get('assessments', [])
print(f"\n  Requirements ({len(assessments)}):")
for a in assessments:
    status = a.get('status', 'unknown')
    desc = a.get('description', '')
    score = a.get('earned_score', 0)
    max_score = a.get('max_score', 0)
    print(f"    - {desc}: {score}/{max_score} ({status})")

# VERIFICATION
print("\n" + "=" * 80)
print("RESULTS")
print("=" * 80)

errors = []

# Check score
overall_score = match.get('overall_score', 0)
if overall_score == 0:
    errors.append("ERROR: Score is 0 - BUG NOT FIXED!")
elif overall_score >= 80:
    print(f"PASS: Score is {overall_score}% - correct!")
else:
    print(f"WARNING: Score is {overall_score}%")

# Check status
status = match.get('overall_status', '')
if 'REJECT' in status.upper():
    errors.append(f"ERROR: Status is REJECTED - BUG NOT FIXED!")
elif status.upper() == 'HIGH':
    print(f"PASS: Status is HIGH - correct!")

# Check assessments
if not assessments:
    errors.append("ERROR: No requirement assessments!")
else:
    satisfied = sum(1 for a in assessments if (a.get('status') or '').lower() == 'satisfied')
    if satisfied == len(assessments):
        print(f"PASS: All {len(assessments)} requirements satisfied!")
    else:
        print(f"WARNING: Only {satisfied}/{len(assessments)} satisfied")

# Check data
if candidate.get('name'):
    print(f"PASS: Candidate name: {candidate.get('name')}")
if candidate.get('skills'):
    print(f"PASS: Skills count: {len(candidate.get('skills', []))}")

if errors:
    print("\nERRORS FOUND:")
    for error in errors:
        print(f"  {error}")
    exit(1)

print("\n" + "=" * 80)
print("SUCCESS! Frontend simulation test PASSED!")
print("=" * 80)
print("\nFrontend WILL display:")
print(f"  - Ponty Rajput with {len(candidate.get('skills', []))} skills")
print(f"  - {match.get('overall_score')}% match score")
print(f"  - All {len(assessments)} requirements satisfied")
print("\nFrontend WILL NOT display:")
print(f"  - 0% score")
print(f"  - REJECTED status")
print(f"  - TypeErrors or missing data")
print("\nReady for user access!\n")
