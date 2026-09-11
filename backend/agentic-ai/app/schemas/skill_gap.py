"""Skill gap analysis schema for Skill Gap Agent."""

from typing import List, Optional
from pydantic import BaseModel, Field


class TransferableSkill(BaseModel):
    candidate_skill: str = Field(description="Skill the candidate possesses (e.g. AWS, Azure, Express)")
    target_skill: str = Field(description="Missing target skill required by job (e.g. GCP, FastAPI)")
    relevance_rationale: str = Field(description="Why this skill provides a strong transferable foundation")


class SkillGapAnalysis(BaseModel):
    candidate_id: str
    job_id: str
    critical_gaps: List[str] = Field(
        default_factory=list,
        description="Missing MUST-HAVE skills that directly impact role viability"
    )
    moderate_gaps: List[str] = Field(
        default_factory=list,
        description="Missing PREFERRED skills that are helpful but not disqualifying"
    )
    transferable_skills: List[TransferableSkill] = Field(
        default_factory=list,
        description="Candidate skills that can bridge missing requirements"
    )
    upskilling_recommendations: List[str] = Field(
        default_factory=list,
        description="Estimated training or ramp-up areas needed for the candidate"
    )
    gap_summary: str = Field(
        description="Concise 1-2 sentence executive summary of the gap analysis"
    )

