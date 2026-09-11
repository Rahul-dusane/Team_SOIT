"""
job.py
Domain-Independent Validated Pydantic contracts for Job Requirement and Job Profile.
Supports arbitrary domain requirements (competency, qualification, certification, experience_duration, responsibility).
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class JobRequirement(BaseModel):
    requirement_id: Optional[str] = None
    description: Optional[str] = Field(default=None, description="Arbitrary requirement text, e.g. 'Manage monthly financial close' or 'Build REST APIs'")
    skill: Optional[str] = None  # Secondary canonical representation if applicable
    category: str = Field(default="competency")  # "competency", "qualification", "certification", "experience_duration", "responsibility"
    importance: str = Field(default="must_have")  # "must_have", "preferred", "nice_to_have"
    mandatory: bool = Field(default=False)
    weight: float = Field(default=10.0, ge=0.0)
    minimum_duration_months: int = Field(default=0, ge=0)

    @field_validator("importance")
    @classmethod
    def validate_importance(cls, v: str) -> str:
        valid_types = {"must_have", "preferred", "nice_to_have"}
        if v not in valid_types:
            raise ValueError(f"importance must be one of {valid_types}, got '{v}'")
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        valid_cats = {"competency", "qualification", "certification", "experience_duration", "responsibility"}
        if v not in valid_cats:
            return "competency"
        return v

    @model_validator(mode="after")
    def populate_description_if_missing(self) -> "JobRequirement":
        if not self.description:
            if self.skill:
                self.description = f"Demonstrate proficiency in {self.skill}"
            else:
                self.description = "General requirement"
        if not self.skill and self.description:
            self.skill = self.description
        return self


class JobProfile(BaseModel):
    job_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    description: Optional[str] = ""
    domain: List[str] = Field(default_factory=list)
    min_experience_months: int = Field(default=0, ge=0)
    must_have_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    education_requirements: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    requirements: List[JobRequirement] = Field(default_factory=list)

    @field_validator("min_experience_months")
    @classmethod
    def validate_min_exp(cls, v: int) -> int:
        if v < 0:
            raise ValueError("min_experience_months must be non-negative")
        return v
