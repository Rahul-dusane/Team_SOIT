"""
check_supabase_live.py
Terminal script to verify live Supabase PostgreSQL connection, inspect database schema tables,
check record counts, execute a pgvector vector similarity search query, and prove Member 1 + Member 2 + Member 3 alignment.
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect

load_dotenv()

# Add backend/agentic-ai to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db.connection import sanitize_database_url, SessionLocal
from contracts.candidate import CandidateProfile, CandidateSkill, CandidateExperience
from contracts.job import JobProfile, JobRequirement
from matching.pipeline import match_candidate_to_job
from db.repositories import CandidateRepository, JobRepository, MatchRepository, DocumentRepository


def print_section(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def main():
    print_section("SUPABASE CLOUD DATABASE & MEMBER 1/2/3 ALIGNMENT VERIFICATION")

    # 1. Test Supabase Database Connection & Host Details
    db_url = os.getenv("DATABASE_URL")
    print(f"[*] Configured DATABASE_URL target: {db_url.split('@')[-1] if db_url else 'None'}")
    
    sanitized_url = sanitize_database_url(db_url)
    db_engine = create_engine(sanitized_url)

    with db_engine.connect() as conn:
        res = conn.execute(text("SELECT version();")).fetchone()
        print(f"[+] Connected to PostgreSQL Server:\n    {res[0]}")
        
        # Check pgvector extension
        vec_res = conn.execute(text("SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';")).fetchone()
        if vec_res:
            print(f"[+] pgvector Extension Active: version {vec_res[1]}")
        else:
            print("[-] pgvector extension not found!")

    # 2. Inspect Tables in Supabase
    print_section("SUPABASE DATABASE SCHEMAS & TABLES (MEMBER 3 PERSISTENCE)")
    inspector = inspect(db_engine)
    tables = inspector.get_table_names()
    print(f"[*] Total Tables in Supabase Database ({len(tables)} tables found):")
    
    with db_engine.connect() as conn:
        for t in sorted(tables):
            count = conn.execute(text(f"SELECT COUNT(*) FROM {t};")).scalar()
            print(f"    - {t:<28} : {count} records")

    # 3. Verify Member 1 -> Member 2 -> Member 3 End-to-End Alignment
    print_section("MEMBER 1 + MEMBER 2 + MEMBER 3 END-TO-END ALIGNMENT TEST")
    
    # MEMBER 1: Profile Schemas, PII-Safety, Normalization
    print("[1] MEMBER 1 Alignment:")
    cand = CandidateProfile(
        candidate_id="LIVE_TEST_CAND_01",
        name="Supabase Integration Candidate",
        email="test@supabase.io",
        total_experience_months=48,
        skills=[CandidateSkill(raw_skill="PostgreSQL"), CandidateSkill(raw_skill="Python"), CandidateSkill(raw_skill="FastAPI")],
        experiences=[CandidateExperience(role="Senior Backend Developer", duration_months=48, description="Built high-performance APIs with Python, FastAPI, and PostgreSQL pgvector.")]
    )
    print(f"    [+] CandidateProfile validated. Raw skills: {[s.raw_skill for s in cand.skills]}")
    print(f"    [+] PII fields present: {cand.name}, {cand.email}")

    job = JobProfile(
        job_id="LIVE_TEST_JOB_01",
        title="Senior Python Database Engineer",
        domain=["IT"],
        requirements=[
            JobRequirement(requirement_id="REQ_01", description="Experience with Python and FastAPI", category="technical", weight=50.0, mandatory=True, skill="Python", minimum_duration_months=24),
            JobRequirement(requirement_id="REQ_02", description="Experience with PostgreSQL database", category="technical", weight=50.0, mandatory=True, skill="PostgreSQL", minimum_duration_months=24)
        ]
    )
    print(f"    [+] JobProfile validated. Title: '{job.title}', Requirements: {len(job.requirements)}")

    # MEMBER 2: Matching Pipeline, Rules Engine, Evidence Retriever, Scorer
    print("\n[2] MEMBER 2 Alignment:")
    db_session = SessionLocal()
    cand_repo = CandidateRepository(db_session)
    job_repo = JobRepository(db_session)
    match_repo = MatchRepository(db_session)
    doc_repo = DocumentRepository(db_session)

    # Save candidate & job
    cand_repo.save_candidate(cand)
    job_repo.save_job(job)

    # Ingest document text for vector retrieval
    doc_repo.save_document("DOC_LIVE_01", cand.candidate_id, "resume.txt", ".txt", 200, "HASH_LIVE_01", "Built high-performance APIs with Python, FastAPI, and PostgreSQL pgvector.")
    # Add chunk with dummy vector
    dummy_vec = [0.1] * 384
    doc_repo.save_chunks("DOC_LIVE_01", cand.candidate_id, [{
        "content": "Built high-performance APIs with Python, FastAPI, and PostgreSQL pgvector.",
        "page_number": 1,
        "start_char": 0,
        "end_char": 100,
        "section_title": "Summary",
        "embedding": dummy_vec
    }])

    # Run Member 2 Match Pipeline
    match_result = match_candidate_to_job(cand, job, db=db_session)
    print(f"    [+] Match Calculated. Score: {match_result.overall_score:.1f}/100, Status: {match_result.confidence_level}")
    print(f"    [+] Requirement Assessments: {len(match_result.requirement_assessments)} evaluated")
    print(f"    [+] Evidence Coverage: {match_result.evidence_coverage * 100:.0f}%")

    # MEMBER 3: Atomic Persistence to Supabase Cloud PostgreSQL
    print("\n[3] MEMBER 3 Alignment:")
    saved_model = match_repo.save_match_atomic(match_result)
    print(f"    [+] Atomically saved Match to Supabase! (Match ID: {saved_model.match_id}, Job: {saved_model.job_id}, Candidate: {saved_model.candidate_id})")

    # Retrieve match back from Supabase to prove round-trip persistence
    retrieved_match = match_repo.get_match(job.job_id, cand.candidate_id)
    assert retrieved_match is not None
    print(f"    [+] Retrieved Match from Supabase DB! Score: {retrieved_match.overall_score:.1f}, Status: {retrieved_match.overall_status}")
    print(f"    [+] Retrieved Assessments from Supabase: {len(retrieved_match.assessments)}")
    print(f"    [+] Retrieved Agent Logs from Supabase: {len(retrieved_match.agent_logs)}")

    # Clean up test records
    cand_repo.delete_candidate(cand.candidate_id)
    db_session.execute(text("DELETE FROM jobs WHERE job_id = :jid;"), {"jid": job.job_id})
    db_session.commit()
    db_session.close()

    print_section("SUPABASE TEST & MEMBER 1 + 2 + 3 ALIGNMENT SUCCESSFUL!")


if __name__ == "__main__":
    main()
