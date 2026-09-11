"""
main.py
FastAPI Service Application Entry Point for HireLens.
Exposes production REST API endpoints for resume upload, candidate management, job definition, matching engine execution, candidate ranking, detailed match breakdowns, and agent logs.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from contracts.candidate import CandidateProfile
from contracts.job import JobProfile
from contracts.match import MatchResult
from matching.pipeline import match_candidate_to_job
from matching.batch_matcher import match_candidates_to_job
from db.connection import get_db, init_db
from db.repositories import CandidateRepository, JobRepository, MatchRepository, DocumentRepository
from ingestion.pipeline import process_batch_upload, ingest_resume_bytes

app = FastAPI(
    title="HireLens - Multi-Agent Recruitment Intelligence API",
    description="Production REST API providing durable persistence, resume ingestion, pgvector search, and explainable candidate-job matching",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    try:
        init_db()
    except Exception as e:
        print(f"[Warning] DB initialization failed: {e}")


@app.get("/health")
@app.get("/api/v1/health")
def health_check():
    return {"status": "ok", "service": "HireLens API Backbone", "version": "1.0.0"}


# --- RESUME INGESTION & UPLOAD ENDPOINTS ---

@app.post("/api/v1/resumes/upload")
@app.post("/api/v1/upload")
async def upload_resumes(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Multipart Resume File Upload.
    Validates, parses (PDF/DOCX/TXT), chunks, embeds 384-dim vectors, extracts structured candidate profiles, and persists records into PostgreSQL/DB.
    Supports partial batch upload failures.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    file_tuples = []
    for file in files:
        content = await file.read()
        file_tuples.append((file.filename, content))

    batch_summary = process_batch_upload(db, file_tuples)
    return batch_summary


# --- CANDIDATE MANAGEMENT ENDPOINTS ---

@app.get("/api/v1/candidates")
def list_candidates(db: Session = Depends(get_db)):
    repo = CandidateRepository(db)
    cands = repo.list_candidates()
    return [c.model_dump() for c in cands]


@app.get("/api/v1/candidates/{candidate_id}")
def get_candidate(candidate_id: str, db: Session = Depends(get_db)):
    repo = CandidateRepository(db)
    cand = repo.get_candidate(candidate_id)
    if not cand:
        raise HTTPException(status_code=404, detail=f"Candidate '{candidate_id}' not found.")
    return cand.model_dump()


@app.delete("/api/v1/candidates/{candidate_id}")
def delete_candidate(candidate_id: str, db: Session = Depends(get_db)):
    """Cascade deletes candidate and associated documents, chunks, vectors, matches, assessments, and logs."""
    repo = CandidateRepository(db)
    success = repo.delete_candidate(candidate_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Candidate '{candidate_id}' not found.")
    return {"status": "success", "message": f"Candidate '{candidate_id}' and all associated records purged."}


# --- JOB MANAGEMENT ENDPOINTS ---

@app.post("/api/v1/jobs")
def create_job(job: JobProfile, db: Session = Depends(get_db)):
    repo = JobRepository(db)
    job_model = repo.save_job(job)
    return {"status": "success", "job_id": job_model.job_id, "job": job.model_dump()}


@app.get("/api/v1/jobs")
def list_jobs(db: Session = Depends(get_db)):
    repo = JobRepository(db)
    jobs = repo.list_jobs()
    return [j.model_dump() for j in jobs]


@app.get("/api/v1/jobs/{job_id}")
def get_job(job_id: str, db: Session = Depends(get_db)):
    repo = JobRepository(db)
    job = repo.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")
    return job.model_dump()


# --- MATCHING ENGINE & PERSISTENCE ENDPOINTS ---

from pydantic import BaseModel

class MatchRunRequest(BaseModel):
    candidate: CandidateProfile
    job: JobProfile


@app.post("/api/v1/matches/run", response_model=MatchResult)
def run_match_endpoint(req: MatchRunRequest, db: Session = Depends(get_db)):
    """
    Executes Member 2 Matching Engine and ATOMICALLY persists match results, requirement assessments, evidence items, skill gaps, recruiter summaries, and agent run logs.
    """
    try:
        candidate = req.candidate
        job = req.job
        cand_repo = CandidateRepository(db)
        job_repo = JobRepository(db)
        match_repo = MatchRepository(db)

        # Ensure candidate and job exist in DB
        cand_repo.save_candidate(candidate)
        job_repo.save_job(job)

        # Run pipeline
        result = match_candidate_to_job(candidate, job, db=db)

        # Atomic persistence inside single transaction
        match_repo.save_match_atomic(
            match_result=result,
            summary_text=f"Match evaluation completed for {candidate.name} against {job.title}. Score: {result.overall_score}/100. Status: {result.confidence_level}.",
            recommendation=result.confidence_level
        )

        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/ranking")
@app.get("/api/v1/matches/{job_id}")
def get_candidate_rankings(job_id: str, db: Session = Depends(get_db)):
    """Retrieves ranked candidates for a specific job from persisted database records."""
    match_repo = MatchRepository(db)
    cand_repo = CandidateRepository(db)
    job_repo = JobRepository(db)

    job = job_repo.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")

    matches = match_repo.get_rankings_for_job(job_id)
    rankings = []
    for rank_idx, m in enumerate(matches, 1):
        cand = cand_repo.get_candidate(m.candidate_id)
        rankings.append({
            "rank": rank_idx,
            "candidate_id": m.candidate_id,
            "name": cand.name if cand else "Unknown",
            "score": round(m.overall_score, 1),
            "status": m.overall_status,
            "decision": m.decision,
            "evidence_coverage": round(m.evidence_coverage or 0.0, 2),
            "breakdown": m.raw_score_breakdown,
            "uncertainty_flags": m.uncertainty_flags or []
        })

    return {"job_id": job_id, "total_candidates": len(rankings), "rankings": rankings}


@app.get("/api/v1/matches/{job_id}/{candidate_id}")
def get_detailed_match(job_id: str, candidate_id: str, db: Session = Depends(get_db)):
    """Retrieves complete match details, requirement assessments, evidence passages, gaps, summary, and agent run logs."""
    match_repo = MatchRepository(db)
    m = match_repo.get_match(job_id, candidate_id)
    if not m:
        raise HTTPException(status_code=404, detail=f"Match record for job '{job_id}' and candidate '{candidate_id}' not found.")

    return {
        "match_id": m.match_id,
        "job_id": m.job_id,
        "candidate_id": m.candidate_id,
        "overall_score": round(m.overall_score, 1),
        "raw_score": round(m.raw_score, 1),
        "overall_status": m.overall_status,
        "decision": m.decision,
        "evidence_coverage": m.evidence_coverage,
        "raw_score_breakdown": m.raw_score_breakdown,
        "uncertainty_flags": m.uncertainty_flags or [],
        "embedding_model": m.embedding_model,
        "scoring_policy_version": m.scoring_policy_version,
        "assessments": [
            {
                "requirement_id": a.requirement_id,
                "description": a.requirement_description,
                "category": a.req_category,
                "importance": a.req_importance,
                "evidence_passage": a.evidence_passage,
                "source_page": a.source_page,
                "confidence": a.evidence_confidence,
                "status": a.status,
                "earned_score": a.earned_score,
                "max_score": a.max_score
            } for a in m.assessments
        ],
        "evidence_items": [
            {
                "requirement_id": e.requirement_id,
                "skill": e.candidate_skill,
                "matched_text": e.matched_text,
                "evidence_passage": e.evidence_passage,
                "page_number": e.page_number,
                "confidence": e.confidence
            } for e in m.evidence_items
        ],
        "gaps": [
            {
                "skill": g.skill,
                "type": g.gap_type,
                "impact": g.impact,
                "severity": g.severity,
                "mitigations": g.mitigations
            } for g in m.gaps
        ],
        "summary": {
            "summary_text": m.summary.summary_text if m.summary else "",
            "key_strengths": m.summary.key_strengths if m.summary else [],
            "key_gaps": m.summary.key_gaps if m.summary else [],
            "recommendation": m.summary.recommendation if m.summary else m.decision
        } if m.summary else None,
        "agent_logs": [
            {
                "agent_name": l.agent_name,
                "step_index": l.step_index,
                "status": l.status,
                "input_summary": l.input_summary,
                "output_summary": l.output_summary,
                "duration_ms": l.duration_ms
            } for l in m.agent_logs
        ]
    }


@app.get("/api/v1/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Provides summary dashboard statistics."""
    cand_repo = CandidateRepository(db)
    job_repo = JobRepository(db)
    cands = cand_repo.list_candidates()
    jobs = job_repo.list_jobs()

    return {
        "total_candidates": len(cands),
        "total_jobs": len(jobs),
        "active_jobs": len([j for j in jobs if j.status == "Active"]),
        "status": "healthy"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
