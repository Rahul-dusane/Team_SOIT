"""
Scores whether the resume's highest education level meets the job's
stated requirement, using the ranked levels in app.config.EDUCATION_RANKS.
"""

from app.config import EDUCATION_RANKS
from app.preprocessing.extractor import extract_education_level


def match_education(resume_text: str, job_text: str) -> dict:
    resume_level = extract_education_level(resume_text)
    required_level = extract_education_level(job_text)

    resume_rank = EDUCATION_RANKS.get(resume_level, 0) if resume_level else 0
    required_rank = EDUCATION_RANKS.get(required_level, 0) if required_level else 0

    if required_rank == 0:
        # No explicit requirement stated -> full score.
        score = 1.0
    elif resume_rank >= required_rank:
        score = 1.0
    else:
        score = resume_rank / required_rank

    return {
        "score": round(score, 4),
        "resume_level": resume_level,
        "required_level": required_level,
    }
