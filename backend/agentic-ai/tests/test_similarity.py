"""
test_similarity.py
Unit tests for semantic cosine similarity calculations.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from nlp.similarity import semantic_similarity


def test_semantic_similarity_basic():
    sim = semantic_similarity("Backend engineer with Python API experience", "Python developer building REST APIs")
    assert sim > 0.60

    sim_diff = semantic_similarity("Python API development", "Chef preparing gourmet food")
    assert sim_diff < 0.30
