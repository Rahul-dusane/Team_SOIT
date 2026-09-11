"""
scorer.py
100-Point Weighted Scoring Engine and score breakdown calculator.
"""

from typing import Tuple
from config.matching_config import DEFAULT_MATCHING_CONFIG, MatchingConfig
from contracts.match import FeatureBreakdown, ScoreBreakdown


def calculate_match_score(features: FeatureBreakdown, cfg: MatchingConfig = DEFAULT_MATCHING_CONFIG) -> Tuple[float, ScoreBreakdown]:
    weights = cfg.scoring_weights

    breakdown = ScoreBreakdown(
        must_have=round(features.must_have_coverage * weights["must_have"], 2),
        preferred=round(features.preferred_coverage * weights["preferred"], 2),
        experience=round(features.experience_fit * weights["experience"], 2),
        role=round(features.role_similarity * weights["role"], 2),
        semantic=round(features.semantic_similarity * weights["semantic"], 2),
        education=round(features.education_match * weights["education"], 2),
        projects=round(features.project_relevance * weights["projects"], 2),
        domain=round(features.domain_match * weights["domain"], 2)
    )

    overall_score = round(
        breakdown.must_have +
        breakdown.preferred +
        breakdown.experience +
        breakdown.role +
        breakdown.semantic +
        breakdown.education +
        breakdown.projects +
        breakdown.domain,
        2
    )

    return overall_score, breakdown
