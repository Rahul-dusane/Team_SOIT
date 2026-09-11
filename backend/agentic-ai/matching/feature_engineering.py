"""
feature_engineering.py
Generates 8 core numerical features for a candidate-job pair, integrating individual requirement weights and role normalization.
"""

from typing import Dict, Any, Tuple, List
from config.matching_config import DEFAULT_MATCHING_CONFIG, MatchingConfig
from contracts.candidate import CandidateProfile
from contracts.job import JobProfile, JobRequirement
from contracts.match import FeatureBreakdown, SkillMatchDetail
from matching.rules import calculate_skill_coverage, calculate_experience_fit, get_degree_level
from nlp.role_normalizer import normalize_role
from nlp.similarity import semantic_similarity


def build_features(candidate: CandidateProfile, job: JobProfile, cfg: MatchingConfig = DEFAULT_MATCHING_CONFIG) -> Tuple[FeatureBreakdown, List[SkillMatchDetail]]:
    """
    Computes candidate-job feature matrix.
    Incorporates individual requirement weights from job.requirements alongside must_have_skills & preferred_skills.
    """
    must_have_reqs: List[Union[str, JobRequirement]] = []
    preferred_reqs: List[Union[str, JobRequirement]] = []

    # 1. Process structured job.requirements if present
    seen_must_have = set()
    seen_preferred = set()

    for req in job.requirements:
        if req.importance == "must_have":
            must_have_reqs.append(req)
            seen_must_have.add(req.skill.lower())
        elif req.importance in ["preferred", "nice_to_have"]:
            preferred_reqs.append(req)
            seen_preferred.add(req.skill.lower())

    # Add legacy separate must_have_skills if not already in requirements
    for s in job.must_have_skills:
        if s.lower() not in seen_must_have:
            must_have_reqs.append(s)
            seen_must_have.add(s.lower())

    # Add legacy separate preferred_skills if not already in requirements
    for s in job.preferred_skills:
        if s.lower() not in seen_preferred:
            preferred_reqs.append(s)
            seen_preferred.add(s.lower())

    must_have_cov, must_have_matches = calculate_skill_coverage(must_have_reqs, candidate.skills, cfg)
    preferred_cov, preferred_matches = calculate_skill_coverage(preferred_reqs, candidate.skills, cfg)

    all_skill_matches = must_have_matches + preferred_matches

    exp_fit = calculate_experience_fit(candidate.total_experience_months, job.min_experience_months)

    job_norm_role = normalize_role(job.title)
    if candidate.experiences:
        cand_roles = " ".join([normalize_role(e.role) for e in candidate.experiences])
        role_sim = semantic_similarity(job_norm_role, cand_roles)
    else:
        role_sim = 0.0

    job_desc = f"{job.title} {job.description} " + " ".join(job.responsibilities)
    cand_text = " ".join([f"{e.role} {e.description}" for e in candidate.experiences])
    cand_text += " " + " ".join([f"{p.title} {p.description}" for p in candidate.projects])
    sem_sim = semantic_similarity(job_desc, cand_text) if cand_text.strip() else 0.0

    if job.education_requirements:
        required_edu_level = max([get_degree_level(e) for e in job.education_requirements], default=3)
        cand_edu_level = max([get_degree_level(e.degree) for e in candidate.education], default=0) if candidate.education else 0
        edu_match = 1.0 if cand_edu_level >= required_edu_level else (round(cand_edu_level / float(required_edu_level), 2) if required_edu_level > 0 else 0.0)
    else:
        edu_match = 1.0

    if candidate.projects:
        proj_text = " ".join([f"{p.title} {p.description} " + " ".join(p.technologies) for p in candidate.projects])
        proj_rel = semantic_similarity(job.description or job.title, proj_text)
    else:
        proj_rel = 0.0

    if not job.domain or not candidate.domains:
        domain_match = 0.0
    else:
        shared = set([d.lower() for d in job.domain]).intersection(set([d.lower() for d in candidate.domains]))
        domain_match = 1.0 if shared else 0.0

    features = FeatureBreakdown(
        must_have_coverage=must_have_cov,
        preferred_coverage=preferred_cov,
        experience_fit=exp_fit,
        role_similarity=role_sim,
        semantic_similarity=sem_sim,
        education_match=edu_match,
        project_relevance=proj_rel,
        domain_match=domain_match
    )

    return features, all_skill_matches
