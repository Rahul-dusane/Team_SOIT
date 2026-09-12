"""
pipeline.py
Domain-Independent Candidate-Job Matching Pipeline.
Evaluates arbitrary job requirements against candidate profiles across any profession (IT, Accounting, Healthcare, etc.),
computing traceable requirement assessments, evidence coverage, uncertainty flags, and score breakdowns.
"""

from typing import Dict, Any, List
from contracts.candidate import CandidateProfile
from contracts.job import JobProfile, JobRequirement
from contracts.match import MatchResult, ScoreBreakdown, RequirementAssessment
from matching.feature_filter import build_scoring_profile
from matching.rules import check_mandatory_requirements
from matching.feature_engineering import build_features
from matching.scorer import calculate_match_score
from matching.gap_engine import find_skill_gaps
from nlp.evidence_retriever import retrieve_candidate_evidence
from config.matching_config import DEFAULT_MATCHING_CONFIG, MatchingConfig


def match_candidate_to_job(candidate: CandidateProfile, job: JobProfile, cfg: MatchingConfig = DEFAULT_MATCHING_CONFIG, db: Any = None) -> MatchResult:
    if not candidate:
        raise ValueError("Candidate profile cannot be None")
    if not job:
        raise ValueError("Job profile cannot be None")

    # 1. PII-Safe Filtering
    sanitized_dict = build_scoring_profile(candidate)
    sanitized_candidate = CandidateProfile(**sanitized_dict)

    # 2. Requirement-Level Assessment across ANY domain requirements
    requirement_assessments: List[RequirementAssessment] = []
    uncertainty_flags: List[str] = []

    req_list = job.requirements
    if not req_list:
        req_list = [JobRequirement(requirement_id=f"R_{idx}", description=f"Demonstrate proficiency in {s}", skill=s, importance="must_have", mandatory=True, weight=20.0) for idx, s in enumerate(job.must_have_skills, 1)]
        req_list += [JobRequirement(requirement_id=f"R_P_{idx}", description=f"Experience with {s}", skill=s, importance="preferred", weight=10.0) for idx, s in enumerate(job.preferred_skills, 1)]

    supported_count = 0

    for idx, req in enumerate(req_list, start=1):
        req_id = req.requirement_id or f"REQ_{idx:02d}"
        status, ev_text, ev_page, conf = retrieve_candidate_evidence(
            requirement_text=req.description,
            candidate=candidate,
            req_skill=req.skill,
            min_duration_months=req.minimum_duration_months,
            db=db
        )
        
        status_mult = 1.0 if status == "satisfied" else (0.5 if status == "partially_supported" else 0.0)
        contrib = status_mult * req.weight
        
        if status in ["satisfied", "partially_supported"]:
            supported_count += 1
        elif status == "contradicted":
            uncertainty_flags.append(f"CONTRADICTION DETECTED: Requirement '{req.description}' contradicted by candidate evidence.")
        else:
            if req.importance == "must_have" or req.mandatory:
                uncertainty_flags.append(f"Missing evidence for mandatory requirement: '{req.description}'")

        requirement_assessments.append(RequirementAssessment(
            requirement_id=req_id,
            description=req.description,
            category=req.category,
            mandatory=req.mandatory or req.importance == "must_have",
            weight=req.weight,
            status=status,
            confidence=conf,
            evidence_text=ev_text if ev_text else None,
            evidence_page=ev_page,
            score_contribution=contrib
        ))

    evidence_coverage = round(supported_count / float(len(req_list)), 2) if req_list else 1.0

    # 3. Mandatory Constraint Check
    mandatory_pass, failed_reqs = check_mandatory_requirements(sanitized_candidate, job, cfg, requirement_assessments)

    # 4. Feature Extraction & Raw Score Calculation
    features, skill_matches = build_features(sanitized_candidate, job, cfg)
    raw_score, raw_breakdown = calculate_match_score(features, requirement_assessments, cfg)

    # 5. Mandatory Failure Policy & Score Adjustment
    if not mandatory_pass:
        if cfg.mandatory_failure_policy == "reject":
            overall_score = 0.0
            score_breakdown = ScoreBreakdown()
            confidence = "REJECTED (Mandatory Failed)"
        else:
            overall_score = raw_score
            score_breakdown = raw_breakdown
            confidence = "FLAGGED (Mandatory Failed)"
    else:
        overall_score = raw_score
        score_breakdown = raw_breakdown

        # 6. Evidence Reliability & Coverage Confidence Classification
        skill_confidences = [s.confidence for s in candidate.skills if hasattr(s, "confidence")]
        min_skill_conf = min(skill_confidences) if skill_confidences else 1.0
        avg_skill_conf = sum(skill_confidences) / len(skill_confidences) if skill_confidences else 1.0

        if evidence_coverage < 0.60 or min_skill_conf < 0.70 or avg_skill_conf < 0.70 or len(uncertainty_flags) > 0:
            confidence = "LOW (Needs Review)"
        elif evidence_coverage >= 0.85 and overall_score >= 80.0:
            confidence = "HIGH"
        else:
            confidence = "MEDIUM"

    # 7. Skill Gap Analysis
    gaps = find_skill_gaps(sanitized_candidate, job, skill_matches)

    return MatchResult(
        candidate_id=candidate.candidate_id,
        job_id=job.job_id,
        raw_score=raw_score,
        overall_score=overall_score,
        evidence_coverage=evidence_coverage,
        mandatory_pass=mandatory_pass,
        confidence_level=confidence,
        uncertainty_flags=uncertainty_flags,
        failed_requirements=failed_reqs,
        requirement_assessments=requirement_assessments,
        features=features,
        raw_score_breakdown=raw_breakdown,
        score_breakdown=score_breakdown,
        skill_matches=skill_matches,
        skill_gaps=gaps
    )
