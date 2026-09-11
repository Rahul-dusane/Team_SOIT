"""
batch_matcher.py
Robust batch matching engine processing candidate-job matches with per-candidate exception isolation.
"""

from typing import List, Dict, Any
import logging
from contracts.candidate import CandidateProfile
from contracts.job import JobProfile
from contracts.match import MatchResult
from matching.pipeline import match_candidate_to_job
from matching.ranking import rank_candidates
from config.matching_config import DEFAULT_MATCHING_CONFIG, MatchingConfig

logger = logging.getLogger(__name__)


def match_candidates_to_job(candidates: List[CandidateProfile], job: JobProfile, cfg: MatchingConfig = DEFAULT_MATCHING_CONFIG) -> Dict[str, Any]:
    matches: List[MatchResult] = []
    errors: List[Dict[str, Any]] = []

    for c in candidates:
        try:
            res = match_candidate_to_job(c, job, cfg)
            matches.append(res)
        except Exception as e:
            logger.error(f"Error matching candidate {getattr(c, 'candidate_id', 'unknown')} for job {job.job_id}: {str(e)}")
            errors.append({
                "candidate_id": getattr(c, 'candidate_id', 'unknown'),
                "error": str(e)
            })

    ranked = rank_candidates(matches)
    return {
        "job_id": job.job_id,
        "job_title": job.title,
        "total_candidates": len(candidates),
        "successful_matches": len(matches),
        "errors": errors,
        "rankings": ranked,
        "matches": matches
    }


def match_all(candidates: List[CandidateProfile], jobs: List[JobProfile], cfg: MatchingConfig = DEFAULT_MATCHING_CONFIG) -> Dict[str, Any]:
    batch_results = {}
    for job in jobs:
        batch_results[job.job_id] = match_candidates_to_job(candidates, job, cfg)
    return batch_results
