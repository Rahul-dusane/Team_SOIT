"""
Combines the individual matcher outputs into one weighted overall score.
"""

from typing import Optional

from app.config import MATCH_WEIGHTS
from app.matching.skill_matcher import match_skills
from app.matching.experience_matcher import match_experience
from app.matching.education_matcher import match_education
from app.matching.role_matcher import match_role


def compute_overall_match(
    resume_text: str, job_text: str, job_title: Optional[str] = None
) -> dict:
    skills = match_skills(resume_text, job_text)
    experience = match_experience(resume_text, job_text)
    education = match_education(resume_text, job_text)
    role = match_role(resume_text, job_text, job_title)

    overall = (
        skills["score"] * MATCH_WEIGHTS["skills"]
        + experience["score"] * MATCH_WEIGHTS["experience"]
        + education["score"] * MATCH_WEIGHTS["education"]
        + role["score"] * MATCH_WEIGHTS["role"]
    )

    return {
        "overall_score": round(overall, 4),
        "skills": skills,
        "experience": experience,
        "education": education,
        "role": role,
    }
