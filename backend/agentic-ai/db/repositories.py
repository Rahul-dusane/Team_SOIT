"""
repositories.py
Repository Layer for HireLens Database Operations.
Provides atomic transactions, retry safety & idempotency, complete profile field storage, and cascade deletion.
"""

import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from contracts.candidate import CandidateProfile, CandidateSkill, CandidateExperience, CandidateEducation, CandidateProject
from contracts.job import JobProfile, JobRequirement
from contracts.match import MatchResult, RequirementAssessment, EvidenceItem, Gap
from db.models import (
    CandidateModel, ExperienceModel, EducationModel, CandidateSkillModel,
    DocumentModel, DocumentChunkModel, JobModel, JobRequirementModel,
    MatchModel, RequirementAssessmentModel, EvidenceItemModel, GapModel,
    RecruiterSummaryModel, AgentRunLogModel, SkillModel, SkillAliasModel, SkillRelationshipModel
)


class CandidateRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_candidate(self, candidate: CandidateProfile) -> CandidateModel:
        """Upsert candidate profile with complete fields (experiences, education, skills, certifications, projects, domains, unmapped_fields)."""
        existing = self.db.query(CandidateModel).filter(CandidateModel.candidate_id == candidate.candidate_id).first()
        if existing:
            cand_model = existing
            cand_model.name = candidate.name
            cand_model.email = candidate.email
            cand_model.phone = candidate.phone
            cand_model.total_experience_months = candidate.total_experience_months
            cand_model.certifications = candidate.certifications
            cand_model.projects = [p.model_dump() if hasattr(p, 'model_dump') else dict(p) for p in candidate.projects]
            cand_model.domains = candidate.domains
            cand_model.unmapped_fields = candidate.unmapped_fields
            
            # Delete existing child items for clean re-insertion
            self.db.query(ExperienceModel).filter(ExperienceModel.candidate_id == candidate.candidate_id).delete()
            self.db.query(EducationModel).filter(EducationModel.candidate_id == candidate.candidate_id).delete()
            self.db.query(CandidateSkillModel).filter(CandidateSkillModel.candidate_id == candidate.candidate_id).delete()
        else:
            cand_model = CandidateModel(
                candidate_id=candidate.candidate_id,
                name=candidate.name,
                email=candidate.email,
                phone=candidate.phone,
                total_experience_months=candidate.total_experience_months,
                certifications=candidate.certifications,
                projects=[p.model_dump() if hasattr(p, 'model_dump') else dict(p) for p in candidate.projects],
                domains=candidate.domains,
                unmapped_fields=candidate.unmapped_fields
            )
            self.db.add(cand_model)

        self.db.flush()

        for exp in candidate.experiences:
            self.db.add(ExperienceModel(
                candidate_id=candidate.candidate_id,
                role=exp.role,
                company=exp.company,
                duration_months=exp.duration_months,
                start_date=exp.start_date,
                end_date=exp.end_date,
                description=exp.description
            ))

        for edu in candidate.education:
            self.db.add(EducationModel(
                candidate_id=candidate.candidate_id,
                degree=edu.degree,
                field=edu.field,
                institution=edu.institution,
                graduation_year=edu.graduation_year
            ))

        for sk in candidate.skills:
            self.db.add(CandidateSkillModel(
                candidate_id=candidate.candidate_id,
                raw_skill=sk.raw_skill,
                normalized_skill=sk.normalized_skill,
                confidence=sk.confidence,
                years_experience=sk.years_experience,
                evidence=sk.evidence,
                page=sk.page
            ))

        self.db.commit()
        self.db.refresh(cand_model)
        return cand_model

    def get_candidate(self, candidate_id: str) -> Optional[CandidateProfile]:
        cand_model = self.db.query(CandidateModel).filter(CandidateModel.candidate_id == candidate_id).first()
        if not cand_model:
            return None

        skills = [
            CandidateSkill(
                raw_skill=s.raw_skill,
                normalized_skill=s.normalized_skill,
                confidence=s.confidence or 1.0,
                years_experience=s.years_experience,
                evidence=s.evidence,
                page=s.page
            ) for s in cand_model.skills
        ]
        experiences = [
            CandidateExperience(
                company=e.company,
                role=e.role,
                duration_months=e.duration_months or 0,
                start_date=e.start_date,
                end_date=e.end_date,
                description=e.description
            ) for s in [cand_model] for e in s.experiences
        ]
        education = [
            CandidateEducation(
                degree=ed.degree,
                field=ed.field,
                institution=ed.institution,
                graduation_year=ed.graduation_year
            ) for s in [cand_model] for ed in s.education
        ]
        projects = [
            CandidateProject(**p) if isinstance(p, dict) else CandidateProject(title=str(p))
            for p in (cand_model.projects or [])
        ]

        return CandidateProfile(
            candidate_id=cand_model.candidate_id,
            name=cand_model.name,
            email=cand_model.email,
            phone=cand_model.phone,
            total_experience_months=cand_model.total_experience_months or 0,
            skills=skills,
            experiences=experiences,
            education=education,
            projects=projects,
            domains=cand_model.domains or [],
            certifications=cand_model.certifications or [],
            unmapped_fields=cand_model.unmapped_fields or {}
        )

    def list_candidates(self) -> List[CandidateProfile]:
        models = self.db.query(CandidateModel).all()
        return [self.get_candidate(m.candidate_id) for m in models if m.candidate_id]

    def delete_candidate(self, candidate_id: str) -> bool:
        cand = self.db.query(CandidateModel).filter(CandidateModel.candidate_id == candidate_id).first()
        if not cand:
            return False
        self.db.delete(cand)  # Foreign keys trigger ON DELETE CASCADE automatically
        self.db.commit()
        return True


class JobRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_job(self, job: JobProfile) -> JobModel:
        existing = self.db.query(JobModel).filter(JobModel.job_id == job.job_id).first()
        if existing:
            job_model = existing
            job_model.title = job.title
            job_model.description = job.description
            job_model.domain = job.domain
            job_model.min_experience_months = job.min_experience_months
            job_model.must_have_skills = job.must_have_skills
            job_model.preferred_skills = job.preferred_skills
            job_model.education_requirements = job.education_requirements
            job_model.certifications = job.certifications
            job_model.responsibilities = job.responsibilities
            
            self.db.query(JobRequirementModel).filter(JobRequirementModel.job_id == job.job_id).delete()
        else:
            job_model = JobModel(
                job_id=job.job_id,
                title=job.title,
                description=job.description,
                domain=job.domain,
                min_experience_months=job.min_experience_months,
                must_have_skills=job.must_have_skills,
                preferred_skills=job.preferred_skills,
                education_requirements=job.education_requirements,
                certifications=job.certifications,
                responsibilities=job.responsibilities
            )
            self.db.add(job_model)

        self.db.flush()

        for req in job.requirements:
            self.db.add(JobRequirementModel(
                job_id=job.job_id,
                requirement_id=req.requirement_id,
                description=req.description or req.skill or "General requirement",
                skill=req.skill or req.description,
                category=req.category,
                importance=req.importance,
                mandatory=req.mandatory,
                weight=req.weight,
                minimum_duration_months=req.minimum_duration_months
            ))

        self.db.commit()
        self.db.refresh(job_model)
        return job_model

    def get_job(self, job_id: str) -> Optional[JobProfile]:
        jm = self.db.query(JobModel).filter(JobModel.job_id == job_id).first()
        if not jm:
            return None

        reqs = [
            JobRequirement(
                requirement_id=r.requirement_id,
                description=r.description,
                skill=r.skill,
                category=r.category or "competency",
                importance=r.importance or "must_have",
                mandatory=bool(r.mandatory),
                weight=r.weight or 10.0,
                minimum_duration_months=r.minimum_duration_months or 0
            ) for r in jm.requirements
        ]

        return JobProfile(
            job_id=jm.job_id,
            title=jm.title,
            description=jm.description,
            domain=jm.domain or [],
            min_experience_months=jm.min_experience_months or 0,
            must_have_skills=jm.must_have_skills or [],
            preferred_skills=jm.preferred_skills or [],
            education_requirements=jm.education_requirements or [],
            certifications=jm.certifications or [],
            responsibilities=jm.responsibilities or [],
            requirements=reqs
        )

    def list_jobs(self) -> List[JobProfile]:
        models = self.db.query(JobModel).all()
        return [self.get_job(m.job_id) for m in models if m.job_id]


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_document_by_hash(self, candidate_id: str, file_hash: str) -> Optional[DocumentModel]:
        return self.db.query(DocumentModel).filter(
            DocumentModel.candidate_id == candidate_id,
            DocumentModel.file_hash == file_hash
        ).first()

    def save_document(self, doc_id: str, candidate_id: str, filename: str, file_type: str, file_size: int, file_hash: str, raw_content: str) -> DocumentModel:
        existing = self.get_document_by_hash(candidate_id, file_hash)
        if existing:
            return existing

        doc = DocumentModel(
            id=doc_id,
            candidate_id=candidate_id,
            filename=filename,
            file_type=file_type,
            file_size=file_size,
            file_hash=file_hash,
            raw_content=raw_content,
            status="processed"
        )
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def save_chunks(self, document_id: str, candidate_id: str, chunks_data: List[Dict[str, Any]]) -> List[DocumentChunkModel]:
        saved_chunks = []
        for idx, chunk in enumerate(chunks_data):
            chunk_obj = DocumentChunkModel(
                id=str(uuid.uuid4()),
                document_id=document_id,
                candidate_id=candidate_id,
                chunk_index=idx,
                content=chunk["content"],
                page_number=chunk.get("page_number", 1),
                start_char=chunk.get("start_char", 0),
                end_char=chunk.get("end_char", 0),
                section_title=chunk.get("section_title", ""),
                embedding=chunk.get("embedding"),
                embedding_model=chunk.get("embedding_model", "all-MiniLM-L6-v2")
            )
            self.db.add(chunk_obj)
            saved_chunks.append(chunk_obj)
        self.db.commit()
        return saved_chunks

    def get_candidate_chunks(self, candidate_id: str) -> List[DocumentChunkModel]:
        return self.db.query(DocumentChunkModel).filter(DocumentChunkModel.candidate_id == candidate_id).all()


class MatchRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_match_atomic(
        self,
        match_result: MatchResult,
        summary_text: str = "",
        key_strengths: List[str] = None,
        key_gaps: List[str] = None,
        recommendation: str = "",
        agent_logs: List[Dict[str, Any]] = None
    ) -> MatchModel:
        """Saves a Match and all associated assessments, evidence, gaps, recruiter summary, and agent logs in ONE ATOMIC TRANSACTION."""
        existing = self.db.query(MatchModel).filter(
            MatchModel.job_id == match_result.job_id,
            MatchModel.candidate_id == match_result.candidate_id
        ).first()

        match_id = existing.match_id if existing else str(uuid.uuid4())

        overall_status_val = getattr(match_result, 'overall_status', None) or getattr(match_result, 'confidence_level', 'Strong Match')
        decision_val = getattr(match_result, 'decision', None) or getattr(match_result, 'confidence_level', 'HIRE')
        raw_breakdown_val = match_result.raw_score_breakdown.model_dump() if hasattr(match_result.raw_score_breakdown, 'model_dump') else match_result.raw_score_breakdown

        if existing:
            # Clear old child records inside the transaction
            self.db.query(RequirementAssessmentModel).filter(RequirementAssessmentModel.match_id == match_id).delete()
            self.db.query(EvidenceItemModel).filter(EvidenceItemModel.match_id == match_id).delete()
            self.db.query(GapModel).filter(GapModel.match_id == match_id).delete()
            self.db.query(RecruiterSummaryModel).filter(RecruiterSummaryModel.match_id == match_id).delete()
            self.db.query(AgentRunLogModel).filter(AgentRunLogModel.match_id == match_id).delete()
            
            existing.overall_score = match_result.overall_score
            existing.raw_score = match_result.raw_score
            existing.overall_status = overall_status_val
            existing.decision = decision_val
            existing.evidence_coverage = match_result.evidence_coverage
            existing.raw_score_breakdown = raw_breakdown_val
            existing.uncertainty_flags = match_result.uncertainty_flags
            existing.embedding_model = "all-MiniLM-L6-v2"
            existing.scoring_policy_version = "v1.0"
            match_model = existing
        else:
            match_model = MatchModel(
                match_id=match_id,
                job_id=match_result.job_id,
                candidate_id=match_result.candidate_id,
                overall_score=match_result.overall_score,
                raw_score=match_result.raw_score,
                overall_status=overall_status_val,
                decision=decision_val,
                evidence_coverage=match_result.evidence_coverage,
                raw_score_breakdown=raw_breakdown_val,
                uncertainty_flags=match_result.uncertainty_flags,
                embedding_model="all-MiniLM-L6-v2",
                scoring_policy_version="v1.0"
            )
            self.db.add(match_model)

        self.db.flush()

        # Add Requirement Assessments
        for ra in match_result.requirement_assessments:
            req_desc = getattr(ra, 'requirement_description', None) or getattr(ra, 'description', '')
            req_cat = getattr(ra, 'req_category', None) or getattr(ra, 'category', 'competency')
            req_imp = getattr(ra, 'req_importance', None) or getattr(ra, 'importance', 'must_have')
            ev_text = getattr(ra, 'candidate_evidence', None) or getattr(ra, 'evidence_text', '')
            ev_pass = getattr(ra, 'evidence_passage', None) or getattr(ra, 'evidence_text', '')
            ev_page = getattr(ra, 'source_page', None) or getattr(ra, 'evidence_page', None)
            ev_conf = getattr(ra, 'evidence_confidence', None) or getattr(ra, 'confidence', 1.0)
            e_score = getattr(ra, 'earned_score', None) or getattr(ra, 'score_contribution', 0.0)
            m_score = getattr(ra, 'max_score', None) or getattr(ra, 'weight', 10.0)
            s_ratio = getattr(ra, 'score_ratio', None) or (e_score / max(m_score, 1.0))

            self.db.add(RequirementAssessmentModel(
                match_id=match_id,
                requirement_id=ra.requirement_id,
                requirement_description=req_desc,
                req_category=req_cat,
                req_importance=req_imp,
                candidate_evidence=ev_text,
                evidence_passage=ev_pass,
                source_page=ev_page,
                evidence_confidence=ev_conf,
                status=ra.status,
                weight=ra.weight,
                earned_score=e_score,
                max_score=m_score,
                score_ratio=s_ratio
            ))

        # Add Evidence Items
        for ev in match_result.evidence_items:
            self.db.add(EvidenceItemModel(
                match_id=match_id,
                requirement_id=ev.requirement_id,
                candidate_skill=ev.candidate_skill,
                matched_text=ev.matched_text,
                evidence_passage=ev.evidence_passage,
                page_number=ev.page_number,
                confidence=ev.confidence
            ))

        # Add Gaps
        for gap in match_result.gaps:
            self.db.add(GapModel(
                match_id=match_id,
                skill=gap.skill,
                gap_type=gap.gap_type,
                impact=gap.impact,
                severity=gap.severity,
                mitigations=gap.mitigations
            ))

        # Add Recruiter Summary
        summary_text = summary_text or f"Match score {match_result.overall_score}/100. Status: {overall_status_val}."
        self.db.add(RecruiterSummaryModel(
            match_id=match_id,
            candidate_id=match_result.candidate_id,
            job_id=match_result.job_id,
            summary_text=summary_text,
            key_strengths=key_strengths or [ev.matched_text for ev in match_result.evidence_items[:3]],
            key_gaps=key_gaps or [g.skill for g in match_result.gaps[:3]],
            recommendation=recommendation or decision_val
        ))

        # Add Agent Logs (strictly real logs, zero invented defaults)
        if agent_logs:
            for log in agent_logs:
                self.db.add(AgentRunLogModel(
                    match_id=match_id,
                    agent_name=log.get("agent_name", "Agent"),
                    step_index=log.get("step_index", 1),
                    status=log.get("status", "success"),
                    input_summary=log.get("input_summary", ""),
                    output_summary=log.get("output_summary", ""),
                    duration_ms=log.get("duration_ms", 0)
                ))

        self.db.commit()
        self.db.refresh(match_model)
        return match_model

    def get_match(self, job_id: str, candidate_id: str) -> Optional[MatchModel]:
        return self.db.query(MatchModel).filter(
            MatchModel.job_id == job_id,
            MatchModel.candidate_id == candidate_id
        ).first()

    def get_match_by_id(self, match_id: str) -> Optional[MatchModel]:
        return self.db.query(MatchModel).filter(MatchModel.match_id == match_id).first()

    def get_match_by_candidate_id(self, candidate_id: str) -> Optional[MatchModel]:
        return self.db.query(MatchModel).filter(MatchModel.candidate_id == candidate_id).order_by(MatchModel.overall_score.desc()).first()

    def get_rankings_for_job(self, job_id: str) -> List[MatchModel]:
        return self.db.query(MatchModel).filter(MatchModel.job_id == job_id).order_by(MatchModel.overall_score.desc()).all()
