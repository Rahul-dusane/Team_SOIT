"""
candidate.py
Domain-Independent Validated Pydantic contracts for Candidate Profile and sub-components.
Supports flexible field aliases and captures unsupported extra fields into unmapped_fields for auditability.
"""

from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, field_validator, model_validator, AliasChoices

KNOWN_CANDIDATE_FIELDS = {
    "candidate_id", "name", "email", "phone", "total_experience_months",
    "skills", "experiences", "work_history", "employment_history",
    "education", "qualifications", "academic_background",
    "projects", "domains", "certifications", "licenses", "credentials",
    "unmapped_fields"
}


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
    certifications: List[str] = Field(default_factory=list, validation_alias=AliasChoices("certifications", "licenses", "credentials"))
    unmapped_fields: Dict[str, Any] = Field(default_factory=dict, description="Preserves unsupported fields for auditability")

    @field_validator("certifications", mode="before")
    @classmethod
    def validate_certifications(cls, v: Any) -> List[str]:
        if v is None:
            return []
        if isinstance(v, str):
            return [v]
        if isinstance(v, list):
            return [str(x) for x in v if x is not None]
        return []

    @model_validator(mode="before")
    @classmethod
    def capture_unmapped_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            extra = {}
            for k, v in data.items():
                if k not in KNOWN_CANDIDATE_FIELDS:
                    extra[k] = v
            if extra:
                existing_unmapped = data.get("unmapped_fields", {})
                if isinstance(existing_unmapped, dict):
                    existing_unmapped.update(extra)
                    data["unmapped_fields"] = existing_unmapped
                else:
                    data["unmapped_fields"] = extra
        return data

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
