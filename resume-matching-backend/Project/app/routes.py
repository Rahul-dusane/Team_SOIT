from fastapi import APIRouter, HTTPException

from app.schemas import MatchRequest, MatchResponse
from app.matching.aggregator import compute_overall_match

router = APIRouter()


@router.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}


@router.post("/api/match", response_model=MatchResponse, tags=["matching"])
def match_resume_to_job(payload: MatchRequest):
    if not payload.resume_text.strip() or not payload.job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="Both 'resume_text' and 'job_description' must be non-empty.",
        )

    result = compute_overall_match(
        resume_text=payload.resume_text,
        job_text=payload.job_description,
        job_title=payload.job_title,
    )
    return result
