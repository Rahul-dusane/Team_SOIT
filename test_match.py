import sys
sys.path.insert(0, 'backend/agentic-ai')
from db.connection import SessionLocal, init_db
from db.repositories import CandidateRepository, JobRepository, MatchRepository
from matching.pipeline import match_candidate_to_job

# Initialize
init_db()
db = SessionLocal()

# Try to run a match
cand_repo = CandidateRepository(db)
job_repo = JobRepository(db)

c = cand_repo.get_candidate('C01')  # Alice Backend
j = job_repo.get_job('J01')  # Backend Engineer

if c and j:
    print(f'Running match: {c.name} vs {j.title}')
    
    # Run match
    result = match_candidate_to_job(c, j, db=db)
    print(f'Raw Score: {result.raw_score}')
    print(f'Overall Score: {result.overall_score}')
    print(f'Confidence: {result.confidence_level}')
    print(f'Decision: {result.decision}')
    print(f'Mandatory Pass: {result.mandatory_pass}')
    
    # Try to save
    match_repo = MatchRepository(db)
    saved = match_repo.save_match_atomic(result)
    print(f'Saved Match ID: {saved.match_id}')
    
    # Try to retrieve
    retrieved = match_repo.get_match_by_id(saved.match_id)
    if retrieved:
        print(f'Retrieved Match: {retrieved.match_id}')
    else:
        print('Match NOT FOUND after save')
else:
    print('Missing candidate or job')

db.close()
