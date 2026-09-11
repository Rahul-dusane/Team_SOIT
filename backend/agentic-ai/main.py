"""
main.py
FastAPI Service Application Entry Point for HireLens.
Exposes production REST API endpoints for resume upload, candidate management, job definition, matching engine execution, candidate ranking, detailed match breakdowns, stats, and Member 1 Agentic AI workflows.
"""

import os
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from contracts.candidate import CandidateProfile
from contracts.job import JobProfile
from contracts.match import MatchResult
from matching.pipeline import match_candidate_to_job
from matching.batch_matcher import match_candidates_to_job
from db.connection import get_db, init_db
from db.repositories import CandidateRepository, JobRepository, MatchRepository, DocumentRepository
from ingestion.pipeline import process_batch_upload, ingest_resume_bytes

# Member 1 Agentic Imports
try:
    from app.agents.resume_agent import extract_candidate_profile
    from app.agents.job_agent import extract_job_profile
    from app.agents.skill_gap_agent import explain_skill_gaps
    from app.agents.evidence_agent import extract_evidence
    from app.agents.recruiter_agent import generate_recruiter_summary
    from app.workflows.graph import run_pipeline
    MEMBER1_AGENTS_AVAILABLE = True
except ImportError:
    MEMBER1_AGENTS_AVAILABLE = False

load_dotenv()

