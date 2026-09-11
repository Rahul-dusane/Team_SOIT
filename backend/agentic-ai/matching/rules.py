"""
rules.py
Matching rules, strict 5-tier classification hierarchy, mandatory checks, and skill coverage formulas.
"""

import os
import csv
from typing import List, Dict, Any, Tuple
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

        # 1. Exact Canonical Match
        if req_canonical == cand_canonical:
            return SkillMatchDetail(
                required_skill=required_skill,
                candidate_skill=c_raw,
                match_type="exact",
                similarity=1.0,
                score=multipliers["exact"]
            )

        # 2. Known Relationship Taxonomy Lookup
        rel_type, rel_score = get_skill_relationship(req_canonical, cand_canonical)
        if rel_type == "transferable" and rel_score >= thresholds["transferable"]:
            if multipliers["transferable"] > best_match.score:
                best_match = SkillMatchDetail(
                    required_skill=required_skill,
                    candidate_skill=c_raw,
                    match_type="transferable",
                    similarity=rel_score,
                    score=multipliers["transferable"]
                )

        elif rel_type == "related" and rel_score >= thresholds["related"]:
            if multipliers["related"] > best_match.score:
                best_match = SkillMatchDetail(
                    required_skill=required_skill,
                    candidate_skill=c_raw,
                    match_type="related",
                    similarity=rel_score,
                    score=multipliers["related"]
                )

        if rel_type == "unrelated":
            continue

        # 3. Semantic Similarity Fallback
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


def calculate_skill_coverage(required_skills: List[str], candidate_skills: List[CandidateSkill], cfg: MatchingConfig = DEFAULT_MATCHING_CONFIG) -> Tuple[float, List[SkillMatchDetail]]:
    if not required_skills:
        return 1.0, []

    matches = [classify_skill_match(req, candidate_skills, cfg) for req in required_skills]
    total_score = sum(m.score for m in matches)
    coverage = total_score / len(required_skills)
    return round(coverage, 3), matches


def calculate_experience_fit(candidate_months: int, required_months: int) -> float:
    if required_months <= 0:
        return 1.0
    ratio = float(candidate_months) / float(required_months)
    return round(min(ratio, 1.0), 3)


def check_mandatory_requirements(candidate: CandidateProfile, job: JobProfile, cfg: MatchingConfig = DEFAULT_MATCHING_CONFIG) -> Tuple[bool, List[FailedRequirement]]:
    failed = []

    if job.min_experience_months > 0 and candidate.total_experience_months < job.min_experience_months:
        failed.append(FailedRequirement(
            type="experience",
            required=job.min_experience_months,
            candidate=candidate.total_experience_months,
            message=f"Candidate experience ({candidate.total_experience_months} mos) is below mandatory requirement ({job.min_experience_months} mos)."
        ))

    must_have_set = set(job.must_have_skills)
    for req in job.requirements:
        if req.importance == "must_have":
            must_have_set.add(req.skill)

    for req_skill in must_have_set:
        match_detail = classify_skill_match(req_skill, candidate.skills, cfg)
        if match_detail.match_type not in ["exact", "equivalent"]:
            failed.append(FailedRequirement(
                type="must_have_skill",
                required=req_skill,
                candidate=match_detail.candidate_skill,
                message=f"Candidate failed mandatory must-have skill '{req_skill}' (match status: '{match_detail.match_type}')."
            ))

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
