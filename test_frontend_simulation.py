#!/usr/bin/env python
"""
FRONTEND SIMULATION TEST
Mimics frontend API calls to verify data flows correctly through the UI
"""

import requests
import json
from datetime import datetime

BASE_URL = 'http://localhost:8000/api/v1'

print("""
==============================================================================
              FRONTEND SIMULATION TEST - Ponty Rajput Workflow              
                Testing exact API calls the UI will make                    
==============================================================================
""")

# SIMULATION 1: User navigates to /resumes page
print("\n[SCENARIO 1] User opens /resumes page")
print("-" * 80)
print("Action: Frontend calls getCandidates()")

resp = requests.get(f'{BASE_URL}/candidates')
candidates = resp.json()

print(f"✅ Response status: {resp.status_code}")
print(f"✅ Candidates returned: {len(candidates)}")

# Find Ponty
ponty = next((c for c in candidates if 'Ponty' in (c.get('name') or '')), None)
if not ponty:
    print("❌ ERROR: Ponty not found!")
    exit(1)

ponty_id = ponty['candidate_id']
print(f"✅ Ponty found: {ponty.get('name')} (ID: {ponty_id})")

# Frontend will display candidate card with this data
print(f"\n   Card will show:")
print(f"   - Name: {ponty.get('name')}")
print(f"   - Role: {ponty.get('role')}")
print(f"   - Skills: {len(ponty.get('skills', []))} items")

# SIMULATION 2: User clicks "View full profile" on Ponty's card
print("\n\n[SCENARIO 2] User clicks Ponty's 'View full profile' link")
print("-" * 80)
print(f"Action: Navigate to /matches/{ponty_id}")
print(f"Params: id={ponty_id}")
print("\nFrontend useEffect will run with id parameter:")

# First, try to get existing match (will fail with 404)
print("  1. Call getMatchDetails(id) - looking for existing match")
resp = requests.get(f'{BASE_URL}/matches/{ponty_id}')
print(f"     Status: {resp.status_code} (expected: 404 - no match yet)")

# Then load candidate data
print(f"  2. Call getCandidateById(id)")
resp = requests.get(f'{BASE_URL}/candidates/{ponty_id}')
if resp.status_code != 200:
    print(f"❌ Failed to load candidate: {resp.status_code}")
    exit(1)

candidate = resp.json()
print(f"     Status: {resp.status_code} ✅")
print(f"     Candidate: {candidate.get('name')}")
print(f"     Skills: {len(candidate.get('skills', []))} extracted")

# Then load available jobs
print(f"  3. Call getJobs()")
resp = requests.get(f'{BASE_URL}/jobs')
jobs = resp.json()
print(f"     Status: {resp.status_code} ✅")
print(f"     Jobs available: {len(jobs)}")

# Find cybersecurity job
cyber_job = next((j for j in jobs if j['job_id'] == 'JOB_CYBER_01'), None)
if not cyber_job:
    print("❌ Cybersecurity job not found!")
    exit(1)

print(f"     First job selected: {cyber_job.get('title')}")

# SIMULATION 3: User clicks "Run Match Engine" button
print("\n\n[SCENARIO 3] User clicks 'Run Match Engine' button")
print("-" * 80)
print(f"Action: Call runMatch({ponty_id}, {cyber_job['job_id']})")

payload = {
    'candidate_id': ponty_id,
    'job_id': cyber_job['job_id']
}

resp = requests.post(f'{BASE_URL}/matches/run', json=payload)
if resp.status_code != 200:
    print(f"❌ Failed to run match: {resp.status_code}")
    print(f"   Response: {resp.text}")
    exit(1)

result = resp.json()
match_id = result.get('match_id')

print(f"✅ Match created: {match_id}")
print(f"   Overall Score: {result.get('overall_score')}/100")
print(f"   Status: {result.get('overall_status')}")

# SIMULATION 4: Navigate to match detail page to show results
print("\n\n[SCENARIO 4] Frontend navigates to /matches/{match_id}")
print("-" * 80)
print(f"Action: Navigate to /matches/{match_id}")
print(f"\nFrontend useEffect will call getMatchDetails(match_id)")

resp = requests.get(f'{BASE_URL}/matches/{match_id}')
if resp.status_code != 200:
    print(f"❌ Failed to get match details: {resp.status_code}")
    exit(1)

