"""
candidate.py
Domain-Independent Validated Pydantic contracts for Candidate Profile and sub-components.
Supports flexible field aliases (e.g. work_history -> experiences, professional_license -> certifications)
to prevent silent data loss across IT, Accounting, Healthcare, Engineering, and other professions.
"""

from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, field_validator, AliasChoices


class CandidateSkill(BaseModel):
    raw_skill: str = Field(..., validation_alias=AliasChoices("raw_skill", "name", "skill", "competency"), min_length=1)
    normalized_skill: Optional[str] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    years_experience: Optional[float] = Field(default=None, ge=0.0)
    evidence: Optional[str] = None
    page: Optional[int] = Field(default=None, ge=1)


class CandidateExperience(BaseModel):
    company: Optional[str] = None
    role: str = Field(..., validation_alias=AliasChoices("role", "title", "position", "job_title"), min_length=1)
    duration_months: int = Field(default=0, ge=0)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = ""

    @field_validator("duration_months", mode="before")
    @classmethod
    def validate_duration(cls, v: Any) -> int:
        if v is None:
            return 0
        try:
            val = int(v)
            return max(0, val)
        except (ValueError, TypeError):
            return 0


class CandidateEducation(BaseModel):
    degree: str = Field(..., validation_alias=AliasChoices("degree", "qualification", "title"), min_length=1)
    field: Optional[str] = None
    institution: Optional[str] = None
    graduation_year: Optional[int] = Field(default=None, ge=1900, le=2100)


class CandidateProject(BaseModel):
    title: str = Field(..., min_length=1)
    description: Optional[str] = ""
    technologies: List[str] = Field(default_factory=list)


class CandidateProfile(BaseModel):
    candidate_id: str = Field(..., min_length=1)
    name: Optional[str] = "Anonymous Candidate"
    email: Optional[str] = None
    phone: Optional[str] = None
    total_experience_months: int = Field(default=0, ge=0)
    skills: List[CandidateSkill] = Field(default_factory=list)
    experiences: List[CandidateExperience] = Field(default_factory=list, validation_alias=AliasChoices("experiences", "work_history", "employment_history"))
    education: List[CandidateEducation] = Field(default_factory=list, validation_alias=AliasChoices("education", "qualifications", "academic_background"))
    projects: List[CandidateProject] = Field(default_factory=list)
    domains: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list, validation_alias=AliasChoices("certifications", "licenses", "professional_license", "credentials"))
    unmapped_fields: Dict[str, Any] = Field(default_factory=dict, description="Preserves unsupported fields for auditability")

    @field_validator("total_experience_months", mode="before")
    @classmethod
    def validate_total_exp(cls, v: Any) -> int:
        if v is None:
            return 0
        try:
            val = int(v)
            return max(0, val)
        except (ValueError, TypeError):
            return 0
