"""
test_e2e_durable_workflow.py
End-to-End PostgreSQL & Checkpoint Recovery Test Suite.
Tests full workflow execution:
Upload -> Extraction -> Matching -> Atomic Persistence -> Session Close -> Reload & Compare.
"""

import pytest
from contracts.candidate import CandidateProfile, CandidateSkill
from contracts.job import JobProfile, JobRequirement
from matching.pipeline import match_candidate_to_job
from db.connection import SessionLocal, init_db
from db.repositories import CandidateRepository, JobRepository, MatchRepository


def test_durable_checkpoint_recovery():
    init_db()
    
    # 1. Instantiate contracts
    cand = CandidateProfile(
        candidate_id="C_DURABLE_01",
        name="Durable Candidate",
        total_experience_months=48,
        skills=[CandidateSkill(raw_skill="Python", normalized_skill="python")]
    )
    job = JobProfile(
        job_id="J_DURABLE_01",
        title="Durable Engineer",
        must_have_skills=["Python"]
    )
    
    # 2. Match
    match_res = match_candidate_to_job(cand, job)
    
    # 3. Persist in Session 1
    db1 = SessionLocal()
    try:
        cand_repo1 = CandidateRepository(db1)
        job_repo1 = JobRepository(db1)
        match_repo1 = MatchRepository(db1)
        
        cand_repo1.save_candidate(cand)
        job_repo1.save_job(job)
        saved_model = match_repo1.save_match_atomic(match_res)
        match_id = saved_model.match_id
    finally:
        db1.close()

    # 4. Restart/Open fresh Session 2
    db2 = SessionLocal()
    try:
        cand_repo2 = CandidateRepository(db2)
        job_repo2 = JobRepository(db2)
        match_repo2 = MatchRepository(db2)
        
        reloaded_cand = cand_repo2.get_candidate("C_DURABLE_01")
        reloaded_job = job_repo2.get_job("J_DURABLE_01")
        reloaded_match = match_repo2.get_match("J_DURABLE_01", "C_DURABLE_01")
        
        # 5. Value Audits & Field Equality Assertions
        assert reloaded_cand is not None
        assert reloaded_cand.name == "Durable Candidate"
        assert reloaded_cand.total_experience_months == 48
        
        assert reloaded_job is not None
        assert reloaded_job.title == "Durable Engineer"
        
        assert reloaded_match is not None
        assert reloaded_match.match_id == match_id
        assert reloaded_match.overall_score == match_res.overall_score
        assert reloaded_match.overall_status == match_res.confidence_level
    finally:
        db2.close()
