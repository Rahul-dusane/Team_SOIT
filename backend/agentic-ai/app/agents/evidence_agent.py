"""Evidence Verification Agent."""

import logging
from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from app.llm.llm_factory import get_llm, MockLLM
from app.schemas.evidence import EvidenceReport, RequirementEvidence
from app.prompts.evidence_prompt import (
    EVIDENCE_SYSTEM_PROMPT,
    EVIDENCE_USER_PROMPT,
)

logger = logging.getLogger(__name__)


def extract_evidence(
    candidate: Dict[str, Any],
    job: Dict[str, Any]
) -> EvidenceReport:
    """
    Audits the candidate's resume and extracts direct citations or proofs
    supporting requirements specified in the job description.
    """
    cid = candidate.get("candidate_id", "C01")
    jid = job.get("job_id", "J01")
    reqs = [r.get("requirement", "") for r in job.get("requirements", [])]
    if not reqs:
        reqs = job.get("must_have_skills", []) + job.get("preferred_skills", [])

    prompt = ChatPromptTemplate.from_messages([
        ("system", EVIDENCE_SYSTEM_PROMPT),
        ("human", EVIDENCE_USER_PROMPT)
    ])

    llm = get_llm(temperature=0.0)

    try:
        structured_llm = llm.with_structured_output(EvidenceReport)
        chain = prompt | structured_llm
        result = chain.invoke({
            "candidate_id": cid,
            "job_id": jid,
            "requirements": ", ".join(reqs),
            "candidate_data": str(candidate)
        })
        if isinstance(result, EvidenceReport):
            return result
        elif isinstance(result, dict):
            return EvidenceReport.model_validate(result)
    except Exception as e:
        logger.warning(f"Evidence LLM failed ({e}), using fallback evidence extractor.")

    fallback_llm = MockLLM().with_structured_output(EvidenceReport)
    return fallback_llm.invoke({"candidate_id": cid, "job_id": jid})

