"""Matching contract schemas defining integration with Member 2's Matching Engine."""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class ScoreBreakdown(BaseModel):
    skills: float = Field(default=0.0, description="Skill overlap score component")
    experience: float = Field(default=0.0, description="Experience tenure score component")
    semantic: float = Field(default=0.0, description="Semantic / vector similarity score component")
    domain: Optional[float] = Field(default=0.0, description="Domain match score component")


class MatchResult(BaseModel):
    candidate_id: str = Field(description="Candidate identifier (e.g. C01)")
    job_id: str = Field(description="Job identifier (e.g. J01)")
    overall_score: float = Field(ge=0.0, le=100.0, description="Calculated matching score (0-100%)")
    mandatory_pass: bool = Field(description="True if candidate meets all MUST_HAVE criteria")
    breakdown: ScoreBreakdown = Field(description="Score breakdown by category")
    gaps: List[str] = Field(default_factory=list, description="List of missing skills/requirements")
    matched_skills: List[str] = Field(default_factory=list, description="List of satisfied skills")

