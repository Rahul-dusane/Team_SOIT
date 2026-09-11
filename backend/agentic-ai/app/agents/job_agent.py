"""Job Specification Extraction Agent."""

import logging
from langchain_core.prompts import ChatPromptTemplate
from app.llm.llm_factory import get_llm, MockLLM
from app.schemas.job import JobProfile
from app.prompts.job_prompt import (
    JOB_EXTRACTION_SYSTEM_PROMPT,
    JOB_EXTRACTION_USER_PROMPT,
)

logger = logging.getLogger(__name__)


def extract_job_profile(job_id: str, job_text: str) -> JobProfile:
    """
    Extracts structured requirements, weights, and criteria from raw job description text.
    Validates strictly against JobProfile Pydantic schema.
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", JOB_EXTRACTION_SYSTEM_PROMPT),
        ("human", JOB_EXTRACTION_USER_PROMPT)
    ])

    llm = get_llm(temperature=0.0)

    # 1. Attempt structured LLM extraction
    try:
        structured_llm = llm.with_structured_output(JobProfile)
        chain = prompt | structured_llm
        result = chain.invoke({
            "job_id": job_id,
            "job_text": job_text
        })
        if isinstance(result, JobProfile):
            return result
        elif isinstance(result, dict):
            return JobProfile.model_validate(result)
    except Exception as e:
        logger.warning(f"LLM extraction failed ({e}), falling back to structured parser.")

    # 2. Fallback execution with mock / deterministic parser
    fallback_llm = MockLLM().with_structured_output(JobProfile)
    return fallback_llm.invoke({
        "job_id": job_id,
        "job_text": job_text
    })

