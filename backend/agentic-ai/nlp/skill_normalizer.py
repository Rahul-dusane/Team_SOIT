"""
skill_normalizer.py
Domain-Independent Skill Normalization Engine supporting arbitrary skills (IT, Accounting, Healthcare, etc.).
Preserves raw text and flags uncertain normalization without forcing technical mappings.
"""

import os
import csv
from typing import Dict, Any, List
from rapidfuzz import process, fuzz
from nlp.aliases import lookup_alias

# Base canonical skills list
CANONICAL_SKILLS: List[str] = [
    "Python", "JavaScript", "TypeScript", "Java", "C++", "Go", "Rust",
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite",
    "FastAPI", "Flask", "Django", "React", "Angular", "Vue.js", "Node.js", "Express.js",
    "Docker", "Kubernetes", "AWS", "Azure", "Google Cloud Platform",
    "TensorFlow", "PyTorch", "scikit-learn", "Pandas", "NumPy", "spaCy",
    "LangChain", "LangGraph",
    "Bookkeeping", "Financial Accounting", "CPA", "Tax Auditing", "Cost Accounting",
    "Clinical Nursing", "Patient Care", "Phlebotomy", "CPR", "Vital Signs",
    "AutoCAD", "Structural Engineering", "Project Management", "Agile"
]


def load_canonical_skills_from_csv(csv_path: str) -> List[str]:
    if os.path.exists(csv_path):
        skills = []
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                skills.append(row["canonical_name"].strip())
        return list(set(skills))
    return CANONICAL_SKILLS


_csv_file = os.path.join(os.path.dirname(__file__), "..", "datasets", "skills.csv")
CANONICAL_LIST = load_canonical_skills_from_csv(_csv_file)


def normalize_skill(skill_str: str) -> Dict[str, Any]:
    """
    Normalizes any skill string across any domain to its canonical form.
    Preserves raw text and handles unfamiliar skills safely.
    Returns:
        {
            "raw": skill_str,
            "canonical": canonical_name,
            "confidence": confidence_float (0.0 to 1.0)
        }
    """
    if not skill_str or not isinstance(skill_str, str):
        return {"raw": str(skill_str), "canonical": "Unknown", "confidence": 0.0}

    raw_clean = skill_str.strip()
    
    # Tier 1: Direct Alias Lookup
    alias_match = lookup_alias(raw_clean)
    if alias_match in CANONICAL_LIST or alias_match != raw_clean:
        return {
            "raw": raw_clean,
            "canonical": alias_match,
            "confidence": 1.0
        }

    # Tier 2: Exact Case-Insensitive Match against Canonical List
    raw_lower = raw_clean.lower()
    for c_skill in CANONICAL_LIST:
        if c_skill.lower() == raw_lower:
            return {
                "raw": raw_clean,
                "canonical": c_skill,
                "confidence": 1.0
            }

    # Tier 3: High-Confidence RapidFuzz Matching (threshold 85 to prevent bad cross-domain mappings)
    match_result = process.extractOne(raw_clean, CANONICAL_LIST, scorer=fuzz.WRatio)
    if match_result and match_result[1] >= 85.0:
        canonical_name = match_result[0]
        confidence = float(match_result[1]) / 100.0
        return {
            "raw": raw_clean,
            "canonical": canonical_name,
            "confidence": round(confidence, 2)
        }

    # Fallback for Unfamiliar Skills: Preserve raw skill in Title Case safely!
    return {
        "raw": raw_clean,
        "canonical": raw_clean.title(),
        "confidence": 0.60
    }
