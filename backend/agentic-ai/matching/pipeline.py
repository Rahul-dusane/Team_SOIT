"""
pipeline.py
Unified single candidate-job matching pipeline with PII-safe filtering, mandatory constraint policy enforcement, and confidence classification.
"""

from typing import Dict, Any, List
from contracts.candidate import CandidateProfile, CandidateSkill
from contracts.job import JobProfile
from contracts.match import MatchResult
from matching.feature_filter import build_scoring_profile
from matching.rules import check_mandatory_requirements
from matching.feature_engineering import build_features
from matching.scorer import calculate_match_score
from matching.gap_engine import find_skill_gaps
from config.matching_config import DEFAULT_MATCHING_CONFIG, MatchingConfig


def match_candidate_to_job(candidate: CandidateProfile, job: JobProfile, cfg: MatchingConfig = DEFAULT_MATCHING_CONFIG) -> MatchResult:
    if not candidate:
        raise ValueError("Candidate profile cannot be None")
    if not job:
        raise ValueError("Job profile cannot be None")

    # 1. PII-Safe Filtering (Strips name/email/phone and sanitizes free text)
    sanitized_dict = build_scoring_profile(candidate)
    sanitized_candidate = CandidateProfile(**sanitized_dict)

    # 2. Mandatory Constraint Check
    mandatory_pass, failed_reqs = check_mandatory_requirements(sanitized_candidate, job, cfg)

    # 3. Feature Extraction using Sanitized Candidate
    features, skill_matches = build_features(sanitized_candidate, job, cfg)

    # 4. Score Calculation
    overall_score, breakdown = calculate_match_score(features, cfg)

    # 5. Mandatory Failure Policy Enforcement
    if not mandatory_pass:
        if cfg.mandatory_failure_policy == "reject":
            overall_score = 0.0
            confidence = "REJECTED (Mandatory Failed)"
        else:
            confidence = "FLAGGED (Mandatory Failed)"
    else:
        # 6. Confidence Classification based on Extracted Skill Evidence Reliability
        skill_confidences = [s.confidence for s in candidate.skills if hasattr(s, "confidence")]
        avg_skill_confidence = sum(skill_confidences) / len(skill_confidences) if skill_confidences else 1.0

        high_thresh = cfg.confidence_thresholds["high"]
        med_thresh = cfg.confidence_thresholds["medium"]

        if avg_skill_confidence >= high_thresh and overall_score >= 80.0:
            confidence = "HIGH"
        elif avg_skill_confidence >= med_thresh or overall_score >= 60.0:
            confidence = "MEDIUM"
        else:
            confidence = "LOW (Needs Review)"

    # 7. Skill Gap Analysis
    gaps = find_skill_gaps(sanitized_candidate, job, skill_matches)

    return MatchResult(
        candidate_id=candidate.candidate_id,
        job_id=job.job_id,
        overall_score=overall_score,
        mandatory_pass=mandatory_pass,
        confidence_level=confidence,
        failed_requirements=failed_reqs,
        features=features,
        score_breakdown=breakdown,
        skill_matches=skill_matches,
        skill_gaps=gaps
    )
