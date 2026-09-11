"""
role_normalizer.py
Normalizes job roles to canonical job titles.
"""

import re
from rapidfuzz import process, fuzz

CANONICAL_ROLES = [
    "Backend Engineer",
    "Frontend Engineer",
    "Full Stack Engineer",
    "DevOps Engineer",
    "Data Scientist",
    "Data Engineer",
    "Machine Learning Engineer",
    "Software Engineer",
    "Cloud Architect",
    "Product Manager"
]


def normalize_role(role_title: str) -> str:
    """Normalize raw role title string to canonical title."""
    if not role_title:
        return "Software Engineer"
    
    clean_title = re.sub(r'\s+', ' ', role_title).strip()
    match = process.extractOne(clean_title, CANONICAL_ROLES, scorer=fuzz.WRatio)
    if match and match[1] >= 75.0:
        return match[0]
    return clean_title.title()
