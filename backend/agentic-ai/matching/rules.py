"""
rules.py
Matching rules, strict 5-tier classification hierarchy, mandatory checks, and weighted skill coverage.
"""

import os
import csv
from typing import List, Dict, Any, Tuple, Union
from config.matching_config import DEFAULT_MATCHING_CONFIG, MatchingConfig
from contracts.candidate import CandidateProfile, CandidateSkill
from contracts.job import JobProfile, JobRequirement
from contracts.match import FailedRequirement, SkillMatchDetail
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
    Strict 5-Tier Skill Match Hierarchy:
    1. Exact canonical equality (EXACT) -> score 1.0
    2. Known taxonomy lookup (TRANSFERABLE / RELATED / UNRELATED)
       - If explicitly UNRELATED (e.g. Java vs JavaScript), reject immediately.
       - If explicitly TRANSFERABLE or RELATED, lock in taxonomy classification.
    3. Semantic similarity fallback (ONLY for unknown pairs NOT in taxonomy DB)
       - If sim >= equivalent threshold -> EQUIVALENT
       - If sim >= transferable threshold -> TRANSFERABLE
       - If sim >= related threshold -> RELATED
    4. Missing (MISSING) -> score 0.0
    """
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

        # 2. Known Taxonomy Relationship Lookup
        rel_type, rel_score = get_skill_relationship(req_canonical, cand_canonical)
        
        # Explicitly reject known unrelated skills (e.g. Java vs JavaScript)
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
            # Locked by taxonomy; do not allow embeddings to promote known relationships to 'equivalent'
            continue

        # 3. Semantic Similarity Fallback (ONLY for unknown pairs not in taxonomy DB)
        if rel_type == "unknown":
            sim = semantic_similarity(req_canonical, cand_canonical)
            if sim >= thresholds["equivalent"]:
                if multipliers["equivalent"] > best_match.score:
                    best_match = SkillMatchDetail(
                        required_skill=required_skill,
                        candidate_skill=c_raw,
                        match_type="equivalent",
                        similarity=sim,
                        score=multipliers["equivalent"]
                    )
            elif sim >= thresholds["transferable"]:
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
    """
    Computes weighted skill coverage score (0.0 to 1.0) respecting individual requirement weights.
    Formula: Sum(match_score * requirement_weight) / Sum(requirement_weight)
    """
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


def check_mandatory_requirements(candidate: CandidateProfile, job: JobProfile, cfg: MatchingConfig = DEFAULT_MATCHING_CONFIG) -> Tuple[bool, List[FailedRequirement]]:
    failed = []

    # 1. Experience Constraint
    if job.min_experience_months > 0 and candidate.total_experience_months < job.min_experience_months:
        failed.append(FailedRequirement(
            type="experience",
            required=job.min_experience_months,
            candidate=candidate.total_experience_months,
            message=f"Candidate experience ({candidate.total_experience_months} mos) is below mandatory requirement ({job.min_experience_months} mos)."
        ))

    # Collect must-have skills from job.must_have_skills AND job.requirements where importance='must_have'
    must_have_set = set(job.must_have_skills)
    for req in job.requirements:
        if req.importance == "must_have":
            must_have_set.add(req.skill)

    # 2. Must-Have Skills Constraint (Only exact or equivalent satisfies mandatory check)
    for req_skill in must_have_set:
        match_detail = classify_skill_match(req_skill, candidate.skills, cfg)
        if match_detail.match_type not in ["exact", "equivalent"]:
            failed.append(FailedRequirement(
                type="must_have_skill",
                required=req_skill,
                candidate=match_detail.candidate_skill,
                message=f"Candidate failed mandatory must-have skill '{req_skill}' (match status: '{match_detail.match_type}')."
            ))

    # 3. Mandatory Education Level Constraint
    if job.education_requirements:
        required_edu_level = max([get_degree_level(e) for e in job.education_requirements], default=0)
        cand_edu_level = max([get_degree_level(e.degree) for e in candidate.education], default=0) if candidate.education else 0
        if cand_edu_level < required_edu_level:
            failed.append(FailedRequirement(
                type="education",
                required=job.education_requirements,
                candidate=[e.degree for e in candidate.education] if candidate.education else None,
                message=f"Candidate education level ({cand_edu_level}) is below required level ({required_edu_level})."
            ))

    # 4. Mandatory Certifications Constraint
    if job.certifications:
        cand_certs = set([c.lower() for c in candidate.certifications])
        for req_cert in job.certifications:
            if req_cert.lower() not in cand_certs:
                failed.append(FailedRequirement(
                    type="certification",
                    required=req_cert,
                    candidate=candidate.certifications,
                    message=f"Candidate is missing mandatory certification: '{req_cert}'."
                ))

    passed = len(failed) == 0
    return passed, failed
