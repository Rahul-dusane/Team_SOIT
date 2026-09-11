"""Skill Gap Analysis Agent."""

import logging
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from app.llm.llm_factory import get_llm, MockLLM
from app.schemas.skill_gap import SkillGapAnalysis
from app.prompts.gap_prompt import (
    SKILL_GAP_SYSTEM_PROMPT,
    SKILL_GAP_USER_PROMPT,
)

logger = logging.getLogger(__name__)


def explain_skill_gaps(
    candidate: Dict[str, Any],
    job: Dict[str, Any],
    match_result: Dict[str, Any]
) -> SkillGapAnalysis:
    """
    Analyzes gaps identified by Member 2's matching engine, discovering
    transferable skills and recommending actionable upskilling paths.
    """
    cid = candidate.get("candidate_id", "C01")
    jid = job.get("job_id", "J01")
    cand_skills = [s.get("name") for s in candidate.get("skills", [])]
    must_skills = job.get("must_have_skills", [])
    pref_skills = job.get("preferred_skills", [])
    gaps = match_result.get("gaps", [])

    prompt = ChatPromptTemplate.from_messages([
        ("system", SKILL_GAP_SYSTEM_PROMPT),
        ("human", SKILL_GAP_USER_PROMPT)
    ])

    llm = get_llm(temperature=0.1)

    try:
        structured_llm = llm.with_structured_output(SkillGapAnalysis)
        chain = prompt | structured_llm
        result = chain.invoke({
            "candidate_id": cid,
            "job_id": jid,
            "candidate_skills": ", ".join(cand_skills) if cand_skills else "None explicitly listed",
            "must_have_skills": ", ".join(must_skills) if must_skills else "None specified",
            "preferred_skills": ", ".join(pref_skills) if pref_skills else "None specified",
            "identified_gaps": ", ".join(gaps) if gaps else "None detected"
        })
        if isinstance(result, SkillGapAnalysis):
            return result
        elif isinstance(result, dict):
            return SkillGapAnalysis.model_validate(result)
    except Exception as e:
        logger.warning(f"Skill gap LLM failed ({e}), using fallback analysis.")

    fallback_llm = MockLLM().with_structured_output(SkillGapAnalysis)
    return fallback_llm.invoke({"candidate_id": cid, "job_id": jid})

