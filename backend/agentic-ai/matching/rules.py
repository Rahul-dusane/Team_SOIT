"""
rules.py
Matching rules, strict 5-tier classification hierarchy, mandatory checks, and weighted skill coverage.
"""

import os
import csv
from typing import List, Dict, Any, Tuple, Union, Optional
from config.matching_config import DEFAULT_MATCHING_CONFIG, MatchingConfig
from contracts.candidate import CandidateProfile, CandidateSkill
from contracts.job import JobProfile, JobRequirement
from contracts.match import FailedRequirement, SkillMatchDetail, RequirementAssessment
from nlp.skill_normalizer import normalize_skill
from nlp.skill_relationships import get_skill_relationship
from nlp.similarity import semantic_similarity

DEGREE_LEVELS = {
    "high school": 1,
    "diploma": 2,
    "bachelor": 3,
    "master": 4,
    "doctorate": 5
}


def load_education_levels() -> Dict[str, int]:
    levels = dict(DEGREE_LEVELS)
    csv_path = os.path.join(os.path.dirname(__file__), "..", "datasets", "education_levels.csv")
    if os.path.exists(csv_path):
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                alias = row["degree_alias"].strip().lower()
                lvl = int(row["level"])
                levels[alias] = lvl
    return levels


EDUCATION_MAP = load_education_levels()


def get_degree_level(degree_str: str) -> int:
    if not degree_str:
        return 0
    d_lower = degree_str.strip().lower()
    return EDUCATION_MAP.get(d_lower, 2)


def classify_skill_match(required_skill: str, candidate_skills: List[CandidateSkill], cfg: MatchingConfig = DEFAULT_MATCHING_CONFIG) -> SkillMatchDetail:
    """
    Strict 5-Tier Skill Match Hierarchy (Semantic embeddings NEVER produce 'equivalent'):
    1. Exact canonical equality (EXACT) -> 1.0 multiplier
    2. Verified alias lookup (EQUIVALENT) -> 1.0 multiplier
    3. Known taxonomy lookup (TRANSFERABLE / RELATED / UNRELATED)
       - 'unrelated' (e.g. Java vs JavaScript) -> reject immediately (0.0 multiplier)
       - 'transferable' -> lock in transferable (0.7 multiplier)
       - 'related' -> lock in related (0.4 multiplier)
    4. Semantic similarity fallback for unknown pairs (TRANSFERABLE / RELATED / MISSING ONLY):
       - sim >= transferable threshold (0.78) -> TRANSFERABLE (0.7 multiplier)
       - sim >= related threshold (0.65) -> RELATED (0.4 multiplier)
       - sim < 0.65 -> MISSING (0.0 multiplier)
    5. Missing (MISSING) -> 0.0 multiplier
    """
    if not required_skill:
        return SkillMatchDetail(
            required_skill=required_skill or "Unknown Requirement",
            candidate_skill=None,
            match_type="missing",
            similarity=0.0,
            score=0.0
        )
    norm_req = normalize_skill(required_skill)
    req_canonical = norm_req["canonical"].lower()

    best_match = SkillMatchDetail(
        required_skill=required_skill,
        candidate_skill=None,
        match_type="missing",
        similarity=0.0,
        score=0.0
    )

    thresholds = cfg.matching_thresholds
    multipliers = cfg.tier_score_multipliers

    for c_skill in candidate_skills:
        c_raw = c_skill.raw_skill
        norm_cand = c_skill.normalized_skill or normalize_skill(c_raw)["canonical"]
        cand_canonical = norm_cand.lower()

        # 1. Exact Canonical Equality
        if req_canonical == cand_canonical:
            return SkillMatchDetail(
                required_skill=required_skill,
                candidate_skill=c_raw,
                match_type="exact",
                similarity=1.0,
                score=multipliers["exact"]
            )

        # 2. Verified Alias Match (Confidence 1.0 from alias dictionary)
        if norm_cand != c_raw and norm_cand.lower() == req_canonical:
            return SkillMatchDetail(
                required_skill=required_skill,
                candidate_skill=c_raw,
                match_type="equivalent",
                similarity=1.0,
                score=multipliers["equivalent"]
            )

        # 3. Known Taxonomy Relationship Lookup
        rel_type, rel_score = get_skill_relationship(req_canonical, cand_canonical)
        
        if rel_type == "unrelated":
            continue

        if rel_type in ["transferable", "related"]:
            match_score = multipliers.get(rel_type, 0.40)
            if match_score > best_match.score:
                best_match = SkillMatchDetail(
                    required_skill=required_skill,
                    candidate_skill=c_raw,
                    match_type=rel_type,
                    similarity=rel_score,
                    score=match_score
                )
            continue

        # 4. Semantic Similarity Fallback (ONLY for unknown pairs, CAPPED to transferable or related!)
        if rel_type == "unknown":
            sim = semantic_similarity(req_canonical, cand_canonical)
            if sim >= thresholds["transferable"]:
                if multipliers["transferable"] > best_match.score:
                    best_match = SkillMatchDetail(
                        required_skill=required_skill,
                        candidate_skill=c_raw,
                        match_type="transferable",
                        similarity=sim,
                        score=multipliers["transferable"]
                    )
            elif sim >= thresholds["related"]:
                if multipliers["related"] > best_match.score:
                    best_match = SkillMatchDetail(
                        required_skill=required_skill,
                        candidate_skill=c_raw,
                        match_type="related",
                        similarity=sim,
                        score=multipliers["related"]
                    )

    return best_match


