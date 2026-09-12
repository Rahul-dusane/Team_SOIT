#!/usr/bin/env python
import requests

resp = requests.get('http://localhost:8000/api/v1/matches/398dc5c8-ad05-4920-80f9-65c7c64dce71')
match = resp.json()

print("Assessment statuses:")
for a in match.get('assessments', []):
    status = a.get('status')
    print(f"  Status type: {type(status).__name__} | Value: '{status}' | Check: {status == 'SATISFIED'} vs {status.upper() == 'SATISFIED' if status else False}")
