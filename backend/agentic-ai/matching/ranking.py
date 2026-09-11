"""
ranking.py
Ranks candidates based on overall match scores and mandatory pass statuses.
"""

from typing import List, Dict, Any
from contracts.match import MatchResult


def rank_candidates(matches: List[MatchResult]) -> List[Dict[str, Any]]:
    sorted_matches = sorted(
        matches,
        key=lambda m: (m.mandatory_pass, m.overall_score),
        reverse=True
    )

    ranked_list = []
    for rank_idx, m in enumerate(sorted_matches, start=1):
        ranked_list.append({
            "rank": rank_idx,
            "candidate_id": m.candidate_id,
            "job_id": m.job_id,
            "overall_score": m.overall_score,
            "mandatory_pass": m.mandatory_pass,
            "confidence_level": m.confidence_level
        })

    return ranked_list
