"""
metrics.py
Quantitative evaluation metrics calculation functions (Precision@K, Recall@K, Top-K Overlap, NDCG@K, Spearman Correlation).
"""

import numpy as np
from typing import List, Set, Dict, Any
from scipy.stats import spearmanr


def precision_at_k(recommended_ids: List[str], relevant_ids: Set[str], k: int = 3) -> float:
    top_k = recommended_ids[:k]
    if not top_k:
        return 0.0
    hits = len(set(top_k).intersection(relevant_ids))
    return round(float(hits) / float(k), 3)


def recall_at_k(recommended_ids: List[str], relevant_ids: Set[str], k: int = 3) -> float:
    if not relevant_ids:
        return 1.0
    top_k = recommended_ids[:k]
    hits = len(set(top_k).intersection(relevant_ids))
    return round(float(hits) / float(len(relevant_ids)), 3)


def top_k_overlap(system_top_k: List[str], human_top_k: List[str], k: int = 3) -> float:
    sys_k = set(system_top_k[:k])
    hum_k = set(human_top_k[:k])
    if not sys_k or not hum_k:
        return 0.0
    overlap = len(sys_k.intersection(hum_k))
    return round(float(overlap) / float(k) * 100.0, 1)


def ndcg_at_k(system_ranks: List[str], human_relevance: Dict[str, float], k: int = 3) -> float:
    top_k = system_ranks[:k]
    dcg = 0.0
    for idx, cand_id in enumerate(top_k, start=1):
        rel = human_relevance.get(cand_id, 0.0)
        dcg += (2**rel - 1) / np.log2(idx + 1)

    # Ideal DCG
    ideal_rels = sorted(human_relevance.values(), reverse=True)[:k]
    idcg = 0.0
    for idx, rel in enumerate(ideal_rels, start=1):
        idcg += (2**rel - 1) / np.log2(idx + 1)

    if idcg == 0:
        return 0.0

    return round(float(dcg / idcg), 3)


def spearman_correlation(system_ranks: List[int], human_ranks: List[int]) -> float:
    if len(system_ranks) < 2:
        return 1.0
    corr, _ = spearmanr(system_ranks, human_ranks)
    return round(float(corr) if not np.isnan(corr) else 0.0, 3)
