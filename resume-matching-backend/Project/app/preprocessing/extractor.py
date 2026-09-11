"""
Extraction routines that pull structured signals out of cleaned text:
- skills (from a known vocabulary)
- years of experience (via regex patterns)
- education level (highest degree mentioned)
- job role / title candidates
"""

import re
from typing import List, Optional

from app.config import KNOWN_SKILLS, EDUCATION_RANKS
from app.preprocessing.text_cleaner import clean_text

_YEARS_PATTERNS = [
    r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience",
    r"experience\s*(?:of)?\s*(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)",
    r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)",
]

_ROLE_KEYWORDS = [
    "engineer", "developer", "manager", "analyst", "scientist", "architect",
    "designer", "consultant", "administrator", "lead", "director",
    "specialist", "intern", "officer", "coordinator",
]


def extract_skills(text: str) -> List[str]:
    """Return the sorted list of known skills present in the text."""
    cleaned = clean_text(text)
    found = set()
    for skill in KNOWN_SKILLS:
        # word-boundary-ish match; skills may contain '.', '+', '#', '/'
        pattern = re.escape(skill)
        if re.search(rf"(?<![a-z0-9]){pattern}(?![a-z0-9])", cleaned):
            found.add(skill)
    return sorted(found)


def extract_years_of_experience(text: str) -> float:
    """
    Return the maximum number of years of experience mentioned in the text,
    or 0.0 if none is found.
    """
    cleaned = clean_text(text)
    years_found = []
    for pattern in _YEARS_PATTERNS:
        for match in re.finditer(pattern, cleaned):
            try:
                years_found.append(float(match.group(1)))
            except (ValueError, IndexError):
                continue
    return max(years_found) if years_found else 0.0


def extract_education_level(text: str) -> Optional[str]:
    """
    Return the highest education level keyword found in the text
    (e.g. 'phd', 'master', 'bachelor'), or None if none is found.
    """
    cleaned = clean_text(text)
    best_level = None
    best_rank = -1
    for keyword, rank in EDUCATION_RANKS.items():
        if re.search(rf"(?<![a-z0-9]){re.escape(keyword)}(?![a-z0-9])", cleaned):
            if rank > best_rank:
                best_rank = rank
                best_level = keyword
    return best_level


def extract_roles(text: str) -> List[str]:
    """
    Extract candidate job-title phrases: short windows of words ending in
    a role keyword (e.g. 'senior software engineer', 'data scientist').
    """
    cleaned = clean_text(text)
    tokens = cleaned.split()
    roles = set()

    for i, token in enumerate(tokens):
        if token in _ROLE_KEYWORDS:
            start = max(0, i - 2)
            phrase = " ".join(tokens[start:i + 1])
            roles.add(phrase)

    return sorted(roles)
