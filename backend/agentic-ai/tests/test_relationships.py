"""
test_relationships.py
Unit tests for skill relationships (Azure <-> AWS, Flask <-> FastAPI, Java vs JavaScript).
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from nlp.skill_relationships import get_skill_relationship, get_transferability_score


def test_transferable_relationship():
    rel, score = get_skill_relationship("Azure", "AWS")
    assert rel == "transferable"
    assert score == 0.80

    rel_flask, score_flask = get_skill_relationship("Flask", "FastAPI")
    assert rel_flask == "transferable"
    assert score_flask == 0.85


def test_unrelated_skill_pair():
    rel, score = get_skill_relationship("Java", "JavaScript")
    assert rel == "unrelated"
    assert score == 0.05
