"""Recruiter Decision & Synthesis Agent."""

import logging
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from app.llm.llm_factory import get_llm, MockLLM
from app.schemas.recruiter import RecruiterSummary
from app.prompts.recruiter_prompt import (
    RECRUITER_SYSTEM_PROMPT,
    RECRUITER_USER_PROMPT,
)

logger = logging.getLogger(__name__)


def generate_recruiter_summary(
    candidate: Dict[str, Any],
    job: Dict[str, Any],
    match_result: Dict[str, Any],
    gaps: Dict[str, Any],
    evidence: Dict[str, Any]
) -> RecruiterSummary:
    """
    Synthesizes the deterministic match score, breakdown, skill gaps,
    and verified evidence into a final executive recruiter briefing.
    
    IMPORTANT: This agent NEVER computes the score; it explains the score.
    """
    cid = candidate.get("candidate_id", "C01")
    jid = job.get("job_id", "J01")
    score = match_result.get("overall_score", 0.0)
    mandatory_pass = match_result.get("mandatory_pass", False)
    breakdown = match_result.get("breakdown", {})

    prompt = ChatPromptTemplate.from_messages([
        ("system", RECRUITER_SYSTEM_PROMPT),
        ("human", RECRUITER_USER_PROMPT)
    ])

    llm = get_llm(temperature=0.2)

    try:
        structured_llm = llm.with_structured_output(RecruiterSummary)
        chain = prompt | structured_llm
        result = chain.invoke({
            "candidate_name": candidate.get("name", f"Candidate {cid}"),
            "total_experience": candidate.get("total_experience_months", 0),
            "skills": ", ".join([s.get("name", "") for s in candidate.get("skills", [])]),
            "job_title": job.get("title", f"Job {jid}"),
            "must_haves": ", ".join(job.get("must_have_skills", [])),
            "preferred": ", ".join(job.get("preferred_skills", [])),
            "overall_score": score,
            "mandatory_pass": "Passed" if mandatory_pass else "Failed Mandatory Criteria",
            "breakdown": str(breakdown),
            "skill_gaps": str(gaps.get("gap_summary", gaps)),
            "evidence": str(evidence.get("items", evidence))
        })
        if isinstance(result, RecruiterSummary):
            return result
        elif isinstance(result, dict):
            return RecruiterSummary.model_validate(result)
    except Exception as e:
        logger.warning(f"Recruiter LLM failed ({e}), using fallback synthesis.")

    fallback_llm = MockLLM().with_structured_output(RecruiterSummary)
    return fallback_llm.invoke({
        "candidate_id": cid,
        "job_id": jid,
        "overall_score": score
    })

