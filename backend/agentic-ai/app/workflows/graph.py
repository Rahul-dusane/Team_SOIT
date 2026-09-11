"""LangGraph Recruitment Orchestrator."""

import logging
from typing import Dict, Any, List
from langgraph.graph import StateGraph, START, END
from app.state.recruitment_state import RecruitmentState
from app.agents.resume_agent import extract_candidate_profile
from app.agents.job_agent import extract_job_profile
from app.agents.skill_gap_agent import explain_skill_gaps
from app.agents.evidence_agent import extract_evidence
from app.agents.recruiter_agent import generate_recruiter_summary
from app.services.mock_matcher import match_candidate_to_job

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Node Definitions
# ---------------------------------------------------------

def resume_agent_node(state: RecruitmentState) -> Dict[str, Any]:
    """Extracts candidate profiles for all submitted resumes."""
    logger.info("Executing Node: resume_agent")
    profiles = dict(state.get("candidate_profiles", {}))
    resume_texts = state.get("resume_texts", {})

    for cid, text in resume_texts.items():
        if cid not in profiles:
            profile = extract_candidate_profile(cid, text)
            profiles[cid] = profile.model_dump()

    return {
        "candidate_profiles": profiles,
        "current_step": "resume_extracted",
        "workflow_status": "EXTRACTING_RESUMES"
    }


def job_agent_node(state: RecruitmentState) -> Dict[str, Any]:
    """Extracts machine-readable specifications for all submitted jobs."""
    logger.info("Executing Node: job_agent")
    profiles = dict(state.get("job_profiles", {}))
    job_texts = state.get("job_texts", {})

    for jid, text in job_texts.items():
        if jid not in profiles:
            profile = extract_job_profile(jid, text)
            profiles[jid] = profile.model_dump()

    return {
        "job_profiles": profiles,
        "current_step": "job_extracted",
        "workflow_status": "EXTRACTING_JOBS"
    }


def matching_node(state: RecruitmentState) -> Dict[str, Any]:
    """
    Simulates Member 2's Matching Engine integration.
    Computes scores for each Candidate x Job combination.
    """
    logger.info("Executing Node: matching")
    matches: List[Dict[str, Any]] = []
    cand_profiles = state.get("candidate_profiles", {})
    job_profiles = state.get("job_profiles", {})

    for cid, c_data in cand_profiles.items():
        for jid, j_data in job_profiles.items():
            match_res = match_candidate_to_job(c_data, j_data)
            matches.append(match_res.model_dump())

    # Sort matches by overall score descending
    matches.sort(key=lambda m: m.get("overall_score", 0), reverse=True)

    return {
        "match_results": matches,
        "current_step": "matching_completed",
        "workflow_status": "MATCHED"
    }


def skill_gap_node(state: RecruitmentState) -> Dict[str, Any]:
    """Analyzes missing skills and discovers transferable competencies."""
    logger.info("Executing Node: skill_gap")
    gaps = dict(state.get("skill_gaps", {}))
    matches = state.get("match_results", [])
    cand_profiles = state.get("candidate_profiles", {})
    job_profiles = state.get("job_profiles", {})

    for m in matches:
        cid = m["candidate_id"]
        jid = m["job_id"]
        pair_key = f"{cid}_{jid}"
        if pair_key not in gaps and cid in cand_profiles and jid in job_profiles:
            gap_analysis = explain_skill_gaps(
                candidate=cand_profiles[cid],
                job=job_profiles[jid],
                match_result=m
            )
            gaps[pair_key] = gap_analysis.model_dump()

    return {
        "skill_gaps": gaps,
        "current_step": "skill_gaps_analyzed"
    }


def evidence_node(state: RecruitmentState) -> Dict[str, Any]:
    """Audits candidate experience and quotes exact proof points."""
    logger.info("Executing Node: evidence")
    evidence_map = dict(state.get("evidence", {}))
    matches = state.get("match_results", [])
    cand_profiles = state.get("candidate_profiles", {})
    job_profiles = state.get("job_profiles", {})

    for m in matches:
        cid = m["candidate_id"]
        jid = m["job_id"]
        pair_key = f"{cid}_{jid}"
        if pair_key not in evidence_map and cid in cand_profiles and jid in job_profiles:
            report = extract_evidence(
                candidate=cand_profiles[cid],
                job=job_profiles[jid]
            )
            evidence_map[pair_key] = report.model_dump()

    return {
        "evidence": evidence_map,
        "current_step": "evidence_extracted"
    }


def recruiter_node(state: RecruitmentState) -> Dict[str, Any]:
    """Synthesizes deterministic scores and qualitative intelligence into final recruiter output."""
    logger.info("Executing Node: recruiter")
    summaries = dict(state.get("recruiter_summaries", {}))
    matches = state.get("match_results", [])
    cand_profiles = state.get("candidate_profiles", {})
    job_profiles = state.get("job_profiles", {})
    gaps = state.get("skill_gaps", {})
    evidence_map = state.get("evidence", {})

    for m in matches:
        cid = m["candidate_id"]
        jid = m["job_id"]
        pair_key = f"{cid}_{jid}"
        if pair_key not in summaries and cid in cand_profiles and jid in job_profiles:
            summary = generate_recruiter_summary(
                candidate=cand_profiles[cid],
                job=job_profiles[jid],
                match_result=m,
                gaps=gaps.get(pair_key, {}),
                evidence=evidence_map.get(pair_key, {})
            )
            summaries[pair_key] = summary.model_dump()

    return {
        "recruiter_summaries": summaries,
        "current_step": "pipeline_completed",
        "workflow_status": "COMPLETED"
    }


# ---------------------------------------------------------
# Graph Construction
# ---------------------------------------------------------

def build_recruitment_graph():
    """Builds and compiles the full LangGraph recruitment workflow."""
    builder = StateGraph(RecruitmentState)

    # Add Nodes
    builder.add_node("resume_agent", resume_agent_node)
    builder.add_node("job_agent", job_agent_node)
    builder.add_node("matching", matching_node)
    builder.add_node("skill_gap", skill_gap_node)
    builder.add_node("evidence", evidence_node)
    builder.add_node("recruiter", recruiter_node)

    # Ingestion flow
    builder.add_edge(START, "resume_agent")
    builder.add_edge("resume_agent", "job_agent")
    builder.add_edge("job_agent", "matching")

    # Sequential flow for explanation, evidence extraction, and recruiter synthesis
    builder.add_edge("matching", "skill_gap")
    builder.add_edge("skill_gap", "evidence")
    builder.add_edge("evidence", "recruiter")
    builder.add_edge("recruiter", END)

    return builder.compile()


def run_pipeline(resume_texts: Dict[str, str], job_texts: Dict[str, str]) -> Dict[str, Any]:
    """Convenience entrypoint to execute the graph with raw inputs."""
    graph = build_recruitment_graph()
    
    initial_state: RecruitmentState = {
        "resume_ids": list(resume_texts.keys()),
        "job_ids": list(job_texts.keys()),
        "resume_texts": resume_texts,
        "job_texts": job_texts,
        "candidate_profiles": {},
        "job_profiles": {},
        "match_results": [],
        "skill_gaps": {},
        "evidence": {},
        "recruiter_summaries": {},
        "current_step": "initialized",
        "workflow_status": "INITIALIZED",
        "errors": []
    }

    return graph.invoke(initial_state)

