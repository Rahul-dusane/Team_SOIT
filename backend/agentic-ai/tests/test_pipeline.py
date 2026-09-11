"""Integration test for full LangGraph Recruitment Pipeline."""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from tests.test_agents import SAMPLE_RESUME, SAMPLE_JD
except ImportError:
    from test_agents import SAMPLE_RESUME, SAMPLE_JD
from app.workflows.graph import run_pipeline


def test_full_pipeline():
    print("\n==========================================")
    print("Testing Full LangGraph Multi-Agent Pipeline")
    print("==========================================")

    resumes = {"C01": SAMPLE_RESUME}
    jobs = {"J01": SAMPLE_JD}

    result = run_pipeline(resume_texts=resumes, job_texts=jobs)

    assert result["workflow_status"] == "COMPLETED"
    assert "C01" in result["candidate_profiles"]
    assert "J01" in result["job_profiles"]
    assert len(result["match_results"]) > 0

    match = result["match_results"][0]
    print(f"\n1. Match Result:")
    print(f"   - Candidate ID: {match['candidate_id']}")
    print(f"   - Job ID: {match['job_id']}")
    print(f"   - Overall Score: {match['overall_score']}%")
    print(f"   - Mandatory Pass: {match['mandatory_pass']}")
    print(f"   - Score Breakdown: {match['breakdown']}")
    print(f"   - Detected Gaps: {match['gaps']}")

    pair_key = "C01_J01"
    print(f"\n2. Skill Gap Agent Analysis ({pair_key}):")
    gap_info = result["skill_gaps"].get(pair_key, {})
    print(f"   - Critical Gaps: {gap_info.get('critical_gaps')}")
    print(f"   - Transferable Skills: {gap_info.get('transferable_skills')}")
    print(f"   - Summary: {gap_info.get('gap_summary')}")

    print(f"\n3. Evidence Agent Report ({pair_key}):")
    evidence_info = result["evidence"].get(pair_key, {})
    for item in evidence_info.get("items", [])[:3]:
        print(f"   - [{item.get('status')}] {item.get('requirement')}: quote='{item.get('quote')}'")

    print(f"\n4. Recruiter Agent Executive Summary ({pair_key}):")
    recruiter_info = result["recruiter_summaries"].get(pair_key, {})
    print(f"   - Recommendation: {recruiter_info.get('recommendation')}")
    print(f"   - Headline: {recruiter_info.get('headline')}")
    print(f"   - Strengths: {recruiter_info.get('strengths')}")
    print(f"   - Concerns: {recruiter_info.get('concerns')}")
    print(f"   - Interview Questions: {recruiter_info.get('interview_focus')}")

    print("\n Full LangGraph Pipeline integration test completed successfully!")


if __name__ == "__main__":
    test_full_pipeline()

