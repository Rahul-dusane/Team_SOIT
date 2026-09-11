"""
skill_relationships.py
Skill relationship knowledge base for technology transferability and relationship classification.
"""

import os
import csv
from typing import Dict, Tuple, Any

# Relationship mapping: (skill_a_lower, skill_b_lower) -> (relationship_type, transferability_score)
RELATIONSHIPS_DB: Dict[Tuple[str, str], Tuple[str, float]] = {
    ("azure", "aws"): ("transferable", 0.80),
    ("aws", "azure"): ("transferable", 0.80),
    ("google cloud platform", "aws"): ("transferable", 0.80),
    ("aws", "google cloud platform"): ("transferable", 0.80),
    ("flask", "fastapi"): ("transferable", 0.85),
    ("fastapi", "flask"): ("transferable", 0.85),
    ("django", "fastapi"): ("transferable", 0.80),
    ("fastapi", "django"): ("transferable", 0.80),
    ("tensorflow", "pytorch"): ("transferable", 0.75),
    ("pytorch", "tensorflow"): ("transferable", 0.75),
    ("mysql", "postgresql"): ("related", 0.70),
    ("postgresql", "mysql"): ("related", 0.70),
    ("angular", "react"): ("related", 0.55),
    ("react", "angular"): ("related", 0.55),
    ("vue.js", "react"): ("related", 0.60),
    ("react", "vue.js"): ("related", 0.60),
    ("java", "javascript"): ("unrelated", 0.05),
    ("javascript", "java"): ("unrelated", 0.05),
    ("docker", "kubernetes"): ("related", 0.75),
}


def load_relationships_from_csv(csv_path: str) -> Dict[Tuple[str, str], Tuple[str, float]]:
    db = dict(RELATIONSHIPS_DB)
    if os.path.exists(csv_path):
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                src = row["source_skill"].strip().lower()
                tgt = row["target_skill"].strip().lower()
                rel = row["relationship"].strip().lower()
                score = float(row["transferability"])
                db[(src, tgt)] = (rel, score)
    return db


_csv_file = os.path.join(os.path.dirname(__file__), "..", "datasets", "skill_relationships.csv")
SKILL_RELATIONSHIPS_MAP = load_relationships_from_csv(_csv_file)


def get_skill_relationship(skill_a: str, skill_b: str) -> Tuple[str, float]:
    """
    Returns (relationship_type, score) between two skills.
    Relationship types: 'exact', 'equivalent', 'transferable', 'related', 'unrelated'
    """
    a_lower = skill_a.strip().lower()
    b_lower = skill_b.strip().lower()

    if a_lower == b_lower:
        return ("exact", 1.0)

    key = (a_lower, b_lower)
    if key in SKILL_RELATIONSHIPS_MAP:
        return SKILL_RELATIONSHIPS_MAP[key]

    return ("unrelated", 0.0)


def get_transferability_score(skill_a: str, skill_b: str) -> float:
    """Returns numeric transferability score (0.0 to 1.0)."""
    _, score = get_skill_relationship(skill_a, skill_b)
    return score
