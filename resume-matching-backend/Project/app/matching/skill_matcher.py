"""
Scores how well a resume's skills cover the skills required by a job
description. Score = fraction of required (job) skills that are present
in the resume.
"""

from typing import List
from app.preprocessing.extractor import extract_skills


def match_skills(resume_text: str, job_text: str) -> dict:
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_text)

    resume_set = set(resume_skills)
    job_set = set(job_skills)

    if not job_set:
        # Nothing specific required -> treat as a full match to avoid
        # unfairly penalizing the resume for an unspecific JD.
        score = 1.0
        matched: List[str] = []
        missing: List[str] = []
    else:
        matched = sorted(resume_set & job_set)
        missing = sorted(job_set - resume_set)
        score = len(matched) / len(job_set)

    return {
        "score": round(score, 4),
        "matched_skills": matched,
        "missing_skills": missing,
        "resume_skills": resume_skills,
        "job_skills": job_skills,
    }
