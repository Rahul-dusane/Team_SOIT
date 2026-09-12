"""
evidence_retriever.py
Domain-Independent Evidence Retrieval & Validation Engine.
Features strict word-boundary matching, contradiction/negation detection, requirement-specific duration validation,
and evidence-backed status determination across any profession.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from contracts.candidate import CandidateProfile
from nlp.similarity import semantic_similarity
from nlp.preprocessing import clean_text

NEGATION_REGEX = re.compile(
    r'\b(no|not|never|without|lacks?|lacking|did\s+not|didn\'t|don\'t|doesn\'t|zero|nil|none)\b',
    re.IGNORECASE
)


def contains_negation(passage: str, keyword: str) -> bool:
    """Detects if a candidate text passage contains a negation regarding the keyword."""
    if not passage or not keyword:
        return False

    pass_lower = passage.lower()
    kw_lower = keyword.lower()

    if kw_lower not in pass_lower:
        return False

    # Check for negation words within 6 words before or after the keyword
    tokens = pass_lower.split()
    for idx, t in enumerate(tokens):
        if kw_lower in t:
            window_start = max(0, idx - 6)
            window_end = min(len(tokens), idx + 6)
            window_text = " ".join(tokens[window_start:window_end])
            if NEGATION_REGEX.search(window_text):
                return True
    return False


def word_boundary_match(keyword: str, text: str) -> bool:
    """Strict word-boundary matching preventing substring corruption (e.g. Java matching JavaScript)."""
    if not keyword or not text:
        return False
    pattern = r'\b' + re.escape(keyword.strip()) + r'\b'
    return bool(re.search(pattern, text, re.IGNORECASE))


def retrieve_candidate_evidence(
    requirement_text: str,
    candidate: CandidateProfile,
    req_skill: str = None,
    min_duration_months: int = 0,
    db: Any = None
) -> Tuple[str, str, Optional[int], float]:
    """
    Searches candidate profile and stored vector chunks for supporting evidence text for an arbitrary requirement.
    Returns (status, evidence_passage, page, confidence).
    Statuses: 'satisfied' (1.0), 'partially_supported' (0.5), 'contradicted' (0.0), 'unknown' (0.0).
    """
    if not requirement_text or not requirement_text.strip():
        return "unknown", "", None, 0.0

    req_clean = clean_text(requirement_text)
    search_terms = []
    if req_skill:
        search_terms.append(req_skill)
    # Extract noun terms from requirement text
    for token in req_clean.split():
        if len(token) > 3 and token.lower() not in ["experience", "knowledge", "proficiency", "with", "using", "demonstrate"]:
            search_terms.append(token)

    best_passage = ""
    best_sim = 0.0
    best_page = None
    total_matching_duration = 0

    # 1. Search Candidate Skills
    for s in candidate.skills:
        if not s or not s.raw_skill:
            continue
            
        raw_skill = s.raw_skill
        evidence_text = getattr(s, 'evidence', None) or ""
        ev_text = f"{raw_skill} - {evidence_text}".strip()

        # Contradiction check in skill evidence
        if evidence_text and contains_negation(evidence_text, raw_skill):
            return "contradicted", f"Contradiction detected: '{evidence_text}'", getattr(s, 'page', None), 1.0

        for term in search_terms:
            if word_boundary_match(term, raw_skill):
                confidence = getattr(s, 'confidence', 1.0) or 1.0
                return "satisfied", ev_text, getattr(s, 'page', None), confidence

        sim = semantic_similarity(req_clean, raw_skill)
        if sim > best_sim:
            best_sim = sim
            best_passage = ev_text
            best_page = getattr(s, 'page', None)

    # 2. Search Experience Descriptions & Roles
    for exp in candidate.experiences:
        if not exp or not exp.role:
            continue
            
        role = exp.role or ""
        company = exp.company or ""
        desc = exp.description or ""
        exp_text = f"{role} at {company}: {desc}".strip()
        
        if not exp_text:
            continue

        # Contradiction Check
        for term in search_terms:
            if contains_negation(exp_text, term):
                return "contradicted", f"Contradiction detected in experience: '{exp_text}'", None, 1.0

        for term in search_terms:
            if word_boundary_match(term, exp_text):
                total_matching_duration += (exp.duration_months or 0)
                if min_duration_months > 0 and total_matching_duration < min_duration_months:
                    # Duration requirement not fully met
                    return "partially_supported", f"{exp_text} (Duration: {total_matching_duration} mos < required {min_duration_months} mos)", None, 0.70
                return "satisfied", exp_text, None, 1.0

        sim = semantic_similarity(req_clean, exp_text)
        if sim > best_sim:
            best_sim = sim
            best_passage = exp_text

    # 3. Search Projects
    for proj in candidate.projects:
        # Handle both CandidateProject objects and dict/string representations
        if isinstance(proj, str):
            proj_text = proj
        elif hasattr(proj, 'title'):
            proj_text = f"{proj.title}: {getattr(proj, 'description', '') or ''} {' '.join(getattr(proj, 'technologies', []) or [])}".strip()
        elif isinstance(proj, dict):
            proj_text = f"{proj.get('title', 'Project')}: {proj.get('description', '') or ''} {' '.join(proj.get('technologies', []) or [])}".strip()
        else:
            proj_text = str(proj)
        
        if not proj_text:
            continue

        for term in search_terms:
            if contains_negation(proj_text, term):
                return "contradicted", f"Contradiction detected in project: '{proj_text}'", None, 1.0

        for term in search_terms:
            if word_boundary_match(term, proj_text):
                return "satisfied", proj_text, None, 1.0

        sim = semantic_similarity(req_clean, proj_text)
        if sim > best_sim:
            best_sim = sim
            best_passage = proj_text

    # 4. Search Education & Certifications
    for edu in candidate.education:
        edu_text = f"{edu.degree} in {edu.field or ''} from {edu.institution or ''}".strip()
        for term in search_terms:
            if word_boundary_match(term, edu_text):
                return "satisfied", edu_text, None, 1.0

    for cert in candidate.certifications:
        for term in search_terms:
            if word_boundary_match(term, cert):
                return "satisfied", f"Certified: {cert}", None, 1.0

    # 5. Vector Store Chunk Lookup if DB session is provided
    if db is not None and candidate.candidate_id:
        try:
            from vector_store import retrieve_evidence_from_vector_store
            vector_results = retrieve_evidence_from_vector_store(db, candidate.candidate_id, requirement_text, top_k=2)
            for v_res in vector_results:
                v_sim = v_res["similarity"]
                v_text = v_res["content"]
                v_page = v_res["page_number"]
                for term in search_terms:
                    if contains_negation(v_text, term):
                        return "contradicted", f"Contradiction detected in vector chunk: '{v_text}'", v_page, 1.0
                    if word_boundary_match(term, v_text):
                        return "satisfied", f"[Vector Match p.{v_page}] {v_text}", v_page, 1.0

                if v_sim > best_sim:
                    best_sim = v_sim
                    best_passage = f"[Vector Match p.{v_page}] {v_text}"
                    best_page = v_page
        except Exception:
            pass

    # 6. Status Determination based on Validated Standards
    if best_sim >= 0.85:
        return "satisfied", best_passage, best_page, round(best_sim, 2)
    elif best_sim >= 0.65:
        return "partially_supported", best_passage, best_page, round(best_sim, 2)
    else:
        return "unknown", "", None, 0.0
