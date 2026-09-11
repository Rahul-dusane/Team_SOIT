"""
evidence_retriever.py
Domain-Independent Evidence Retrieval Engine.
Retrieves supporting text passages and candidate claims for any job requirement text across any profession.
"""

from typing import Dict, Any, List, Optional, Tuple
from contracts.candidate import CandidateProfile
from nlp.similarity import semantic_similarity
from nlp.preprocessing import clean_text


def retrieve_candidate_evidence(requirement_text: str, candidate: CandidateProfile, req_skill: str = None) -> Tuple[str, str, Optional[int], float]:
    """
    Searches candidate profile for supporting evidence text for an arbitrary requirement.
    Returns (status, evidence_passage, page, confidence).
    Statuses: 'satisfied' (1.0), 'partially_supported' (0.5), 'contradicted' (0.0), 'unknown' (0.0).
    """
    if not requirement_text or not requirement_text.strip():
        return "unknown", "", None, 0.0

    req_clean = clean_text(requirement_text).lower()
    target_skill_lower = req_skill.lower() if req_skill else None

    best_passage = ""
    best_sim = 0.0
    best_page = None

    # Search Candidate Skills
    for s in candidate.skills:
        raw_s_lower = s.raw_skill.lower()
        norm_s_lower = (s.normalized_skill or "").lower()

        # Direct skill match
        if (target_skill_lower and (target_skill_lower == raw_s_lower or target_skill_lower == norm_s_lower)) or raw_s_lower in req_clean:
            ev_msg = f"Proficient in {s.raw_skill}" + (f": {s.evidence}" if s.evidence else "")
            return "satisfied", ev_msg, s.page, s.confidence

        s_text = f"{s.raw_skill} - {s.evidence or ''}".strip()
        sim = semantic_similarity(req_clean, s.raw_skill)
        if sim > best_sim:
            best_sim = sim
            best_passage = s_text
            best_page = s.page

    # Search Experience descriptions & roles
    for exp in candidate.experiences:
        exp_text = f"{exp.role} at {exp.company or ''}: {exp.description or ''}".strip()
        if not exp_text:
            continue
        
        if req_clean in exp_text.lower() or (target_skill_lower and target_skill_lower in exp_text.lower()):
            return "satisfied", exp_text, None, 1.0

        sim = semantic_similarity(req_clean, exp_text)
        if sim > best_sim:
            best_sim = sim
            best_passage = exp_text

    # Search Projects
    for proj in candidate.projects:
        proj_text = f"{proj.title}: {proj.description or ''} {' '.join(proj.technologies)}".strip()
        if not proj_text:
            continue
        
        if req_clean in proj_text.lower() or (target_skill_lower and target_skill_lower in proj_text.lower()):
            return "satisfied", proj_text, None, 1.0

        sim = semantic_similarity(req_clean, proj_text)
        if sim > best_sim:
            best_sim = sim
            best_passage = proj_text

    # Search Education & Certifications
    for edu in candidate.education:
        edu_text = f"{edu.degree} in {edu.field or ''} from {edu.institution or ''}".strip()
        if req_clean in edu_text.lower():
            return "satisfied", edu_text, None, 1.0

    for cert in candidate.certifications:
        if req_clean in cert.lower() or (target_skill_lower and target_skill_lower in cert.lower()):
            return "satisfied", f"Certified: {cert}", None, 1.0

    # Status Determination based on evidence threshold
    if best_sim >= 0.75:
        return "satisfied", best_passage, best_page, round(best_sim, 2)
    elif best_sim >= 0.55:
        return "partially_supported", best_passage, best_page, round(best_sim, 2)
    else:
        return "unknown", "", None, 0.0
