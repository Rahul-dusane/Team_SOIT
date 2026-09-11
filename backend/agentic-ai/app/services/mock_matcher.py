"""Mock Matching Engine implementing Member 2's deterministic scoring contract."""

from typing import Dict, Any, List
from app.schemas.match import MatchResult, ScoreBreakdown


def match_candidate_to_job(candidate_data: Dict[str, Any], job_data: Dict[str, Any]) -> MatchResult:
    """
    Simulates Member 2's mathematical matching engine:
    - Analyzes skill overlap against weighted must-haves and preferred skills.
    - Evaluates experience duration against minimum job threshold.
    - Computes a deterministic overall_score on a 0-100% scale.
    - Determines if all MUST_HAVE criteria passed.
    """
    cid = candidate_data.get("candidate_id", "Unknown")
    jid = job_data.get("job_id", "Unknown")
    
    cand_skills_raw = candidate_data.get("skills", [])
    cand_skill_names = {s.get("name", "").strip().lower() for s in cand_skills_raw}
    
    must_haves = [s.strip().lower() for s in job_data.get("must_have_skills", [])]
    preferred = [s.strip().lower() for s in job_data.get("preferred_skills", [])]
    
    # 1. Skill analysis
    matched_must = [m for m in must_haves if any(m in cs or cs in m for cs in cand_skill_names)]
    missing_must = [m for m in must_haves if not any(m in cs or cs in m for cs in cand_skill_names)]
    
    matched_pref = [p for p in preferred if any(p in cs or cs in m for cs in cand_skill_names for m in [p])]
    missing_pref = [p for p in preferred if not any(p in cs or cs in m for cs in cand_skill_names for m in [p])]
    
    must_score = (len(matched_must) / max(len(must_haves), 1)) * 50.0
    pref_score = (len(matched_pref) / max(len(preferred), 1)) * 20.0
    skill_component = must_score + pref_score
    
    # 2. Experience analysis
    cand_exp = candidate_data.get("total_experience_months", 0)
    req_exp = job_data.get("min_experience_months", 0)
    
    if req_exp == 0:
        exp_component = 20.0
    else:
        exp_ratio = min(cand_exp / req_exp, 1.5)
        exp_component = min(exp_ratio * 20.0, 20.0)
        
    # 3. Baseline semantic component simulation
    semantic_component = 10.0 if len(matched_must) > 0 else 2.0
    
    # Total calculation
    overall = min(round(skill_component + exp_component + semantic_component, 1), 100.0)
    mandatory_pass = len(missing_must) == 0
    
    # Collect all gaps (title-cased for readability)
    all_gaps = [m.capitalize() for m in missing_must] + [p.capitalize() for p in missing_pref]
    all_matched = [m.capitalize() for m in matched_must] + [p.capitalize() for p in matched_pref]
    
    return MatchResult(
        candidate_id=cid,
        job_id=jid,
        overall_score=overall,
        mandatory_pass=mandatory_pass,
        breakdown=ScoreBreakdown(
            skills=round(skill_component, 1),
            experience=round(exp_component, 1),
            semantic=round(semantic_component, 1),
            domain=0.0
        ),
        gaps=all_gaps,
        matched_skills=all_matched
    )

