"""
match.py
Domain-Independent Pydantic contracts for Requirement Assessment, Skill Details, Skill Gaps, and Match Outputs.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SkillMatchDetail(BaseModel):
    required_skill: str
    candidate_skill: Optional[str] = None
    match_type: str  # "exact", "equivalent", "transferable", "related", "missing"
    similarity: float = 0.0
    score: float = 0.0


class RequirementAssessment(BaseModel):
    requirement_id: Optional[str] = None
    description: str = ""
    category: str = "competency"  # "competency", "qualification", "certification", "experience_duration", "responsibility"
    mandatory: bool = False
    weight: float = 10.0
    status: str = "unknown"  # "satisfied" (1.0), "partially_supported" (0.5), "contradicted" (0.0), "unknown" (0.0)
    confidence: float = 1.0
    evidence_text: Optional[str] = None
    evidence_page: Optional[int] = None
    score_contribution: float = 0.0


class EvidenceItem(BaseModel):
    requirement_id: Optional[str] = None
    candidate_skill: Optional[str] = None
    matched_text: Optional[str] = None
    evidence_passage: Optional[str] = None
    page_number: Optional[int] = None
    confidence: float = 1.0


class Gap(BaseModel):
    skill: str
    gap_type: str = "optional"  # "critical", "moderate", "optional", "transferable"
    impact: Optional[str] = "Low"
    severity: Optional[str] = "minor"
    mitigations: List[str] = Field(default_factory=list)


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
    raw_score: float = 0.0                      # Unadjusted raw score sum (0.0 to 100.0)
    overall_score: float = 0.0                  # Post-policy final score (0.0 if rejected)
    evidence_coverage: float = 0.0              # % of job requirements with supporting candidate evidence (0.0 to 1.0)
    mandatory_pass: bool = True
    confidence_level: str = "HIGH"              # "HIGH", "MEDIUM", "LOW (Needs Review)", "REJECTED (Mandatory Failed)"
    uncertainty_flags: List[str] = Field(default_factory=list)
    failed_requirements: List[FailedRequirement] = Field(default_factory=list)
    requirement_assessments: List[RequirementAssessment] = Field(default_factory=list)
    evidence_items: List[EvidenceItem] = Field(default_factory=list)
    gaps: List[Gap] = Field(default_factory=list)
    features: FeatureBreakdown = Field(default_factory=FeatureBreakdown)
    raw_score_breakdown: ScoreBreakdown = Field(default_factory=ScoreBreakdown)
    score_breakdown: ScoreBreakdown = Field(default_factory=ScoreBreakdown)
    skill_matches: List[SkillMatchDetail] = Field(default_factory=list)
    skill_gaps: SkillGaps = Field(default_factory=SkillGaps)
