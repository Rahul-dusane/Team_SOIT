"""Candidate profile schemas for Resume Agent extraction."""

from typing import List, Optional
from pydantic import BaseModel, Field


class Skill(BaseModel):
    name: str = Field(description="Normalized skill or technology name (e.g. Python, Docker)")
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence level between 0.0 and 1.0 based on explicit resume mentions"
    )
    evidence: Optional[str] = Field(
        default=None,
        description="Direct brief quote or context from the resume supporting this skill"
    )


class Experience(BaseModel):
    company: Optional[str] = Field(default=None, description="Employer or organization name")
    role: Optional[str] = Field(default=None, description="Job title or designation")
    duration_months: Optional[int] = Field(default=0, ge=0, description="Duration in months")
    description: Optional[str] = Field(default=None, description="Summary of responsibilities and impact")
    technologies: List[str] = Field(default_factory=list, description="Technologies used in this role")


class Education(BaseModel):
    degree: Optional[str] = Field(default=None, description="Degree earned (e.g. B.Tech, M.S., B.S.)")
    field: Optional[str] = Field(default=None, description="Field of study / major (e.g. Computer Science)")
    institution: Optional[str] = Field(default=None, description="University, college or school name")
    graduation_year: Optional[int] = Field(default=None, description="Year of graduation")


class CandidateProfile(BaseModel):
    candidate_id: str = Field(description="Unique identifier for the candidate (e.g. C01)")
    name: Optional[str] = Field(default=None, description="Full name of candidate")
    email: Optional[str] = Field(default=None, description="Email address if present")
    phone: Optional[str] = Field(default=None, description="Phone number if present")
    summary: Optional[str] = Field(default=None, description="Professional summary or bio")
    
    skills: List[Skill] = Field(default_factory=list, description="List of validated skills")
    experience: List[Experience] = Field(default_factory=list, description="Employment history")
    total_experience_months: int = Field(default=0, ge=0, description="Sum of all relevant experience in months")
    
    education: List[Education] = Field(default_factory=list, description="Educational background")
    projects: List[str] = Field(default_factory=list, description="Key projects with brief description")
    certifications: List[str] = Field(default_factory=list, description="Certifications and licenses")
    domains: List[str] = Field(default_factory=list, description="Domains worked in (e.g. Fintech, Healthcare, Cloud)")

