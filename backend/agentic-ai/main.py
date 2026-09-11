"""
main.py
FastAPI application entry point exposing candidate matching and batch evaluation endpoints.
"""

from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any
from contracts.candidate import CandidateProfile
from contracts.job import JobProfile
from contracts.match import MatchResult
from matching.pipeline import match_candidate_to_job
from matching.batch_matcher import match_candidates_to_job, match_all
from matching.evaluation import evaluate_batch_results

app = FastAPI(
    title="HireLens - Multi-Agent Recruitment Intelligence API",
    description="Explainable candidate-job matching and quantitative evaluation engine",
    version="1.0.0"
)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "HireLens Matching Engine"}


@app.post("/api/v1/matches/run", response_model=MatchResult)
def run_match(candidate: CandidateProfile, job: JobProfile):
    try:
        result = match_candidate_to_job(candidate, job)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/matches/batch-job")
def run_batch_job(candidates: List[CandidateProfile], job: JobProfile):
    try:
        return match_candidates_to_job(candidates, job)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
