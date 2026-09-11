"""FastAPI Server exposing Member 1's Agentic AI Subsystem."""

import os
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from app.agents.resume_agent import extract_candidate_profile
from app.agents.job_agent import extract_job_profile
from app.agents.skill_gap_agent import explain_skill_gaps
from app.agents.evidence_agent import extract_evidence
from app.agents.recruiter_agent import generate_recruiter_summary
from app.workflows.graph import run_pipeline

load_dotenv()

app = FastAPI(
    title="AI Recruitment Brain (Member 1)",
    description="Agentic LLM Extraction, Skill Gap Reasoning, Evidence Auditing, and LangGraph Pipeline Orchestration",
    version="1.0.0"
)

# Enable CORS for Member 4's Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Request / Response Schemas
# ---------------------------------------------------------

class ResumeParseRequest(BaseModel):
    candidate_id: str = Field(default="C01", description="Unique ID for candidate")
    text: str = Field(description="Raw text of the resume")


class JobParseRequest(BaseModel):
    job_id: str = Field(default="J01", description="Unique ID for job")
    text: str = Field(description="Raw text of the job description")


class WorkflowRunRequest(BaseModel):
    resumes: Dict[str, str] = Field(
        description="Dictionary mapping candidate_id to raw resume text"
    )
    jobs: Dict[str, str] = Field(
        description="Dictionary mapping job_id to raw job description text"
    )


# ---------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------

@app.get("/health")
def health_check():
    """Health check endpoint for frontend and orchestration monitoring."""
    provider = os.getenv("LLM_PROVIDER", "openai")
    return {
        "status": "healthy",
        "member": "Member 1 — Agentic AI / LLM Lead",
        "provider": provider
    }


@app.post("/agents/resume")
def parse_resume(req: ResumeParseRequest):
    """
    Resume Agent Endpoint:
    Accepts raw resume text and returns validated CandidateProfile JSON.
    """
    try:
        profile = extract_candidate_profile(req.candidate_id, req.text)
        return {
            "status": "success",
            "candidate_id": req.candidate_id,
            "profile": profile.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/job")
def parse_job(req: JobParseRequest):
    """
    Job Agent Endpoint:
    Accepts raw JD text and returns machine-readable JobProfile with requirement weights.
    """
    try:
        profile = extract_job_profile(req.job_id, req.text)
        return {
            "status": "success",
            "job_id": req.job_id,
            "profile": profile.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


WORKFLOW_STORE: Dict[str, Dict[str, Any]] = {}


@app.post("/workflows/run")
def run_recruitment_workflow(req: WorkflowRunRequest):
    """
    LangGraph Workflow Execution Endpoint:
    Processes batch resumes against batch job specifications through the multi-agent graph.
    """
    if not req.resumes:
        raise HTTPException(status_code=400, detail="At least one resume must be provided.")
    if not req.jobs:
        raise HTTPException(status_code=400, detail="At least one job description must be provided.")

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
def get_workflow_result(workflow_id: str):
    """Retrieve the full results of a specific workflow execution."""
    if workflow_id not in WORKFLOW_STORE:
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_id}' not found.")
    return WORKFLOW_STORE[workflow_id]


@app.get("/workflows/{workflow_id}/status")
def get_workflow_status(workflow_id: str):
    """Retrieve current status and step of a specific workflow execution."""
    if workflow_id not in WORKFLOW_STORE:
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_id}' not found.")
    wf = WORKFLOW_STORE[workflow_id]
    return {
        "workflow_id": workflow_id,
        "status": wf.get("status"),
        "current_step": wf.get("current_step")
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

