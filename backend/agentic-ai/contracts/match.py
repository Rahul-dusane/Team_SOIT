"""
match.py
Pydantic contracts for Match Output, Skill Details, Skill Gaps, and Feature Breakdowns.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SkillMatchDetail(BaseModel):
    required_skill: str
    candidate_skill: Optional[str] = None
    match_type: str  # "exact", "equivalent", "transferable", "related", "missing"
    similarity: float = 0.0
    score: float = 0.0


class TransferableGap(BaseModel):
    from_skill: str
    to_skill: str
    confidence: float


class SkillGaps(BaseModel):
    critical: List[str] = Field(default_factory=list)
    moderate: List[str] = Field(default_factory=list)
    optional: List[str] = Field(default_factory=list)
    transferable: List[TransferableGap] = Field(default_factory=list)


class FeatureBreakdown(BaseModel):
    must_have_coverage: float = 0.0
    preferred_coverage: float = 0.0
    experience_fit: float = 0.0
    role_similarity: float = 0.0
    semantic_similarity: float = 0.0
    education_match: float = 0.0
    project_relevance: float = 0.0
    domain_match: float = 0.0


class ScoreBreakdown(BaseModel):
    must_have: float = 0.0
    preferred: float = 0.0
    experience: float = 0.0
    role: float = 0.0
    semantic: float = 0.0
    education: float = 0.0
    projects: float = 0.0
    domain: float = 0.0


class FailedRequirement(BaseModel):
    type: str
    required: Any
    candidate: Any
    message: str


class MatchResult(BaseModel):
    candidate_id: str
    job_id: str
    overall_score: float
    mandatory_pass: bool
    confidence_level: str = "HIGH"  # "HIGH", "MEDIUM", "LOW"
    failed_requirements: List[FailedRequirement] = Field(default_factory=list)
    features: FeatureBreakdown
    score_breakdown: ScoreBreakdown
    skill_matches: List[SkillMatchDetail] = Field(default_factory=list)
    skill_gaps: SkillGaps
