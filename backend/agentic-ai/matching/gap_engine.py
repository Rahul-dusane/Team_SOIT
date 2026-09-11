"""
gap_engine.py
Skill Gap Engine categorizing missing skills into critical, moderate, optional, and transferable.
"""

from typing import List, Set
from contracts.candidate import CandidateProfile
from contracts.job import JobProfile
from contracts.match import SkillGaps, TransferableGap, SkillMatchDetail
from matching.rules import classify_skill_match


def find_skill_gaps(candidate: CandidateProfile, job: JobProfile, skill_matches: List[SkillMatchDetail]) -> SkillGaps:
    """
    Identifies missing skills and categorizes them:
    - Missing must-have skill -> critical (checks both job.must_have_skills AND job.requirements)
    - Missing preferred skill -> moderate / optional
    - Available transferable skill -> transferable
    """
    critical = []
    moderate = []
    optional = []
    transferable = []

    # Gather must-have skills from separate list and structured requirements
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
        if req_skill in seen_gaps:
            continue

        if match.match_type == "missing":
            seen_gaps.add(req_skill)
            if req_skill in must_have_set:
                critical.append(req_skill)
            elif req_skill in preferred_set:
                moderate.append(req_skill)
            else:
                optional.append(req_skill)

        elif match.match_type == "transferable" and match.candidate_skill:
            if req_skill in must_have_set and req_skill not in critical:
                # If mandatory requirement is only satisfied by a transferable skill, log as critical gap!
                critical.append(req_skill)
                seen_gaps.add(req_skill)
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
