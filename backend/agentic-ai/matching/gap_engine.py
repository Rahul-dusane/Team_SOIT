"""
gap_engine.py
Skill Gap Engine categorizing missing skills into critical, moderate, optional, and transferable.
"""

from typing import List
from contracts.candidate import CandidateProfile
from contracts.job import JobProfile
from contracts.match import SkillGaps, TransferableGap, SkillMatchDetail
from matching.rules import classify_skill_match


def find_skill_gaps(candidate: CandidateProfile, job: JobProfile, skill_matches: List[SkillMatchDetail]) -> SkillGaps:
    critical = []
    moderate = []
    optional = []
    transferable = []

    for match in skill_matches:
        if match.match_type == "missing":
            if match.required_skill in job.must_have_skills:
                critical.append(match.required_skill)
            elif match.required_skill in job.preferred_skills:
                moderate.append(match.required_skill)
            else:
                optional.append(match.required_skill)

        elif match.match_type == "transferable" and match.candidate_skill:
            transferable.append(TransferableGap(
                from_skill=match.candidate_skill,
                to_skill=match.required_skill,
                confidence=match.similarity
            ))

    return SkillGaps(
        critical=critical,
        moderate=moderate,
        optional=optional,
        transferable=transferable
    )