app = FastAPI(
    title="HireLens - Multi-Agent Recruitment Intelligence API",
    description="Production REST API providing durable persistence, resume ingestion, pgvector search, explainable candidate-job matching, and Agentic AI workflows",
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
    return {
        "status": "healthy",
        "service": "HireLens API Backbone",
        "version": "1.0.0",
        "member1_agents": MEMBER1_AGENTS_AVAILABLE
    }


# ---------------------------------------------------------
# MEMBER 3 REST API ENDPOINTS
# ---------------------------------------------------------

@app.post("/api/v1/resumes/upload")
@app.post("/api/v1/upload")
async def upload_resumes(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Multipart Resume File Upload.
    Validates, parses (PDF/DOCX/TXT), chunks, embeds 384-dim vectors, extracts structured candidate profiles, and persists records into DB.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    file_tuples = []
    for file in files:
        content = await file.read()
        file_tuples.append((file.filename, content))

    results = process_batch_upload(file_tuples, db=db)
    return results


@app.get("/api/v1/candidates", response_model=List[Dict[str, Any]])
def list_candidates(db: Session = Depends(get_db)):
    cand_repo = CandidateRepository(db)
    candidates = cand_repo.list_candidates()
    return [c.model_dump() for c in candidates]


@app.get("/api/v1/candidates/{candidate_id}")
def get_candidate_by_id(candidate_id: str, db: Session = Depends(get_db)):
    cand_repo = CandidateRepository(db)
    candidate = cand_repo.get_candidate(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidate '{candidate_id}' not found.")
    return candidate.model_dump()


@app.delete("/api/v1/candidates/{candidate_id}")
def delete_candidate_by_id(candidate_id: str, db: Session = Depends(get_db)):
    cand_repo = CandidateRepository(db)
    success = cand_repo.delete_candidate(candidate_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Candidate '{candidate_id}' not found.")
    return {"status": "success", "message": f"Candidate '{candidate_id}' and all associated documents deleted."}


@app.post("/api/v1/jobs")
def create_or_update_job(job: JobProfile, db: Session = Depends(get_db)):
    job_repo = JobRepository(db)
    job_repo.save_job(job)
    return {"status": "success", "job_id": job.job_id, "title": job.title}


@app.get("/api/v1/jobs", response_model=List[Dict[str, Any]])
def list_jobs(db: Session = Depends(get_db)):
    job_repo = JobRepository(db)
    jobs = job_repo.list_jobs()
    return [j.model_dump() for j in jobs]


@app.get("/api/v1/jobs/{job_id}")
def get_job_by_id(job_id: str, db: Session = Depends(get_db)):
    job_repo = JobRepository(db)
    job = job_repo.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")
    return job.model_dump()


class RunMatchRequest(BaseModel):
    candidate_id: str
    job_id: str


@app.post("/api/v1/matches/run")
def run_candidate_job_match(req: RunMatchRequest, db: Session = Depends(get_db)):
    cand_repo = CandidateRepository(db)
    job_repo = JobRepository(db)
    match_repo = MatchRepository(db)

    candidate = cand_repo.get_candidate(req.candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidate '{req.candidate_id}' not found.")

    job = job_repo.get_job(req.job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{req.job_id}' not found.")

    match_result = match_candidate_to_job(candidate, job, db=db)
    match_model = match_repo.save_match_atomic(match_result)

    return {
        "status": "success",
        "match_id": match_model.match_id,
        "overall_score": match_result.overall_score,
        "overall_status": match_result.confidence_level,
        "decision": match_result.confidence_level,
        "evidence_coverage": match_result.evidence_coverage
    }


@app.get("/api/v1/ranking")
@app.get("/api/v1/matches/{job_id}")
def get_candidate_rankings_for_job(job_id: str, db: Session = Depends(get_db)):
    job_repo = JobRepository(db)
    job = job_repo.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")

    match_repo = MatchRepository(db)
    matches = match_repo.get_rankings_for_job(job_id)

    rankings = []
    for idx, m in enumerate(matches, start=1):
        rankings.append({
            "rank": idx,
            "match_id": m.match_id,
            "candidate_id": m.candidate_id,
            "overall_score": m.overall_score,
            "overall_status": m.overall_status,
            "evidence_coverage": m.evidence_coverage,
            "decision": m.decision
        })

    return {
        "job_id": job_id,
        "job_title": job.title,
        "total_ranked": len(rankings),
        "rankings": rankings
    }


@app.get("/api/v1/matches/{job_id}/{candidate_id}")
def get_match_breakdown(job_id: str, candidate_id: str, db: Session = Depends(get_db)):
    match_repo = MatchRepository(db)
    match_record = match_repo.get_match(job_id, candidate_id)

    if not match_record:
        raise HTTPException(status_code=404, detail=f"Match record for Job '{job_id}' and Candidate '{candidate_id}' not found.")

    return match_record


@app.get("/api/v1/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    cand_repo = CandidateRepository(db)
    job_repo = JobRepository(db)
    cands = cand_repo.list_candidates()
    jobs = job_repo.list_jobs()

    return {
        "total_candidates": len(cands),
        "total_jobs": len(jobs),
        "active_jobs": len(jobs),
        "status": "healthy"
    }


# ---------------------------------------------------------
# MEMBER 1 AGENTIC AI ENDPOINTS
# ---------------------------------------------------------

class ResumeParseRequest(BaseModel):
    candidate_id: str = Field(default="C01", description="Unique ID for candidate")
    text: str = Field(description="Raw text of the resume")


class JobParseRequest(BaseModel):
    job_id: str = Field(default="J01", description="Unique ID for job")
    text: str = Field(description="Raw text of the job description")


class WorkflowRunRequest(BaseModel):
    resumes: Dict[str, str] = Field(description="Dictionary mapping candidate_id to raw resume text")
    jobs: Dict[str, str] = Field(description="Dictionary mapping job_id to raw job description text")


@app.post("/agents/resume")
def parse_resume_endpoint(req: ResumeParseRequest):
    if not MEMBER1_AGENTS_AVAILABLE:
        raise HTTPException(status_code=501, detail="Member 1 agents module not configured.")
    try:
        profile = extract_candidate_profile(req.candidate_id, req.text)
        return {"status": "success", "candidate_id": req.candidate_id, "profile": profile.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/job")
def parse_job_endpoint(req: JobParseRequest):
    if not MEMBER1_AGENTS_AVAILABLE:
        raise HTTPException(status_code=501, detail="Member 1 agents module not configured.")
    try:
        profile = extract_job_profile(req.job_id, req.text)
        return {"status": "success", "job_id": req.job_id, "profile": profile.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


WORKFLOW_STORE: Dict[str, Dict[str, Any]] = {}


@app.post("/workflows/run")
def run_recruitment_workflow_endpoint(req: WorkflowRunRequest):
    if not MEMBER1_AGENTS_AVAILABLE:
        raise HTTPException(status_code=501, detail="Member 1 agents module not configured.")
    if not req.resumes or not req.jobs:
        raise HTTPException(status_code=400, detail="Resumes and jobs are required.")

    try:
        import uuid
        workflow_id = f"wf_{uuid.uuid4().hex[:8]}"
        result = run_pipeline(resume_texts=req.resumes, job_texts=req.jobs)
        response_data = {
            "workflow_id": workflow_id,
            "status": result.get("workflow_status", "COMPLETED"),
            "current_step": result.get("current_step"),
            "candidate_profiles": result.get("candidate_profiles"),
            "job_profiles": result.get("job_profiles"),
            "match_results": result.get("match_results"),
            "skill_gaps": result.get("skill_gaps"),
            "evidence": result.get("evidence"),
            "recruiter_summaries": result.get("recruiter_summaries")
        }
        WORKFLOW_STORE[workflow_id] = response_data
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/workflows/{workflow_id}")
def get_workflow_result_endpoint(workflow_id: str):
    if workflow_id not in WORKFLOW_STORE:
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_id}' not found.")
    return WORKFLOW_STORE[workflow_id]


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
