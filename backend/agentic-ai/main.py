"""
main.py
FastAPI Service Application Entry Point for HireLens.
Exposes production REST API endpoints for resume upload, candidate management, job definition, matching engine execution, candidate ranking, detailed match breakdowns, stats, and Member 1 Agentic AI workflows.
"""

import sys
import os
import uuid

# Prevent OpenBLAS memory allocation failures on Windows multi-threaded reloaders
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

# Automatically add backend/agentic-ai directory to sys.path so modules can be imported directly
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

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

from db.connection import get_db, init_db, check_db_health

from fastapi.security import APIKeyHeader
from fastapi import Request, Security
import time
import logging

logger = logging.getLogger("hirelens.monitoring")

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

from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from datetime import datetime, timezone

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "error_code": f"HTTP_{exc.status_code}",
            "detail": exc.detail,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "error_code": "VALIDATION_ERROR",
            "detail": "Invalid request payload or query parameters.",
            "errors": [str(e) for e in exc.errors()],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Server Error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error_code": "INTERNAL_SERVER_ERROR",
            "detail": f"Internal server error: {str(exc)}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )



@app.middleware("http")
async def telemetry_middleware(request: Request, call_next):
    """Production Telemetry Middleware: assigns X-Request-ID and tracks execution latency in ms."""
    request_id = request.headers.get("X-Request-ID") or f"req_{uuid.uuid4().hex[:8]}"
    start_time = time.time()
    
    response = await call_next(request)
    
    duration_ms = round((time.time() - start_time) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time-ms"] = str(duration_ms)
    
    logger.info(f"[{request_id}] {request.method} {request.url.path} - {response.status_code} ({duration_ms}ms)")
    return response


api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: Optional[str] = Security(api_key_header)):
    """Production Auth Dependency: verifies X-API-Key header when configured in production."""
    expected_key = os.getenv("API_KEY")
    if not expected_key or os.getenv("TESTING") == "true":
        return True
    if api_key and api_key == expected_key:
        return True
    raise HTTPException(
        status_code=401,
        detail="Unauthorized: Invalid or missing X-API-Key header."
    )


@app.on_event("startup")
def startup_event():
    try:
        init_db()
    except Exception as e:
        print(f"[Warning] DB initialization failed: {e}")


@app.get("/health")
@app.get("/api/v1/health")
def health_check(db: Session = Depends(get_db)):
    """Production Health Check with live DB connectivity, LLM provider status, and system metrics."""
    db_status = check_db_health(db)
    is_healthy = db_status.get("status") == "connected"
    
    cand_repo = CandidateRepository(db)
    job_repo = JobRepository(db)
    
    total_candidates = len(cand_repo.list_candidates())
    total_jobs = len(job_repo.list_jobs())
    
    llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()
    has_gemini = bool(os.getenv("GEMINI_API_KEY") and not os.getenv("GEMINI_API_KEY").startswith("your_"))
    
    return {
        "status": "ok" if is_healthy else "degraded",
        "service": "HireLens Recruitment Intelligence Backbone",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "database": db_status,
        "llm_provider": {
            "configured_provider": llm_provider,
            "gemini_active": has_gemini,
            "member1_agents": MEMBER1_AGENTS_AVAILABLE
        },
        "metrics": {
            "total_candidates": total_candidates,
            "total_jobs": total_jobs
        }
    }


# ---------------------------------------------------------
# MEMBER 3 REST API ENDPOINTS
# ---------------------------------------------------------

