"""
test_gap_engine.py
Unit tests for skill gap categorization (critical, moderate, optional, transferable).
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from contracts.candidate import CandidateProfile, CandidateSkill
from contracts.job import JobProfile
from matching.rules import classify_skill_match
from matching.gap_engine import find_skill_gaps


def test_gap_engine_categorization():
    job = JobProfile(
        job_id="J01",
        title="Cloud Backend Developer",
        must_have_skills=["Python", "Kubernetes"],
        preferred_skills=["Redis"]
    )

    candidate = CandidateProfile(
        candidate_id="C01",
        skills=[CandidateSkill(raw_skill="Python")]
    )

    matches = [
        classify_skill_match("Python", candidate.skills),
        classify_skill_match("Kubernetes", candidate.skills),
        classify_skill_match("Redis", candidate.skills)
    ]

    gaps = find_skill_gaps(candidate, job, matches)
    assert "Kubernetes" in gaps.critical
    assert "Redis" in gaps.moderate
