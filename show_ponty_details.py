#!/usr/bin/env python
import requests
import json

match_id = "398dc5c8-ad05-4920-80f9-65c7c64dce71"

resp = requests.get(f'http://localhost:8000/api/v1/matches/{match_id}')
match_detail = resp.json()

print("=== PONTY RAJPUT MATCH DETAILS ===\n")
print(f"Match ID: {match_detail.get('match_id')}")
print(f"Candidate: {match_detail.get('candidate_id')}")
print(f"Job: {match_detail.get('job_id')}")
print(f"\n=== SCORES ===")
print(f"Overall Score: {match_detail.get('overall_score')}/100")
print(f"Raw Score: {match_detail.get('raw_score')}")
print(f"Status: {match_detail.get('overall_status')}")
print(f"Decision: {match_detail.get('decision')}")
print(f"Evidence Coverage: {match_detail.get('evidence_coverage'):.0%}")

print(f"\n=== SCORE BREAKDOWN ===")
breakdown = match_detail.get('raw_score_breakdown', {})
for key, value in breakdown.items():
    print(f"{key}: {value} points")

print(f"\n=== REQUIREMENT ASSESSMENTS ===")
assessments = match_detail.get('assessments', [])
print(f"Total: {len(assessments)}")
for a in assessments:
    status = a.get('status', 'unknown')
    desc = a.get('description', 'N/A')
    earned = a.get('earned_score', 0)
    max_score = a.get('max_score', 10)
    print(f"  {status.upper()}: {desc} ({earned}/{max_score})")

print(f"\n=== SUMMARY ===")
summary = match_detail.get('summary', {})
print(f"Summary: {summary.get('summary_text', 'N/A')}")
print(f"Strengths: {summary.get('key_strengths', [])}")
print(f"Gaps: {summary.get('key_gaps', [])}")
print(f"Recommendation: {summary.get('recommendation', 'N/A')}")

print(f"\n=== UNCERTAINTY FLAGS ===")
flags = match_detail.get('uncertainty_flags', [])
if flags:
    for f in flags:
        print(f"  - {f}")
else:
    print("  None")
