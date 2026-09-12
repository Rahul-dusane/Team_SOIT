import requests

# Get all jobs
resp = requests.get('http://localhost:8000/api/v1/jobs')
jobs = resp.json()
print('=== AVAILABLE JOBS ===')
for j in jobs:
    print(f'{j["job_id"]}: {j["title"]}')
    if j.get('must_have_skills'):
        print(f'  Must-have: {j["must_have_skills"][:3]}...')
    print()

# Create a cybersecurity job if it doesn't exist
cybersec_jobs = [j for j in jobs if 'cyber' in j['title'].lower() or 'penetration' in j['title'].lower()]
if not cybersec_jobs:
    print('No cybersecurity job found. Creating one...')
    from contracts.job import JobProfile, JobRequirement
    
    job = JobProfile(
        job_id='JOB_CYBER_01',
        title='Cybersecurity Analyst & Penetration Tester',
        description='Conduct penetration testing and security assessments',
        must_have_skills=['Penetration Testing', 'Vulnerability Assessment'],
        preferred_skills=['CEH', 'Ethical Hacking', 'Network Security'],
        min_experience_months=0
    )
    
    resp = requests.post('http://localhost:8000/api/v1/jobs', json=job.model_dump())
    print(f'Created job: {resp.json()}')
else:
    print(f'Found cybersecurity job: {cybersec_jobs[0]["job_id"]}')
