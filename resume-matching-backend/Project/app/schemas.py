from typing import List, Optional
from pydantic import BaseModel, Field


class MatchRequest(BaseModel):
    resume_text: str = Field(..., description="Raw resume text")
    job_description: str = Field(..., description="Raw job description text")
    job_title: Optional[str] = Field(
        None, description="Optional explicit job title to match against resume roles"
    )


class SkillMatchResult(BaseModel):
    score: float
    matched_skills: List[str]
    missing_skills: List[str]
    resume_skills: List[str]
    job_skills: List[str]


class ExperienceMatchResult(BaseModel):
    score: float
    resume_years: float
    required_years: float


class EducationMatchResult(BaseModel):
    score: float
    resume_level: Optional[str]
    required_level: Optional[str]


class RoleMatchResult(BaseModel):
    score: float
    resume_roles: List[str]
    job_role: Optional[str]


class MatchResponse(BaseModel):
    overall_score: float
    skills: SkillMatchResult
    experience: ExperienceMatchResult
    education: EducationMatchResult
    role: RoleMatchResult
