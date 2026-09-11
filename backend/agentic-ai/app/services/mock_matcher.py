"""Matching Engine bridge delegating to Member 2's deterministic scoring contract."""

from typing import Dict, Any
from contracts.candidate import CandidateProfile
from contracts.job import JobProfile
from matching.pipeline import match_candidate_to_job as real_match_candidate_to_job


def match_candidate_to_job(candidate_data: Dict[str, Any], job_data: Dict[str, Any]) -> Any:
    """Delegates directly to Member 2's production matching engine."""
    cand_obj = CandidateProfile.model_validate(candidate_data) if isinstance(candidate_data, dict) else candidate_data
    job_obj = JobProfile.model_validate(job_data) if isinstance(job_data, dict) else job_data
    return real_match_candidate_to_job(cand_obj, job_obj)


