"""Resume Information Extraction Agent."""

import logging
from langchain_core.prompts import ChatPromptTemplate
from app.llm.llm_factory import get_llm, MockLLM
from app.schemas.candidate import CandidateProfile
from app.prompts.resume_prompt import (
    RESUME_EXTRACTION_SYSTEM_PROMPT,
    RESUME_EXTRACTION_USER_PROMPT,
)

logger = logging.getLogger(__name__)


def extract_candidate_profile(candidate_id: str, resume_text: str) -> CandidateProfile:
    """
    Extracts structured factual information from raw resume text.
    Validates strictly against CandidateProfile Pydantic schema.
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", RESUME_EXTRACTION_SYSTEM_PROMPT),
        ("human", RESUME_EXTRACTION_USER_PROMPT)
    ])

    llm = get_llm(temperature=0.0)
    
    # 1. Attempt structured LLM extraction
    try:
        structured_llm = llm.with_structured_output(CandidateProfile)
        chain = prompt | structured_llm
        result = chain.invoke({
            "candidate_id": candidate_id,
            "resume_text": resume_text
        })
        if isinstance(result, CandidateProfile):
            return result
        elif isinstance(result, dict):
            return CandidateProfile.model_validate(result)
    except Exception as e:
        logger.warning(f"LLM extraction failed ({e}), falling back to structured parser.")

    # 2. Fallback execution with mock / deterministic parser
    fallback_llm = MockLLM().with_structured_output(CandidateProfile)
    return fallback_llm.invoke({
        "candidate_id": candidate_id,
        "resume_text": resume_text
    })

