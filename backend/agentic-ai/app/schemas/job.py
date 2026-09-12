"""Job profile schemas for Job Agent extraction."""

from typing import List, Literal
from pydantic import BaseModel, Field


class JobRequirement(BaseModel):
    requirement: str = Field(description="Normalized skill or requirement description")
    requirement_type: Literal["MUST_HAVE", "PREFERRED"] = Field(
        description="Whether this requirement is mandatory or optional"
    )
    importance: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"] = Field(
        default="HIGH",
        description="Relative importance level"
    )
    weight: float = Field(
        default=5.0,
        ge=1.0,
        le=10.0,
        description="Numeric weight on a 1.0 to 10.0 scale for Member 2's matching engine"
    )


class JobProfile(BaseModel):
    job_id: str = Field(description="Unique identifier for the job (e.g. J01)")
    title: str = Field(description="Job title / role name")
    
    requirements: List[JobRequirement] = Field(
        default_factory=list,
        description="List of weighted job requirements"
    )
    must_have_skills: List[str] = Field(
        default_factory=list,
        description="List of non-negotiable required skills"
    )
    preferred_skills: List[str] = Field(
        default_factory=list,
        description="List of nice-to-have skills"
    )
    min_experience_months: int = Field(
        default=0,
        ge=0,
        description="Minimum total work experience required in months"
    )
    education_requirements: List[str] = Field(
        default_factory=list,
        description="Degrees or education levels required"
    )
    responsibilities: List[str] = Field(
        default_factory=list,
        description="Key day-to-day responsibilities"
    )
    domain: List[str] = Field(
        default_factory=list,
        description="Target industry or domain (e.g. Backend, Cloud, Data Engineering)"
    )

