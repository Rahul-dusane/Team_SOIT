"""
Scores how closely the resume's role history matches the target job
title/role. Uses word-overlap plus a fuzzy string similarity fallback,
taking the best match among all role phrases found in the resume.
"""

from difflib import SequenceMatcher
from typing import List, Optional

from app.preprocessing.extractor import extract_roles
from app.preprocessing.text_cleaner import clean_text


def _similarity(a: str, b: str) -> float:
    word_overlap = 0.0
    a_words, b_words = set(a.split()), set(b.split())
    if a_words and b_words:
        word_overlap = len(a_words & b_words) / len(a_words | b_words)

    fuzzy = SequenceMatcher(None, a, b).ratio()
    return max(word_overlap, fuzzy)


def match_role(resume_text: str, job_text: str, job_title: Optional[str] = None) -> dict:
    resume_roles = extract_roles(resume_text)

    job_role = clean_text(job_title) if job_title else None
    if not job_role:
        job_roles_found = extract_roles(job_text)
        job_role = job_roles_found[0] if job_roles_found else None

    if not job_role:
        # No discernible target role -> full score, nothing to compare against.
        score = 1.0
    elif not resume_roles:
        score = 0.0
    else:
        score = max(_similarity(job_role, r) for r in resume_roles)

    return {
        "score": round(score, 4),
        "resume_roles": resume_roles,
        "job_role": job_role,
    }
