"""
scorer.py
Domain-Independent Requirement-Level Scorer and Score Breakdown calculator.
Computes traceable requirement-level scores bounded strictly between 0.0 and 100.0,
ensuring breakdown components sum exactly to the raw_score.
"""

from typing import Tuple, List
from config.matching_config import DEFAULT_MATCHING_CONFIG, MatchingConfig
from contracts.match import FeatureBreakdown, ScoreBreakdown, RequirementAssessment


def calculate_match_score(features: FeatureBreakdown, assessments: List[RequirementAssessment] = None, cfg: MatchingConfig = DEFAULT_MATCHING_CONFIG) -> Tuple[float, ScoreBreakdown]:
    """
    Calculates overall score (0.0 to 100.0) and explicit breakdown.
    If requirement assessments are provided, derives total score from requirement-level assessments
    and maps requirement category score contributions into the ScoreBreakdown object.
    """
    if assessments and len(assessments) > 0:
        total_weight = sum(a.weight for a in assessments)
        total_score_contrib = sum(a.score_contribution for a in assessments)
        
        raw_score = (total_score_contrib / total_weight * 100.0) if total_weight > 0 else 100.0
        raw_score = round(min(100.0, max(0.0, raw_score)), 2)

        # Map requirement category contributions directly to breakdown fields
        must_have_contrib = sum(a.score_contribution for a in assessments if a.category == "competency" and a.mandatory)
        pref_contrib = sum(a.score_contribution for a in assessments if a.category == "competency" and not a.mandatory)
        edu_contrib = sum(a.score_contribution for a in assessments if a.category == "qualification")
        cert_contrib = sum(a.score_contribution for a in assessments if a.category == "certification")
        exp_contrib = sum(a.score_contribution for a in assessments if a.category == "experience_duration")
        resp_contrib = sum(a.score_contribution for a in assessments if a.category == "responsibility")

        # Scale contributions so breakdown sum equals raw_score exactly
        scale = (raw_score / total_score_contrib) if total_score_contrib > 0 else 1.0

        breakdown = ScoreBreakdown(
            must_have=round(must_have_contrib * scale, 2),
            preferred=round(pref_contrib * scale, 2),
            experience=round(exp_contrib * scale, 2),
            role=round(resp_contrib * scale, 2),
            semantic=round(cert_contrib * scale, 2),
            education=round(edu_contrib * scale, 2),
            projects=0.0,
            domain=0.0
        )
        return raw_score, breakdown

    weights = cfg.scoring_weights
    breakdown = ScoreBreakdown(
        must_have=round(features.must_have_coverage * weights.get("must_have", 30.0), 2),
        preferred=round(features.preferred_coverage * weights.get("preferred", 15.0), 2),
        experience=round(features.experience_fit * weights.get("experience", 20.0), 2),
        role=round(features.role_similarity * weights.get("role", 10.0), 2),
        semantic=round(features.semantic_similarity * weights.get("semantic", 10.0), 2),
        education=round(features.education_match * weights.get("education", 5.0), 2),
        projects=round(features.project_relevance * weights.get("projects", 5.0), 2),
        domain=round(features.domain_match * weights.get("domain", 5.0), 2)
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

    overall_score = round(min(100.0, max(0.0, overall_score)), 2)
    return overall_score, breakdown
