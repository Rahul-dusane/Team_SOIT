"""
feature_filter.py
PII-Safe feature extractor sanitizing all text fields (roles, titles, field, institution, descriptions)
without corrupting technical skill terms.
"""

import re
from typing import Dict, Any, List
from contracts.candidate import CandidateProfile
from nlp.preprocessing import EMAIL_REGEX, PHONE_REGEX, clean_text
from nlp.skill_normalizer import CANONICAL_SKILLS

# Known technical terms that must NEVER be stripped by name token replacement
TECH_PROTECTED_TERMS = set([s.lower() for s in CANONICAL_SKILLS] + [
    "ray", "c", "go", "r", "sql", "aws", "gcp", "git", "api", "rest", "dev", "ops", "data"
])


def sanitize_pii_text(text: str, name: str = None) -> str:
    """Strips email, phone numbers, and candidate name tokens from text while preserving tech terms."""
    if not text:
        return ""
    
    text = EMAIL_REGEX.sub("[EMAIL_REMOVED]", text)
    text = PHONE_REGEX.sub("[PHONE_REMOVED]", text)

    if name and len(name.strip()) > 2:
        for token in name.strip().split():
            t_lower = token.strip().lower()
            if len(t_lower) > 2 and t_lower not in TECH_PROTECTED_TERMS:
                text = re.sub(r'\b' + re.escape(token) + r'\b', "[NAME_REMOVED]", text, flags=re.IGNORECASE)

    return clean_text(text)


def build_scoring_profile(candidate: CandidateProfile) -> Dict[str, Any]:
    """
    Strips all PII / identity information (name, email, phone)
    and sanitizes all text fields across experiences, projects, education, and skills.
    """
    cand_name = candidate.name or ""
    
    anonymized_experiences = []
    for exp in candidate.experiences:
        exp_dict = exp.model_dump() if hasattr(exp, "model_dump") else exp.dict()
        exp_dict["role"] = sanitize_pii_text(exp_dict.get("role", ""), cand_name)
        exp_dict["company"] = sanitize_pii_text(exp_dict.get("company", ""), cand_name)
        exp_dict["description"] = sanitize_pii_text(exp_dict.get("description", ""), cand_name)
        anonymized_experiences.append(exp_dict)

    anonymized_projects = []
    for proj in candidate.projects:
        proj_dict = proj.model_dump() if hasattr(proj, "model_dump") else proj.dict()
        proj_dict["title"] = sanitize_pii_text(proj_dict.get("title", ""), cand_name)
        proj_dict["description"] = sanitize_pii_text(proj_dict.get("description", ""), cand_name)
        proj_dict["technologies"] = [sanitize_pii_text(tech, cand_name) for tech in proj_dict.get("technologies", [])]
        anonymized_projects.append(proj_dict)

    anonymized_education = []
    for edu in candidate.education:
        edu_dict = edu.model_dump() if hasattr(edu, "model_dump") else edu.dict()
        edu_dict["degree"] = sanitize_pii_text(edu_dict.get("degree", ""), cand_name)
        edu_dict["field"] = sanitize_pii_text(edu_dict.get("field", ""), cand_name)
        edu_dict["institution"] = sanitize_pii_text(edu_dict.get("institution", ""), cand_name)
        anonymized_education.append(edu_dict)

    anonymized_skills = []
    for s in candidate.skills:
        s_dict = s.model_dump() if hasattr(s, "model_dump") else s.dict()
        s_dict["raw_skill"] = s_dict.get("raw_skill", "")
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
