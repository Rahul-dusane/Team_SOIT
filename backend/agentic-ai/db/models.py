"""
models.py
SQLAlchemy Declarative ORM Models for HireLens Database.
Supports all 17 schema tables with complete profile fields, versioning, and ON DELETE CASCADE relationships.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, JSON, DateTime, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from db.connection import Base, IS_SQLITE

try:
    from pgvector.sqlalchemy import Vector
    PGVECTOR_AVAILABLE = not IS_SQLITE
except ImportError:
    PGVECTOR_AVAILABLE = False


class CandidateModel(Base):
    __tablename__ = "candidates"

    candidate_id = Column(String(100), primary_key=True)
    name = Column(String(255), default="Anonymous Candidate")
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    total_experience_months = Column(Integer, default=0)
    certifications = Column(JSON, default=list)
    projects = Column(JSON, default=list)
    domains = Column(JSON, default=list)
    unmapped_fields = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    experiences = relationship("ExperienceModel", back_populates="candidate", cascade="all, delete-orphan")
    education = relationship("EducationModel", back_populates="candidate", cascade="all, delete-orphan")
    skills = relationship("CandidateSkillModel", back_populates="candidate", cascade="all, delete-orphan")
    documents = relationship("DocumentModel", back_populates="candidate", cascade="all, delete-orphan")
    matches = relationship("MatchModel", back_populates="candidate", cascade="all, delete-orphan")


class ExperienceModel(Base):
    __tablename__ = "experiences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(String(100), ForeignKey("candidates.candidate_id", ondelete="CASCADE"), nullable=False)
    role = Column(String(255), nullable=False)
    company = Column(String(255), nullable=True)
    duration_months = Column(Integer, default=0)
    start_date = Column(String(50), nullable=True)
    end_date = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)

    candidate = relationship("CandidateModel", back_populates="experiences")


class EducationModel(Base):
    __tablename__ = "education"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(String(100), ForeignKey("candidates.candidate_id", ondelete="CASCADE"), nullable=False)
    degree = Column(String(255), nullable=False)
    field = Column(String(255), nullable=True)
    institution = Column(String(255), nullable=True)
    graduation_year = Column(Integer, nullable=True)

    candidate = relationship("CandidateModel", back_populates="education")


class CandidateSkillModel(Base):
    __tablename__ = "candidate_skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(String(100), ForeignKey("candidates.candidate_id", ondelete="CASCADE"), nullable=False)
    raw_skill = Column(String(255), nullable=False)
    normalized_skill = Column(String(255), nullable=True)
    confidence = Column(Float, default=1.0)
    years_experience = Column(Float, nullable=True)
    evidence = Column(Text, nullable=True)
    page = Column(Integer, nullable=True)

    candidate = relationship("CandidateModel", back_populates="skills")


class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(String(100), primary_key=True)
    candidate_id = Column(String(100), ForeignKey("candidates.candidate_id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_hash = Column(String(64), nullable=False)
    raw_content = Column(Text, nullable=True)
    status = Column(String(50), default="processed")
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("candidate_id", "file_hash", name="uq_candidate_file_hash"),
    )

    candidate = relationship("CandidateModel", back_populates="documents")
    chunks = relationship("DocumentChunkModel", back_populates="document", cascade="all, delete-orphan")


class DocumentChunkModel(Base):
    __tablename__ = "document_chunks"

    id = Column(String(100), primary_key=True)
    document_id = Column(String(100), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    candidate_id = Column(String(100), ForeignKey("candidates.candidate_id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    page_number = Column(Integer, default=1)
    start_char = Column(Integer, default=0)
    end_char = Column(Integer, default=0)
    section_title = Column(String(255), nullable=True)
    
    if PGVECTOR_AVAILABLE:
        embedding = Column(Vector(384))
    else:
        embedding = Column(JSON, nullable=True)  # Fallback vector list for SQLite testing

    embedding_model = Column(String(100), default="all-MiniLM-L6-v2")
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("DocumentModel", back_populates="chunks")


class JobModel(Base):
    __tablename__ = "jobs"

    job_id = Column(String(100), primary_key=True)
    title = Column(String(255), nullable=False)
    department = Column(String(255), default="Engineering")
    status = Column(String(50), default="Active")
    description = Column(Text, nullable=True)
    domain = Column(JSON, default=list)
    min_experience_months = Column(Integer, default=0)
    must_have_skills = Column(JSON, default=list)
    preferred_skills = Column(JSON, default=list)
    education_requirements = Column(JSON, default=list)
    certifications = Column(JSON, default=list)
    responsibilities = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    requirements = relationship("JobRequirementModel", back_populates="job", cascade="all, delete-orphan")
    matches = relationship("MatchModel", back_populates="job", cascade="all, delete-orphan")


class JobRequirementModel(Base):
    __tablename__ = "job_requirements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String(100), ForeignKey("jobs.job_id", ondelete="CASCADE"), nullable=False)
    requirement_id = Column(String(100), nullable=True)
    description = Column(Text, nullable=False)
    skill = Column(String(255), nullable=True)
    category = Column(String(50), default="competency")
    importance = Column(String(50), default="must_have")
    mandatory = Column(Boolean, default=False)
    weight = Column(Float, default=10.0)
    minimum_duration_months = Column(Integer, default=0)

    job = relationship("JobModel", back_populates="requirements")


class SkillModel(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    canonical_name = Column(String(255), unique=True, nullable=False)
    category = Column(String(100), default="general")


class SkillAliasModel(Base):
    __tablename__ = "skill_aliases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    alias_name = Column(String(255), unique=True, nullable=False)
    canonical_name = Column(String(255), nullable=False)


class SkillRelationshipModel(Base):
    __tablename__ = "skill_relationships"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_skill = Column(String(255), nullable=False)
    target_skill = Column(String(255), nullable=False)
    relationship = Column(String(50), nullable=False)
    transferability = Column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint("source_skill", "target_skill", name="uq_skill_pair"),
    )


class MatchModel(Base):
    __tablename__ = "matches"

    match_id = Column(String(100), primary_key=True)
    job_id = Column(String(100), ForeignKey("jobs.job_id", ondelete="CASCADE"), nullable=False)
    candidate_id = Column(String(100), ForeignKey("candidates.candidate_id", ondelete="CASCADE"), nullable=False)
    overall_score = Column(Float, nullable=False)
    raw_score = Column(Float, nullable=False)
    overall_status = Column(String(50), nullable=False)
    decision = Column(String(50), nullable=False)
    evidence_coverage = Column(Float, default=0.0)
    raw_score_breakdown = Column(JSON, default=dict)
    uncertainty_flags = Column(JSON, default=list)
    embedding_model = Column(String(100), default="all-MiniLM-L6-v2")
    scoring_policy_version = Column(String(50), default="v1.0")
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("job_id", "candidate_id", name="uq_job_candidate_match"),
    )

    job = relationship("JobModel", back_populates="matches")
    candidate = relationship("CandidateModel", back_populates="matches")
    assessments = relationship("RequirementAssessmentModel", back_populates="match", cascade="all, delete-orphan")
    evidence_items = relationship("EvidenceItemModel", back_populates="match", cascade="all, delete-orphan")
    gaps = relationship("GapModel", back_populates="match", cascade="all, delete-orphan")
    summary = relationship("RecruiterSummaryModel", back_populates="match", uselist=False, cascade="all, delete-orphan")
    agent_logs = relationship("AgentRunLogModel", back_populates="match", cascade="all, delete-orphan")


class RequirementAssessmentModel(Base):
    __tablename__ = "requirement_assessments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(String(100), ForeignKey("matches.match_id", ondelete="CASCADE"), nullable=False)
    requirement_id = Column(String(100), nullable=True)
    requirement_description = Column(Text, nullable=True)
    req_category = Column(String(50), nullable=True)
    req_importance = Column(String(50), nullable=True)
    candidate_evidence = Column(Text, nullable=True)
    evidence_passage = Column(Text, nullable=True)
    source_page = Column(Integer, nullable=True)
    evidence_confidence = Column(Float, nullable=True)
    status = Column(String(50), nullable=True)
    weight = Column(Float, nullable=True)
    earned_score = Column(Float, nullable=True)
    max_score = Column(Float, nullable=True)
    score_ratio = Column(Float, nullable=True)

    match = relationship("MatchModel", back_populates="assessments")


class EvidenceItemModel(Base):
    __tablename__ = "evidence_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(String(100), ForeignKey("matches.match_id", ondelete="CASCADE"), nullable=False)
    requirement_id = Column(String(100), nullable=True)
    candidate_skill = Column(String(255), nullable=True)
    matched_text = Column(Text, nullable=True)
    evidence_passage = Column(Text, nullable=True)
    page_number = Column(Integer, nullable=True)
    confidence = Column(Float, nullable=True)

    match = relationship("MatchModel", back_populates="evidence_items")


class GapModel(Base):
    __tablename__ = "gaps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(String(100), ForeignKey("matches.match_id", ondelete="CASCADE"), nullable=False)
    skill = Column(String(255), nullable=False)
    gap_type = Column(String(50), nullable=False)
    impact = Column(String(50), nullable=True)
    severity = Column(String(50), nullable=True)
    mitigations = Column(JSON, default=list)

    match = relationship("MatchModel", back_populates="gaps")


class RecruiterSummaryModel(Base):
    __tablename__ = "recruiter_summaries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(String(100), ForeignKey("matches.match_id", ondelete="CASCADE"), nullable=False)
    candidate_id = Column(String(100), nullable=False)
    job_id = Column(String(100), nullable=False)
    summary_text = Column(Text, nullable=False)
    key_strengths = Column(JSON, default=list)
    key_gaps = Column(JSON, default=list)
    recommendation = Column(String(100), nullable=True)

    match = relationship("MatchModel", back_populates="summary")


class AgentRunLogModel(Base):
    __tablename__ = "agent_run_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(String(100), ForeignKey("matches.match_id", ondelete="CASCADE"), nullable=False)
    agent_name = Column(String(100), nullable=False)
    step_index = Column(Integer, default=0)
    status = Column(String(50), default="success")
    input_summary = Column(Text, nullable=True)
    output_summary = Column(Text, nullable=True)
    duration_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    match = relationship("MatchModel", back_populates="agent_logs")
