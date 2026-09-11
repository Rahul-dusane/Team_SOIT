"""
feature_filter.py
PII-Safe feature extractor stripping identity fields and anonymizing free text before scoring.
"""

import re
from typing import Dict, Any, List
from contracts.candidate import CandidateProfile
from nlp.preprocessing import EMAIL_REGEX, PHONE_REGEX, clean_text


def sanitize_pii_text(text: str, name: str = None) -> str:
    """Strips email, phone numbers, and candidate name from free text."""
    if not text:
        return ""
    text = EMAIL_REGEX.sub("[EMAIL_REMOVED]", text)
    text = PHONE_REGEX.sub("[PHONE_REMOVED]", text)
    if name and len(name.strip()) > 2:
        for token in name.strip().split():
            if len(token) > 2:
                text = re.sub(re.escape(token), "[NAME_REMOVED]", text, flags=re.IGNORECASE)
    return clean_text(text)


def build_scoring_profile(candidate: CandidateProfile) -> Dict[str, Any]:
    """
    Strips all PII / identity information (name, email, phone)
    and produces a clean, anonymized scoring dictionary containing only technical & career data.
    """
    cand_name = candidate.name or ""
    
    anonymized_experiences = []
    for exp in candidate.experiences:
        exp_dict = exp.model_dump() if hasattr(exp, "model_dump") else exp.dict()
        exp_dict["description"] = sanitize_pii_text(exp_dict.get("description", ""), cand_name)
        anonymized_experiences.append(exp_dict)

    anonymized_projects = []
    for proj in candidate.projects:
        proj_dict = proj.model_dump() if hasattr(proj, "model_dump") else proj.dict()
        proj_dict["description"] = sanitize_pii_text(proj_dict.get("description", ""), cand_name)
        anonymized_projects.append(proj_dict)

    anonymized_education = []
    for edu in candidate.education:
        edu_dict = edu.model_dump() if hasattr(edu, "model_dump") else edu.dict()
        anonymized_education.append(edu_dict)

    anonymized_skills = []
    for s in candidate.skills:
        s_dict = s.model_dump() if hasattr(s, "model_dump") else s.dict()
        s_dict["evidence"] = sanitize_pii_text(s_dict.get("evidence", ""), cand_name)
        anonymized_skills.append(s_dict)

    return {
        "candidate_id": candidate.candidate_id,
        "total_experience_months": candidate.total_experience_months,
        "skills": anonymized_skills,
        "experiences": anonymized_experiences,
        "education": anonymized_education,
        "projects": anonymized_projects,
        "domains": candidate.domains,
        "certifications": candidate.certifications
    }
