"""Convert app.schemas (agent output) to contracts (matching input)."""

from typing import Dict, Any, List, Optional
from app.schemas.candidate import CandidateProfile as AppCandidateProfile
from app.schemas.candidate import Skill as AppSkill
from app.schemas.candidate import Experience as AppExperience
from app.schemas.candidate import Education as AppEducation
from app.schemas.job import JobProfile as AppJobProfile
from app.schemas.job import JobRequirement as AppJobRequirement
from contracts.candidate import CandidateProfile, CandidateSkill, CandidateExperience, CandidateEducation, CandidateProject
from contracts.job import JobProfile, JobRequirement


def convert_app_candidate_to_contract(app_profile: AppCandidateProfile) -> CandidateProfile:
    """Convert app.schemas.CandidateProfile → contracts.CandidateProfile."""
    return CandidateProfile(
        candidate_id=app_profile.candidate_id,
        name=app_profile.name,
        email=app_profile.email,
        phone=app_profile.phone,
        total_experience_months=app_profile.total_experience_months,
        skills=[
            CandidateSkill(
                raw_skill=s.name,
                normalized_skill=s.name,
                confidence=s.confidence,
                evidence=s.evidence,
                page=None
            )
            for s in app_profile.skills
        ],
        experiences=[
            CandidateExperience(
                role=e.role or "Unknown Role",
                company=e.company,
                duration_months=e.duration_months or 0,
                description=e.description
            )
            for e in app_profile.experience
        ],
        education=[
            CandidateEducation(
                degree=ed.degree or "Unknown",
                field=ed.field,
                institution=ed.institution,
                graduation_year=ed.graduation_year
            )
            for ed in app_profile.education
        ],
        projects=[
            CandidateProject(
                title=p if isinstance(p, str) else str(p),
                description=None,
                technologies=[]
            ) if isinstance(p, str) else CandidateProject(
                title=p.get("title", "Project") if isinstance(p, dict) else str(p),
                description=p.get("description") if isinstance(p, dict) else None,
                technologies=p.get("technologies", []) if isinstance(p, dict) else []
            )
            for p in (app_profile.projects or [])
        ],
        domains=app_profile.domains or [],
        certifications=app_profile.certifications or []
    )


def convert_app_job_to_contract(app_profile: AppJobProfile) -> JobProfile:
    """Convert app.schemas.JobProfile → contracts.JobProfile."""
    
    # Convert app requirements to contract requirements
    requirements = []
    importance_map = {
        "CRITICAL": "must_have",
        "HIGH": "must_have",
        "MEDIUM": "preferred",
        "LOW": "nice_to_have"
    }
    
    for idx, req in enumerate(app_profile.requirements or []):
        importance = importance_map.get(req.importance, "preferred")
        mandatory = importance == "must_have"
        
        requirements.append(JobRequirement(
            requirement_id=req.requirement_id or f"REQ_{idx:02d}",
            description=req.description,
            skill=req.skill,
            importance=importance,
            mandatory=mandatory,
            weight=req.weight or (20.0 if mandatory else 10.0),
            minimum_duration_months=getattr(req, "minimum_duration_months", 0),
            category=getattr(req, "category", "competency")
        ))
    
    return JobProfile(
        job_id=app_profile.job_id,
        title=app_profile.title,
        description=app_profile.description,
        requirements=requirements,
        must_have_skills=app_profile.must_have_skills or [],
        preferred_skills=app_profile.preferred_skills or [],
        min_experience_months=app_profile.min_experience_months or 0,
        education_requirements=app_profile.education_requirements or [],
        certifications_required=app_profile.certifications_required or []
    )


def convert_contract_candidate_to_app(contract_profile: CandidateProfile) -> Dict[str, Any]:
    """Convert contracts.CandidateProfile → app.schemas.CandidateProfile (as dict)."""
    return {
        "candidate_id": contract_profile.candidate_id,
        "name": contract_profile.name,
        "email": contract_profile.email,
        "phone": contract_profile.phone,
        "summary": None,
        "skills": [
            {
                "name": s.raw_skill,
                "confidence": s.confidence,
                "evidence": s.evidence
            }
            for s in contract_profile.skills
        ],
        "experience": [
            {
                "company": e.company,
                "role": e.role,
                "duration_months": e.duration_months,
                "description": e.description,
                "technologies": []
            }
            for e in contract_profile.experiences
        ],
        "total_experience_months": contract_profile.total_experience_months,
        "education": [
            {
                "degree": ed.degree,
                "field": ed.field,
                "institution": ed.institution,
                "graduation_year": ed.graduation_year
            }
            for ed in contract_profile.education
        ],
        "projects": [p.title if hasattr(p, "title") else str(p) for p in contract_profile.projects],
        "domains": contract_profile.domains,
        "certifications": contract_profile.certifications
    }
