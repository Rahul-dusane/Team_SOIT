"""
candidate.py
Pydantic contracts for Candidate Profile and sub-components.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class CandidateSkill(BaseModel):
    raw_skill: str
    normalized_skill: Optional[str] = None
    confidence: float = 1.0
    years_experience: Optional[float] = None
    evidence: Optional[str] = None
    page: Optional[int] = None


class CandidateExperience(BaseModel):
    company: Optional[str] = None
    role: str
    duration_months: int = 0
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = ""


class CandidateEducation(BaseModel):
    degree: str
    field: Optional[str] = None
    institution: Optional[str] = None
    graduation_year: Optional[int] = None


class CandidateProject(BaseModel):
    title: str
    description: Optional[str] = ""
    technologies: List[str] = Field(default_factory=list)


class CandidateProfile(BaseModel):
    candidate_id: str
    name: Optional[str] = "Anonymous Candidate"
    email: Optional[str] = None
    phone: Optional[str] = None
    total_experience_months: int = 0
    skills: List[CandidateSkill] = Field(default_factory=list)
    experiences: List[CandidateExperience] = Field(default_factory=list)
    education: List[CandidateEducation] = Field(default_factory=list)
    projects: List[CandidateProject] = Field(default_factory=list)
    domains: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
