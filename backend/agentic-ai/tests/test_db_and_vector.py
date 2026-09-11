"""
test_db_and_vector.py
Unit tests for ORM models, Repositories, Atomic Persistence, Vector Storage, and Cascade Deletion.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.connection import Base
from db.repositories import CandidateRepository, JobRepository, MatchRepository, DocumentRepository
from contracts.candidate import CandidateProfile, CandidateSkill, CandidateExperience, CandidateEducation
from contracts.job import JobProfile, JobRequirement
from contracts.match import MatchResult, RequirementAssessment, EvidenceItem, Gap
from vector_store import embed_text, retrieve_evidence_from_vector_store, store_chunks_with_embeddings


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_complete_candidate_profile_persistence(db_session):
    cand_repo = CandidateRepository(db_session)
    cand = CandidateProfile(
        candidate_id="CAND_TEST_01",
        name="Jane Accountant",
        email="jane@example.com",
        phone="555-1234",
        total_experience_months=60,
        skills=[CandidateSkill(raw_skill="General Ledger"), CandidateSkill(raw_skill="Financial Close")],
        experiences=[CandidateExperience(role="Senior Accountant", company="Finance Co", duration_months=36)],
        education=[CandidateEducation(degree="B.Com", field="Accounting")],
        certifications=["CPA License #999"],
        projects=[{"title": "ERP Implementation", "description": "Led SAP migration"}],
        domains=["Finance", "Taxation"],
        unmapped_fields={"license_number": "CPA999", "clearance": "Top Secret"}
    )

    cand_repo.save_candidate(cand)

    retrieved = cand_repo.get_candidate("CAND_TEST_01")
    assert retrieved is not None
    assert retrieved.name == "Jane Accountant"
    assert retrieved.certifications == ["CPA License #999"]
    assert retrieved.domains == ["Finance", "Taxation"]
    assert retrieved.unmapped_fields["license_number"] == "CPA999"


def test_atomic_match_persistence(db_session):
    cand_repo = CandidateRepository(db_session)
    job_repo = JobRepository(db_session)
    match_repo = MatchRepository(db_session)

    cand = CandidateProfile(candidate_id="C_ATOMIC", name="Atomic User", skills=[CandidateSkill(raw_skill="Python")])
    job = JobProfile(job_id="J_ATOMIC", title="Python Engineer", requirements=[JobRequirement(skill="Python")])
    cand_repo.save_candidate(cand)
    job_repo.save_job(job)

    result = MatchResult(
        match_id="M_ATOMIC",
        job_id="J_ATOMIC",
        candidate_id="C_ATOMIC",
        overall_score=95.0,
        raw_score=95.0,
        overall_status="Strong Match",
        decision="HIRE",
        evidence_coverage=1.0,
        raw_score_breakdown={"skills": 95.0},
        requirement_assessments=[
            RequirementAssessment(
                requirement_id="R1",
                requirement_description="Python proficiency",
                earned_score=95.0,
                max_score=100.0,
                status="satisfied"
            )
        ],
        evidence_items=[
            EvidenceItem(requirement_id="R1", candidate_skill="Python", matched_text="Extensive Python background")
        ],
        gaps=[
            Gap(skill="Kubernetes", gap_type="optional", impact="Low", severity="minor")
        ]
    )

    match_repo.save_match_atomic(
        match_result=result,
        summary_text="Atomic test summary",
        recommendation="HIRE"
    )

    m = match_repo.get_match("J_ATOMIC", "C_ATOMIC")
    assert m is not None
    assert m.overall_score == 95.0
    assert len(m.assessments) == 1
    assert len(m.evidence_items) == 1
    assert len(m.gaps) == 1
    assert m.summary is not None
    assert m.summary.summary_text == "Atomic test summary"


def test_vector_dimension_validation():
    vec = embed_text("Python FastAPI Developer")
    assert len(vec) == 384


def test_cascade_deletion(db_session):
    cand_repo = CandidateRepository(db_session)
    job_repo = JobRepository(db_session)
    match_repo = MatchRepository(db_session)
    doc_repo = DocumentRepository(db_session)

    cand = CandidateProfile(candidate_id="C_CASCADE", name="Cascade User")
    job = JobProfile(job_id="J_CASCADE", title="DevOps Engineer")
    cand_repo.save_candidate(cand)
    job_repo.save_job(job)

    doc_repo.save_document("DOC_1", "C_CASCADE", "resume.pdf", ".pdf", 1000, "HASH123", "Resume content")
    store_chunks_with_embeddings(db_session, "DOC_1", "C_CASCADE", [{"content": "DevOps skills"}])

    res = MatchResult(match_id="M_CASCADE", job_id="J_CASCADE", candidate_id="C_CASCADE", overall_score=80.0, raw_score=80.0, overall_status="Moderate", decision="INTERVIEW")
    match_repo.save_match_atomic(res)

    # Delete candidate
    success = cand_repo.delete_candidate("C_CASCADE")
    assert success is True

    # Verify purge
    assert cand_repo.get_candidate("C_CASCADE") is None
    assert match_repo.get_match("J_CASCADE", "C_CASCADE") is None
    assert doc_repo.get_candidate_chunks("C_CASCADE") == []
