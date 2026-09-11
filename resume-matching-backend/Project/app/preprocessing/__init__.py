"""
preprocessing package

Handles text normalization and structured field extraction
(skills, years of experience, education, roles) from raw
resume / job description text.
"""

from app.preprocessing.text_cleaner import clean_text
from app.preprocessing.extractor import (
    extract_skills,
    extract_years_of_experience,
    extract_education_level,
    extract_roles,
)

__all__ = [
    "clean_text",
    "extract_skills",
    "extract_years_of_experience",
    "extract_education_level",
    "extract_roles",
]