def calculate_skill_coverage(required_skills: List[Union[str, JobRequirement]], candidate_skills: List[CandidateSkill], cfg: MatchingConfig = DEFAULT_MATCHING_CONFIG) -> Tuple[float, List[SkillMatchDetail]]:
    if not required_skills:
        return 1.0, []

    matches = []
    total_weighted_score = 0.0
    total_weight = 0.0

    for req_item in required_skills:
        if isinstance(req_item, JobRequirement):
            skill_name = req_item.skill
            w = float(req_item.weight) if req_item.weight > 0 else 1.0
        else:
            skill_name = str(req_item)
            w = 1.0

        match_detail = classify_skill_match(skill_name, candidate_skills, cfg)
        matches.append(match_detail)

        total_weighted_score += match_detail.score * w
        total_weight += w

    coverage = total_weighted_score / total_weight if total_weight > 0 else 1.0
    return round(coverage, 3), matches


def calculate_experience_fit(candidate_months: int, required_months: int) -> float:
    if required_months <= 0:
        return 1.0
    ratio = float(candidate_months) / float(required_months)
    return round(min(ratio, 1.0), 3)


def check_mandatory_requirements(
    candidate: CandidateProfile,
    job: JobProfile,
    cfg: MatchingConfig = DEFAULT_MATCHING_CONFIG,
    assessments: Optional[List[RequirementAssessment]] = None
) -> Tuple[bool, List[FailedRequirement]]:
    failed = []

    # 1. Experience Constraint
    if job.min_experience_months > 0 and candidate.total_experience_months < job.min_experience_months:
        failed.append(FailedRequirement(
            type="experience",
            required=job.min_experience_months,
            candidate=candidate.total_experience_months,
            message=f"Candidate experience ({candidate.total_experience_months} mos) is below mandatory requirement ({job.min_experience_months} mos)."
        ))

    # 2. Check against evidence-backed requirement assessments if provided
    if assessments:
        must_have_failed = False
        for a in assessments:
            if a.mandatory and a.status not in ["satisfied", "partially_supported"]:
                must_have_failed = True
                failed.append(FailedRequirement(
                    type="must_have_skill",
                    required=a.description or a.requirement_id,
                    candidate=a.status,
                    message=f"Candidate failed mandatory requirement '{a.description}' (status: '{a.status}')."
                ))
        # Mandatory pass is granted if all mandatory technical skills/qualifications are satisfied
        passed = not must_have_failed
        return passed, failed

    # 3. Standalone fallback check
    must_have_set = set()
    for s in job.must_have_skills:
        if s and len(s) < 40 and not any(w in s.lower() for w in ["experience", "years", "building", "proficient"]):
            must_have_set.add(s)
    for req in job.requirements:
        if (req.importance == "must_have" or req.mandatory) and req.skill:
            s = req.skill
            if s and len(s) < 40 and not any(w in s.lower() for w in ["experience", "years", "building", "proficient"]):
                must_have_set.add(s)

    # Allow EXACT, EQUIVALENT, TRANSFERABLE, or RELATED matches for must-have skills
    # Only REJECT completely missing skills
    for req_skill in must_have_set:
        match_detail = classify_skill_match(req_skill, candidate.skills, cfg)
        # Allow: exact, equivalent, transferable, related. Reject only: missing, unrelated
        if match_detail.match_type in ["missing", "unrelated"]:
            failed.append(FailedRequirement(
                type="must_have_skill",
                required=req_skill,
                candidate=match_detail.candidate_skill,
                message=f"Candidate failed mandatory must-have skill '{req_skill}' (match status: '{match_detail.match_type}')."
            ))

    passed = len(failed) == 0
    return passed, failed
