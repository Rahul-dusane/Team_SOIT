"""
job.py
Pydantic contracts for Job Requirement and Job Profile.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class JobRequirement(BaseModel):
    requirement_id: Optional[str] = None
    skill: str
    importance: str = "must_have"  # "must_have", "preferred", "nice_to_have"
    weight: float = 10.0


class JobProfile(BaseModel):
    job_id: str
    title: str
    description: Optional[str] = ""
    domain: List[str] = Field(default_factory=list)
    min_experience_months: int = 0
    must_have_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    education_requirements: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    requirements: List[JobRequirement] = Field(default_factory=list)
