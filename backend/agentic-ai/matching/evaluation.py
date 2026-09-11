"""
evaluation.py
Evaluation engine running ground_truth benchmark experiments without artificial substitution.
"""

import os
from typing import Dict, List, Any
import pandas as pd
from .metrics import precision_at_k, recall_at_k, top_k_overlap, ndcg_at_k, spearman_correlation


def load_ground_truth(csv_path: str) -> Dict[str, Dict[str, Any]]:
    """
    Loads ground_truth.csv. Returns dict mapping job_id to human ranking details.
    """
    data = {}
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        for job_id, group in df.groupby("job_id"):
            sorted_group = group.sort_values("human_rank")
            human_top_3 = sorted_group["candidate_id"].head(3).tolist()
            relevance_map = {}
            for _, row in group.iterrows():
                label = row["human_label"]
                rel = 3.0 if label == "strong" else (2.0 if label == "medium" else 1.0)
                relevance_map[row["candidate_id"]] = rel

            data[job_id] = {
                "human_top_3": human_top_3,
                "human_relevance": relevance_map,
                "human_ranks": dict(zip(group["candidate_id"], group["human_rank"]))
            }
    return data


def evaluate_batch_results(batch_results: Dict[str, Any], ground_truth_path: str = None) -> pd.DataFrame:
    """
    Evaluates system rankings against ground truth data for each job.
    If ground truth is missing for a job, metrics reflect missing evaluation data (N/A) rather than substituting system rankings.
    """
    if ground_truth_path is None:
        ground_truth_path = os.path.join(os.path.dirname(__file__), "..", "datasets", "ground_truth.csv")

    gt_data = load_ground_truth(ground_truth_path)
    eval_rows = []

    for job_id, job_res in batch_results.items():
        sys_rankings = job_res["rankings"]
        sys_top_3 = [r["candidate_id"] for r in sys_rankings[:3]]

        gt = gt_data.get(job_id)
        if not gt:
            eval_rows.append({
                "Job ID": job_id,
                "Human Top-3": "NO GROUND TRUTH",
                "System Top-3": ", ".join(sys_top_3),
                "Overlap %": "N/A",
                "Precision@3": "N/A",
                "Recall@3": "N/A",
                "NDCG@3": "N/A",
                "Spearman": "N/A"
            })
            continue

        hum_top_3 = gt["human_top_3"]
        hum_rel = gt["human_relevance"]
        hum_ranks_map = gt["human_ranks"]

        relevant_set = set([c for c, rel in hum_rel.items() if rel >= 2.0])

        prec = precision_at_k(sys_top_3, relevant_set, k=3)
        rec = recall_at_k(sys_top_3, relevant_set, k=3)
        overlap = top_k_overlap(sys_top_3, hum_top_3, k=3)
        ndcg = ndcg_at_k([r["candidate_id"] for r in sys_rankings], hum_rel, k=3)

        sys_rank_nums = [r["rank"] for r in sys_rankings]
        hum_rank_nums = [hum_ranks_map.get(r["candidate_id"], 99) for r in sys_rankings]
        spearman = spearman_correlation(sys_rank_nums, hum_rank_nums)

        eval_rows.append({
            "Job ID": job_id,
            "Human Top-3": ", ".join(hum_top_3),
            "System Top-3": ", ".join(sys_top_3),
            "Overlap %": f"{overlap}%",
            "Precision@3": prec,
            "Recall@3": rec,
            "NDCG@3": ndcg,
            "Spearman": spearman
        })

    return pd.DataFrame(eval_rows)
