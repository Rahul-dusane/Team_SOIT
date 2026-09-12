"""Actual API/database checks on disposable SQLite; offline embedding fallback."""
import run_backend_tests as isolated
import json
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app
from db.connection import engine, SessionLocal
from db.repositories import MatchRepository
from ingestion.chunker import chunk_pages_or_sections

results = []
def check(name, actual, expected):
    results.append({'name': name, 'actual': actual, 'expected': expected, 'passed': actual == expected})

source = 'Payroll first role. Payroll second role.'
chunks = chunk_pages_or_sections([{'page_number': 1, 'text': source}], chunk_size_words=3, overlap_words=0)
check('Repeated-word chunk offsets reproduce source', all(source[c['start_char']:c['end_char']] == c['content'] for c in chunks), True)

with TestClient(app, raise_server_exceptions=False) as client:
    upload = client.post('/api/v1/resumes/upload', files=[('files', ('resume.txt', b'Pat Example\nEmail: pat@example.test\nBookkeeping and payroll.\nNo education information provided.', 'text/plain'))])
    check('TXT upload succeeds', upload.status_code, 200)
    if upload.status_code == 200:
        data = upload.json()['file_results'][0]
        cid = data['candidate_id']
        check('No education invented', data['candidate']['education'], [])
        dup = client.post('/api/v1/resumes/upload', files=[('files', ('resume.txt', b'Pat Example\nEmail: pat@example.test\nBookkeeping and payroll.\nNo education information provided.', 'text/plain'))])
        check('Duplicate upload returns same candidate', dup.json()['file_results'][0]['candidate_id'], cid)
        check('Anonymous candidate read blocked', client.get('/api/v1/candidates/' + cid).status_code in (401,403), True)
        job = {'job_id':'AUDIT_JOB','title':'Accountant','requirements':[{'skill':'Bookkeeping','description':'Bookkeeping','importance':'must_have'}]}
        check('Job creation succeeds', client.post('/api/v1/jobs',json=job).status_code, 200)
        match = client.post('/api/v1/matches/run',json={'candidate_id':cid,'job_id':'AUDIT_JOB'})
        check('Match succeeds',match.status_code,200)
        check('Saved match retrievable',client.get('/api/v1/matches/AUDIT_JOB/'+cid).status_code,200)
        engine.dispose()
        check('Match survives DB reconnect',client.get('/api/v1/matches/AUDIT_JOB/'+cid).status_code,200)
        # Fault injection: checks real API handling of an unsuccessful repository write.
        with patch.object(MatchRepository,'save_match_atomic',side_effect=RuntimeError('Injected storage failure')):
            fail = client.post('/api/v1/matches/run',json={'candidate_id':cid,'job_id':'AUDIT_JOB'})
        check('Failed save does not return success',fail.status_code >= 500,True)
        check('Anonymous deletion blocked',client.delete('/api/v1/candidates/'+cid).status_code in (401,403),True)
    bad = client.post('/api/v1/resumes/upload', files=[('files', ('bad.exe', b'not a resume', 'application/octet-stream'))])
    check('Invalid upload reported failed',bad.json().get('failed'),1)

out = isolated.ROOT/'audit'/'real_world_results.json'
out.write_text(json.dumps({'mode':'actual TestClient and disposable SQLite; offline model fallback; no live LLM/PostgreSQL', 'checks':results},indent=2),encoding='utf-8')
for r in results: print(('PASS' if r['passed'] else 'FAIL'),r['name'],str(r['actual'])[:300])
print('TOTAL',sum(r['passed'] for r in results),'/',len(results))
