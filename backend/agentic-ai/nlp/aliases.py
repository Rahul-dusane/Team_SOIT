"""
aliases.py
Skill alias loader and lookup service.
"""

import os
import csv
from typing import Dict

# Default fallback dictionary
SKILL_ALIASES: Dict[str, str] = {
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "postgres sql": "PostgreSQL",
    "pg": "PostgreSQL",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "reactjs": "React",
    "react.js": "React",
    "react": "React",
    "gcp": "Google Cloud Platform",
    "google cloud": "Google Cloud Platform",
    "aws": "AWS",
    "amazon web services": "AWS",
    "azure": "Azure",
    "py": "Python",
    "python3": "Python",
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "tf": "TensorFlow",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "torch": "PyTorch",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "node": "Node.js",
    "nodejs": "Node.js",
    "docker": "Docker",
    "redis": "Redis",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "sklearn": "scikit-learn",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "spacy": "spaCy",
    "langchain": "LangChain",
    "langgraph": "LangGraph",
}


def load_aliases_from_csv(csv_path: str) -> Dict[str, str]:
    aliases = dict(SKILL_ALIASES)
    if os.path.exists(csv_path):
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                alias = row["alias"].strip().lower()
                canonical = row["canonical"].strip()
                aliases[alias] = canonical
    return aliases


# Try loading from datasets/aliases.csv relative to this file
_csv_file = os.path.join(os.path.dirname(__file__), "..", "datasets", "aliases.csv")
ALIASES_MAP = load_aliases_from_csv(_csv_file)


def lookup_alias(skill_str: str) -> str:
    cleaned = skill_str.strip().lower()
    return ALIASES_MAP.get(cleaned, skill_str.strip())
