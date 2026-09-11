"""Recruiter synthesis schema for Recruiter Agent."""

from typing import List, Literal
from pydantic import BaseModel, Field


class RecruiterSummary(BaseModel):
    candidate_id: str
    job_id: str
    overall_score: float = Field(description="Deterministic score forwarded from matching engine")
    recommendation: Literal["STRONG_MATCH", "POTENTIAL_MATCH", "WEAK_MATCH", "DO_NOT_PROCEED"] = Field(
        description="Categorical hiring recommendation"
    )
    headline: str = Field(description="One-sentence executive summary headline for the recruiter")
    summary: str = Field(default="", description="Detailed executive summary of candidate suitability")
    strengths: List[str] = Field(
        default_factory=list,
        description="Top 3-5 confirmed strengths matching the job requirements"
    )
    concerns: List[str] = Field(
        default_factory=list,
        description="Identified risks, missing skills, or experience deficits"
    )
    interview_focus: List[str] = Field(
        default_factory=list,
        description="Targeted technical and domain questions recommended for the interviewer"
    )
    suggested_role_level: str = Field(
        default="Mid-Level",
        description="Assessed seniority match (e.g. Junior, Mid, Senior, Lead)"
    )

