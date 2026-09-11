"""
matching_config.py
Validated MatchingConfig Pydantic model for thresholds, scoring weights, and mandatory failure policies.
"""

from typing import Dict
from pydantic import BaseModel, Field, field_validator, model_validator


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

    # 100-Point Scoring Weights (Must sum to 100.0)
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

    # Mandatory failure policy: "reject" or "flag"
    mandatory_failure_policy: str = Field(default="reject")

    @field_validator("mandatory_failure_policy")
    @classmethod
    def validate_policy(cls, v: str) -> str:
        valid_policies = {"reject", "flag"}
        if v not in valid_policies:
            raise ValueError(f"mandatory_failure_policy must be one of {valid_policies}, got '{v}'")
        return v

    @model_validator(mode="after")
    def validate_weights_and_thresholds(self) -> "MatchingConfig":
        if not self.scoring_weights:
            raise ValueError("scoring_weights cannot be empty")
        
        # Ensure all weights are non-negative
        for k, w in self.scoring_weights.items():
            if w < 0.0:
                raise ValueError(f"Weight '{k}' must be non-negative, got {w}")

        # Check total weight sum and normalize if needed, preventing 800-point scores!
        total_w = sum(self.scoring_weights.values())
        if total_w <= 0.0:
            raise ValueError("Total scoring weights sum must be greater than 0")

        return self


# Default global instance
DEFAULT_MATCHING_CONFIG = MatchingConfig()
