"""Recruitment state definition for LangGraph orchestrator."""

from typing import TypedDict, List, Dict, Any, Optional


class RecruitmentState(TypedDict, total=False):
    """The shared memory across all LangGraph nodes in the recruitment pipeline."""

    # 1. Inputs
    resume_ids: List[str]
    job_ids: List[str]
    resume_texts: Dict[str, str]  # e.g. {"C01": "raw text...", "C02": "raw text..."}
    job_texts: Dict[str, str]     # e.g. {"J01": "raw text..."}

    # 2. Agent Structured Extractions
    candidate_profiles: Dict[str, Any]  # {"C01": CandidateProfile.model_dump()}
    job_profiles: Dict[str, Any]        # {"J01": JobProfile.model_dump()}

    # 3. Matching Engine Outputs (Member 2 Contract)
    match_results: List[Dict[str, Any]] # List of MatchResult.model_dump()

    # 4. Agent Reasoning Outputs
    skill_gaps: Dict[str, Any]          # {"C01_J01": SkillGapAnalysis.model_dump()}
    evidence: Dict[str, Any]            # {"C01_J01": EvidenceReport.model_dump()}
    recruiter_summaries: Dict[str, Any] # {"C01_J01": RecruiterSummary.model_dump()}

    # 5. Pipeline Telemetry & Error Handling
    current_step: str
    workflow_status: str                # "INITIALIZED" | "EXTRACTING" | "MATCHED" | "COMPLETED" | "FAILED"
    errors: List[str]

