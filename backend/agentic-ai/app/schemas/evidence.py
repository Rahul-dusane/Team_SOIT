"""Evidence verification schema for Evidence Agent."""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class RequirementEvidence(BaseModel):
    requirement: str = Field(description="The job requirement being verified")
    status: Literal["VERIFIED", "PARTIALLY_VERIFIED", "NOT_FOUND"] = Field(
        description="Verification state of this requirement in the candidate's resume"
    )
    quote: Optional[str] = Field(
        default=None,
        description="Exact quote or excerpt from the resume serving as verifiable proof"
    )
    context_source: Optional[str] = Field(
        default=None,
        description="Source section where evidence was found (e.g. 'Project: Distributed API', 'Experience at Acme')"
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence score for this evidence match"
    )


class EvidenceReport(BaseModel):
    candidate_id: str
    job_id: str
    items: List[RequirementEvidence] = Field(
        default_factory=list,
        description="List of verified evidence items for all key job requirements"
    )

