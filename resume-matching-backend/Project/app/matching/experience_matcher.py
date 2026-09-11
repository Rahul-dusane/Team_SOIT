"""
Scores whether the resume's years of experience meet the job's stated
requirement. Meeting or exceeding the requirement scores 1.0; falling
short scores proportionally (resume_years / required_years).
"""

from app.preprocessing.extractor import extract_years_of_experience


def match_experience(resume_text: str, job_text: str) -> dict:
    resume_years = extract_years_of_experience(resume_text)
    required_years = extract_years_of_experience(job_text)

    if required_years <= 0:
        # No explicit requirement stated -> full score.
        score = 1.0
    elif resume_years >= required_years:
        score = 1.0
    else:
        score = resume_years / required_years

    return {
        "score": round(score, 4),
        "resume_years": resume_years,
        "required_years": required_years,
    }
