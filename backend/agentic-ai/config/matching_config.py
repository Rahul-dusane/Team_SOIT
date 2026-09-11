"""
matching_config.py
Validated MatchingConfig Pydantic model for thresholds, scoring weights, and mandatory failure policies.
"""

from typing import Dict
from pydantic import BaseModel, Field


class MatchingConfig(BaseModel):

    # Similarity thresholds for skill matching tiers
    matching_thresholds: Dict[str, float] = Field(default_factory=lambda: {
        "equivalent": 0.92,
        "transferable": 0.78,
        "related": 0.65,
    })

    # Score multipliers per tier
    tier_score_multipliers: Dict[str, float] = Field(default_factory=lambda: {
        "exact": 1.00,
        "equivalent": 1.00,
        "transferable": 0.70,
        "related": 0.40,
        "missing": 0.00,
    })

    # 100-Point Scoring Weights
    scoring_weights: Dict[str, float] = Field(default_factory=lambda: {
        "must_have": 30.0,
        "preferred": 15.0,
        "experience": 20.0,
        "role": 10.0,
        "semantic": 10.0,
        "education": 5.0,
        "projects": 5.0,
        "domain": 5.0,
    })

    # Confidence classification thresholds for evidence reliability
    confidence_thresholds: Dict[str, float] = Field(default_factory=lambda: {
        "high": 0.90,
        "medium": 0.70,
    })

    # Mandatory failure policy: "reject" (fails mandatory_pass) or "flag"
    mandatory_failure_policy: str = "reject"


# Default global instance
DEFAULT_MATCHING_CONFIG = MatchingConfig()
