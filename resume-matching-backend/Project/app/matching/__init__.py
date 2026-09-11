"""
matching package

Each matcher module scores one dimension of fit between a resume and a
job description. `aggregator.py` combines the individual scores into a
single overall match score using the weights defined in app.config.
"""

from app.matching.skill_matcher import match_skills
from app.matching.experience_matcher import match_experience
from app.matching.education_matcher import match_education
from app.matching.role_matcher import match_role
from app.matching.aggregator import compute_overall_match

__all__ = [
    "match_skills",
    "match_experience",
    "match_education",
    "match_role",
    "compute_overall_match",
]
