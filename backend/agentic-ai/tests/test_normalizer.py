"""
test_normalizer.py
Unit tests for skill normalization (Postgres -> PostgreSQL, K8s -> Kubernetes, ReactJS -> React).
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from nlp.skill_normalizer import normalize_skill


def test_alias_normalization():
    res1 = normalize_skill("Postgres")
    assert res1["canonical"] == "PostgreSQL"
    assert res1["confidence"] == 1.0

    res2 = normalize_skill("k8s")
    assert res2["canonical"] == "Kubernetes"

    res3 = normalize_skill("reactjs")
    assert res3["canonical"] == "React"

    res4 = normalize_skill("gcp")
    assert res4["canonical"] == "Google Cloud Platform"


def test_fuzzy_normalization():
    res = normalize_skill("Postgre SQL")
    assert res["canonical"] == "PostgreSQL"
