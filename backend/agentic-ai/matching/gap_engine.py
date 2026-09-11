"""
gap_engine.py
Skill Gap Engine categorizing missing and non-exact mandatory skills into critical, moderate, optional, and transferable gaps.
"""

from typing import List, Set
from contracts.candidate import CandidateProfile
from contracts.job import JobProfile
from contracts.match import SkillGaps, TransferableGap, SkillMatchDetail


def find_skill_gaps(candidate: CandidateProfile, job: JobProfile, skill_matches: List[SkillMatchDetail]) -> SkillGaps:
    """
    Identifies missing skills and non-exact mandatory skills:
    - Mandatory skill not matched as 'exact' or 'equivalent' (e.g. matched as related, transferable, or missing) -> CRITICAL gap!
    - Preferred skill missing -> MODERATE gap
    - Optional skill missing -> OPTIONAL gap
    - Available transferable skill -> TRANSFERABLE gap detail
    """
    critical = []
    moderate = []
    optional = []
    transferable = []

    must_have_set: Set[str] = set(job.must_have_skills)
    preferred_set: Set[str] = set(job.preferred_skills)

    for req in job.requirements:
        if req.importance == "must_have":
            must_have_set.add(req.skill)
        elif req.importance == "preferred":
            preferred_set.add(req.skill)

    seen_gaps = set()

    for match in skill_matches:
        req_skill = match.required_skill
        m_type = match.match_type

        # Mandatory skill check: anything other than exact/equivalent is a CRITICAL GAP!
        if req_skill in must_have_set:
            if m_type not in ["exact", "equivalent"] and req_skill not in seen_gaps:
                critical.append(req_skill)
                seen_gaps.add(req_skill)

        # Non-mandatory gap checks
        if m_type == "missing" and req_skill not in seen_gaps:
            seen_gaps.add(req_skill)
            if req_skill in preferred_set:
                moderate.append(req_skill)
            else:
                optional.append(req_skill)

        # Record transferable info if candidate has a transferable alternative
        if m_type == "transferable" and match.candidate_skill:
            transferable.append(TransferableGap(
                from_skill=match.candidate_skill,
                to_skill=req_skill,
                confidence=match.similarity
            ))

    return SkillGaps(
        critical=critical,
        moderate=moderate,
        optional=optional,
        transferable=transferable
    )