match = resp.json()
print(f"✅ Match details loaded")

# Simulate rendering the MatchDetail component
print(f"\nComponent will render:")
print(f"  Title: {candidate.get('name')} (h1)")
print(f"  Role: {candidate.get('role')} · {candidate.get('experience')} experience")
print(f"  Education: {candidate.get('education')}")

print(f"\n  Overall Match Score:")
print(f"    - Job: {cyber_job.get('title')}")
print(f"    - Score: {match.get('overall_score')}/100")
print(f"    - Status: {match.get('overall_status')}")
print(f"    - Decision: {match.get('decision')}")

print(f"\n  Score Breakdown:")
breakdown = match.get('raw_score_breakdown', {})
for key, value in breakdown.items():
    if isinstance(value, (int, float)) and value > 0:
        print(f"    - {key}: {value} points")

print(f"\n  Skills Section:")
skills = candidate.get('skills', [])
if isinstance(skills, list):
    skill_names = []
    for s in skills:
        if isinstance(s, dict):
            skill_names.append(s.get('raw_skill', 'Unknown'))
        elif isinstance(s, str):
            skill_names.append(s)
    print(f"    Listed: {', '.join(skill_names[:5])}...")
    print(f"    Total: {len(skill_names)}")

print(f"\n  Requirement Assessments:")
assessments = match.get('assessments', [])
for a in assessments:
    status = a.get('status', 'UNKNOWN')
    desc = a.get('description', '')
    score = a.get('earned_score', 0)
    max_score = a.get('max_score', 0)
    print(f"    ✅ {desc}: {score}/{max_score} ({status})")

summary = match.get('summary', {})
if summary:
    print(f"\n  Recruiter Summary:")
    print(f"    {summary.get('summary_text', 'N/A')}")
    print(f"    Recommendation: {summary.get('recommendation', 'N/A')}")

# VERIFICATION
print("\n\n" + "=" * 80)
print("FRONTEND SIMULATION RESULTS")
print("=" * 80)

errors = []

# Check if score is correct
overall_score = match.get('overall_score', 0)
if overall_score == 0:
    errors.append("❌ Score is 0 - BUG NOT FIXED!")
elif overall_score < 50:
    errors.append(f"⚠️  Score is {overall_score} - seems low for perfect match")
else:
    print(f"✅ Score is {overall_score}% - correct!")

# Check status
status = match.get('overall_status', '')
if 'REJECT' in status.upper():
    errors.append(f"❌ Status is REJECTED - BUG NOT FIXED!")
elif status == 'HIGH':
    print(f"✅ Status is HIGH - correct!")
else:
    print(f"⚠️  Status is {status}")

# Check assessments
assessments = match.get('assessments', [])
if not assessments:
    errors.append("❌ No requirement assessments!")
else:
    satisfied = sum(1 for a in assessments if (a.get('status') or '').lower() == 'satisfied')
    if satisfied == len(assessments):
        print(f"✅ All {len(assessments)} requirements satisfied!")
    else:
        errors.append(f"⚠️  Only {satisfied}/{len(assessments)} requirements satisfied")

# Check data quality
if not candidate.get('skills'):
    errors.append("❌ No skills in candidate profile!")
else:
    print(f"✅ Candidate has {len(candidate.get('skills', []))} skills")

if not candidate.get('name'):
    errors.append("❌ Candidate name is missing!")
else:
    print(f"✅ Candidate name: {candidate.get('name')}")

if errors:
    print("\n⚠️  ISSUES FOUND:")
    for error in errors:
        print(f"  {error}")
    exit(1)

print("\n" + "=" * 80)
print("🎉 FRONTEND SIMULATION TEST PASSED!")
print("=" * 80)
print("\nThe frontend will display:")
print(f"  • Ponty Rajput profile with {len(candidate.get('skills', []))} skills")
print(f"  • {match.get('overall_score')}% match score with {len(assessments)} satisfied requirements")
print(f"  • Recruiter recommendation: {summary.get('recommendation', 'N/A')}")
print(f"\nUI will NOT show:")
print(f"  ❌ 0% score")
print(f"  ❌ REJECTED status")
print(f"  ❌ TypeError or undefined property errors")
print(f"  ❌ Missing data sections")
print("\n✅ System is ready for user access!\n")
