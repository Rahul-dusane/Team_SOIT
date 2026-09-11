"""
test_batch_matcher.py
Unit tests for batch matching across 10 candidates x 3 jobs.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from contracts.candidate import CandidateProfile, CandidateSkill
from contracts.job import JobProfile
from matching.batch_matcher import match_candidates_to_job, match_all


def test_batch_matching_10x3():
    candidates = [
        CandidateProfile(candidate_id=f"C{i:02d}", total_experience_months=12 * i, skills=[CandidateSkill(raw_skill="Python"), CandidateSkill(raw_skill="PostgreSQL")])
        for i in range(1, 11)
    ]

    jobs = [
        JobProfile(job_id="J01", title="Backend Dev", must_have_skills=["Python"]),
        JobProfile(job_id="J02", title="Database Dev", must_have_skills=["PostgreSQL"]),
        JobProfile(job_id="J03", title="Senior Engineer", min_experience_months=60, must_have_skills=["Python"])
    ]

    batch_output = match_all(candidates, jobs)
    assert len(batch_output) == 3
    assert len(batch_output["J01"]["rankings"]) == 10
    assert len(batch_output["J02"]["rankings"]) == 10
    assert len(batch_output["J03"]["rankings"]) == 10