@app.post("/api/v1/resumes/upload")
@app.post("/api/v1/upload")
async def upload_resumes(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    auth: bool = Depends(verify_api_key)
):
    """
    Multipart Resume File Upload.
    Validates, parses (PDF/DOCX/TXT), chunks, embeds 384-dim vectors, extracts structured candidate profiles, and persists records into DB.
    Requires authentication when API_KEY is set.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    allowed_exts = {".pdf", ".docx", ".txt"}
    file_tuples = []
    for file in files:
        filename = file.filename or "uploaded_resume.txt"
        ext = os.path.splitext(filename)[1].lower()
        if ext not in allowed_exts:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type '{ext}' for file '{filename}'. Only PDF, DOCX, and TXT files are allowed."
            )
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"File '{filename}' exceeds maximum allowed size limit of 10 MB."
            )
        file_tuples.append((filename, content))

    results = process_batch_upload(db=db, files=file_tuples)
    return results


@app.get("/api/v1/candidates", response_model=List[Dict[str, Any]])
def list_candidates(db: Session = Depends(get_db), auth: bool = Depends(verify_api_key)):
    cand_repo = CandidateRepository(db)
    candidates = cand_repo.list_candidates()
    return [c.model_dump() for c in candidates]


@app.get("/api/v1/candidates/{candidate_id}")
def get_candidate_by_id(candidate_id: str, db: Session = Depends(get_db), auth: bool = Depends(verify_api_key)):
    cand_repo = CandidateRepository(db)
    candidate = cand_repo.get_candidate(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidate '{candidate_id}' not found.")
    return candidate.model_dump()


@app.delete("/api/v1/candidates/{candidate_id}")
def delete_candidate_by_id(candidate_id: str, db: Session = Depends(get_db), auth: bool = Depends(verify_api_key)):
    cand_repo = CandidateRepository(db)
    success = cand_repo.delete_candidate(candidate_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Candidate '{candidate_id}' not found.")
    return {"status": "success", "message": f"Candidate '{candidate_id}' and all associated documents deleted."}


@app.post("/api/v1/jobs")
def create_or_update_job(job: JobProfile, db: Session = Depends(get_db), auth: bool = Depends(verify_api_key)):
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
    candidate_id: Optional[str] = None
    job_id: Optional[str] = None
    candidate: Optional[CandidateProfile] = None
    job: Optional[JobProfile] = None


@app.post("/api/v1/matches/run")
def run_candidate_job_match(req: RunMatchRequest, db: Session = Depends(get_db)):
    cand_repo = CandidateRepository(db)
    job_repo = JobRepository(db)
    match_repo = MatchRepository(db)

    candidate = req.candidate
    if not candidate and req.candidate_id:
        candidate = cand_repo.get_candidate(req.candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found or not provided.")

    job = req.job
    if not job and req.job_id:
        job = job_repo.get_job(req.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or not provided.")

    match_result = match_candidate_to_job(candidate, job, db=db)
    try:
        match_model = match_repo.save_match_atomic(match_result)
        match_id = match_model.match_id
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database persistence failed: {e}")

    return {
        "status": "success",
        "match_id": match_id,
        "candidate_id": candidate.candidate_id,
        "job_id": job.job_id,
        "overall_score": match_result.overall_score,
        "overall_status": match_result.confidence_level,
        "decision": match_result.confidence_level,
        "evidence_coverage": match_result.evidence_coverage
    }


@app.get("/api/v1/ranking")
@app.get("/api/v1/ranking/{job_id}")
def get_candidate_rankings_for_job(job_id: Optional[str] = None, db: Session = Depends(get_db)):
    job_repo = JobRepository(db)
    job = None
    if job_id:
        job = job_repo.get_job(job_id)
    else:
        all_jobs = job_repo.list_jobs()
        if all_jobs:
            job = all_jobs[0]
            job_id = job.job_id

    if not job:
        return {
            "job_id": job_id or "NONE",
            "job_title": "No Job Selected",
            "total_candidates": 0,
            "total_ranked": 0,
            "rankings": []
        }

    match_repo = MatchRepository(db)
    matches = match_repo.get_rankings_for_job(job.job_id)

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
        "total_candidates": len(rankings),
        "total_ranked": len(rankings),
        "rankings": rankings
    }


@app.get("/api/v1/matches/{job_id}/{candidate_id}")
@app.get("/api/v1/matches/{match_id}")
def get_match_breakdown(job_id: str, candidate_id: Optional[str] = None, match_id: Optional[str] = None, db: Session = Depends(get_db)):
    match_repo = MatchRepository(db)
    match_record = None

    if candidate_id:
        match_record = match_repo.get_match(job_id, candidate_id)
    else:
        # job_id param was passed as single match_id
        from db.models import MatchModel
        match_record = db.query(MatchModel).filter(MatchModel.match_id == job_id).first()

    if not match_record:
        raise HTTPException(status_code=404, detail="Match record not found.")

    assessments = [
        {
            "requirement_id": a.requirement_id,
            "description": a.requirement_description,
            "status": a.status,
            "weight": a.weight,
            "earned_score": a.earned_score,
            "max_score": a.max_score,
            "score_ratio": a.score_ratio
        } for a in (match_record.assessments or [])
    ]
    summary = {
        "summary_text": match_record.summary.summary_text if match_record.summary else "",
        "key_strengths": match_record.summary.key_strengths if match_record.summary else [],
        "key_gaps": match_record.summary.key_gaps if match_record.summary else [],
        "recommendation": match_record.summary.recommendation if match_record.summary else ""
    } if match_record.summary else {}

    agent_logs = [
        {
            "agent_name": l.agent_name,
            "step_index": l.step_index,
            "status": l.status,
            "duration_ms": l.duration_ms
        } for l in (match_record.agent_logs or [])
    ]

    return {
        "match_id": match_record.match_id,
        "job_id": match_record.job_id,
        "candidate_id": match_record.candidate_id,
        "overall_score": match_record.overall_score,
        "overall_status": match_record.overall_status,
        "decision": match_record.decision,
        "evidence_coverage": match_record.evidence_coverage,
        "raw_score_breakdown": match_record.raw_score_breakdown,
        "uncertainty_flags": match_record.uncertainty_flags,
        "assessments": assessments,
        "summary": summary,
        "agent_logs": agent_logs
    }


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
def parse_resume_endpoint(req: ResumeParseRequest, db: Session = Depends(get_db)):
    if not MEMBER1_AGENTS_AVAILABLE:
        raise HTTPException(status_code=501, detail="Member 1 agents module not configured.")
    try:
        profile = extract_candidate_profile(req.candidate_id, req.text)
        cand_repo = CandidateRepository(db)
        cand_repo.save_candidate(profile)
        return {"status": "success", "candidate_id": req.candidate_id, "profile": profile.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/job")
def parse_job_endpoint(req: JobParseRequest, db: Session = Depends(get_db)):
    if not MEMBER1_AGENTS_AVAILABLE:
        raise HTTPException(status_code=501, detail="Member 1 agents module not configured.")
    try:
        profile = extract_job_profile(req.job_id, req.text)
        job_repo = JobRepository(db)
        job_repo.save_job(profile)
        return {"status": "success", "job_id": req.job_id, "profile": profile.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


WORKFLOW_STORE: Dict[str, Dict[str, Any]] = {}


@app.post("/workflows/run")
def run_recruitment_workflow_endpoint(req: WorkflowRunRequest, db: Session = Depends(get_db)):
    if not MEMBER1_AGENTS_AVAILABLE:
        raise HTTPException(status_code=501, detail="Member 1 agents module not configured.")
    if not req.resumes or not req.jobs:
        raise HTTPException(status_code=400, detail="Resumes and jobs are required.")

    try:
        import uuid
        workflow_id = f"wf_{uuid.uuid4().hex[:8]}"
        result = run_pipeline(resume_texts=req.resumes, job_texts=req.jobs)

        cand_repo = CandidateRepository(db)
        job_repo = JobRepository(db)
        match_repo = MatchRepository(db)

        # Durable Database Persistence of Candidate Profiles
        for cid, c_data in (result.get("candidate_profiles") or {}).items():
            try:
                c_obj = CandidateProfile.model_validate(c_data)
                cand_repo.save_candidate(c_obj)
            except Exception:
                pass

        # Durable Database Persistence of Job Profiles
        for jid, j_data in (result.get("job_profiles") or {}).items():
            try:
                j_obj = JobProfile.model_validate(j_data)
                job_repo.save_job(j_obj)
            except Exception:
                pass

        # Durable Database Persistence of Matches & Assessments
        for m_data in (result.get("match_results") or {}):
            try:
                m_obj = MatchResult.model_validate(m_data)
                pair_key = f"{m_obj.candidate_id}_{m_obj.job_id}"
                summary_data = (result.get("recruiter_summaries") or {}).get(pair_key, {})
                summary_text = summary_data.get("summary", "")
                strengths = summary_data.get("strengths", [])
                concerns = summary_data.get("concerns", [])
                recommendation = summary_data.get("recommendation", "")

                match_repo.save_match_atomic(
                    match_result=m_obj,
                    summary_text=summary_text,
                    key_strengths=strengths,
                    key_gaps=concerns,
                    recommendation=recommendation
                )
            except Exception:
                pass

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
