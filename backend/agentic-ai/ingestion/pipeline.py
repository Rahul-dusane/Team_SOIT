"""
pipeline.py
End-to-end Document Ingestion Pipeline.
Coordinates validation, multi-format parsing, sliding-window chunking, vector embedding, DB persistence, and candidate extraction.
Supports partial batch upload failure reporting.
"""

import uuid
import re
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from contracts.candidate import CandidateProfile, CandidateSkill, CandidateExperience, CandidateEducation
from ingestion.validator import validate_file
from ingestion.parser import parse_document
from ingestion.chunker import chunk_pages_or_sections
from db.repositories import CandidateRepository, DocumentRepository
from vector_store import store_chunks_with_embeddings


def extract_candidate_profile_from_text(raw_text: str, filename: str, candidate_id: str = None) -> CandidateProfile:
    """
    Rule/NLP-assisted extractor that builds a CandidateProfile from raw resume text.
    Handles non-IT and IT profiles cleanly.
    """
    if not candidate_id:
        candidate_id = f"CAND_{uuid.uuid4().hex[:8].upper()}"

    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    
    # Candidate name heuristic
    name = "Anonymous Candidate"
    if lines:
        first_line = lines[0]
        if len(first_line) < 50 and not any(k in first_line.lower() for k in ["resume", "cv", "curriculum"]):
            name = first_line

    # Email & phone extraction
    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', raw_text)
    email = email_match.group(0) if email_match else None

    phone_match = re.search(r'\(?\+?\d{1,3}\)?[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}', raw_text)
    phone = phone_match.group(0) if phone_match else None

    # Total experience heuristic
    exp_months = 0
    exp_matches = re.findall(r'(\d+)\+?\s*(?:years?|yrs?)', raw_text, re.IGNORECASE)
    if exp_matches:
        max_years = max([int(y) for y in exp_matches if int(y) < 45], default=0)
        exp_months = max_years * 12

    # Skills extraction using domain taxonomy keywords
    skills_found = []
    known_skill_keywords = [
        "Python", "FastAPI", "Flask", "Django", "PostgreSQL", "MySQL", "MongoDB",
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "React", "Node.js", "Java",
        "JavaScript", "TypeScript", "C++", "C#", "Go", "SQL", "General Ledger",
        "Bookkeeping", "Financial Close", "Auditing", "Taxation", "Payroll",
        "Patient Care", "Clinical Nursing", "ICU", "Triage", "Phlebotomy", "EHR", "IV Administration"
    ]
    
    for kw in known_skill_keywords:
        if re.search(r'\b' + re.escape(kw) + r'\b', raw_text, re.IGNORECASE):
            skills_found.append(CandidateSkill(raw_skill=kw, normalized_skill=kw.lower(), confidence=1.0))

    # Experience entries heuristic
    experiences = []
    role_matches = re.findall(r'(?:Senior|Lead|Staff|Junior|Associate)?\s*(?:Software Engineer|Backend Developer|Developer|Accountant|Financial Analyst|Nurse|Clinical Nurse|Manager|Consultant)', raw_text, re.IGNORECASE)
    for role in set(role_matches):
        experiences.append(CandidateExperience(
            role=role,
            company="Extracted Experience",
            duration_months=max(exp_months, 12),
            description=f"Experienced as {role} handling key operational responsibilities."
        ))

    if not experiences:
        experiences.append(CandidateExperience(
            role="Professional",
            company="General Industry",
            duration_months=exp_months,
            description="Extracted candidate background"
        ))

    # Education entries heuristic
    education = []
    edu_matches = re.findall(r'\b(?:B\.?Tech|M\.?Tech|B\.?E|B\.?Sc|M\.?Sc|BCA|MCA|MBA|Bachelor|Master|Diploma|B\.?Com)\b[^\.\n]*', raw_text, re.IGNORECASE)
    for edu_str in edu_matches[:2]:
        education.append(CandidateEducation(
            degree=edu_str.strip(),
            field="Specialized Field",
            institution="University"
        ))

    if not education:
        education.append(CandidateEducation(degree="Bachelor Degree", field="General Studies"))

    # Extract certifications and domains
    certifications = []
    cert_matches = re.findall(r'\b(?:CPA|RN|AWS Certified|PMP|CFA|ACCA|CKA)\b[^\.\n]*', raw_text, re.IGNORECASE)
    for c in cert_matches:
        certifications.append(c.strip())

    return CandidateProfile(
        candidate_id=candidate_id,
        name=name,
        email=email,
        phone=phone,
        total_experience_months=exp_months,
        skills=skills_found,
        experiences=experiences,
        education=education,
        certifications=certifications,
        domains=["Engineering" if "Python" in raw_text or "Java" in raw_text else "General"],
        unmapped_fields={"source_filename": filename}
    )


def ingest_resume_bytes(
    db: Session,
    filename: str,
    content: bytes,
    candidate_id: str = None
) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Ingests a single resume file bytes.
    Returns (success, status_code, result_dict).
    """
    # 1. Server-side validation
    is_valid, status_msg, val_meta = validate_file(filename, content)
    if not is_valid:
        return False, status_msg, {"filename": filename, "error": status_msg}

    file_hash = val_meta["file_hash"]
    doc_repo = DocumentRepository(db)
    cand_repo = CandidateRepository(db)

    # 2. Extract profile & assign candidate ID if new
    if not candidate_id:
        candidate_id = f"CAND_{file_hash[:10].upper()}"

    # Deduplication Check
    existing_doc = doc_repo.get_document_by_hash(candidate_id, file_hash)
    if existing_doc:
        existing_cand = cand_repo.get_candidate(candidate_id)
        return True, "duplicate_retrieved", {
            "filename": filename,
            "status": "duplicate",
            "candidate_id": candidate_id,
            "document_id": existing_doc.id,
            "candidate": existing_cand.model_dump() if existing_cand else {}
        }

    # 3. Parse Document
    try:
        raw_text, structured_units, parse_meta = parse_document(filename, content)
    except Exception as e:
        return False, f"parse_error: {str(e)}", {"filename": filename, "error": str(e)}

    # 4. Extract Structured Candidate Profile
    cand_profile = extract_candidate_profile_from_text(raw_text, filename, candidate_id)
    cand_repo.save_candidate(cand_profile)

    # 5. Save Document Record
    doc_id = f"DOC_{uuid.uuid4().hex[:10]}"
    doc_record = doc_repo.save_document(
        doc_id=doc_id,
        candidate_id=candidate_id,
        filename=filename,
        file_type=val_meta["extension"],
        file_size=val_meta["size_bytes"],
        file_hash=file_hash,
        raw_content=raw_text
    )

    # 6. Chunk Document & Generate Vector Embeddings
    chunks = chunk_pages_or_sections(structured_units)
    saved_chunks = store_chunks_with_embeddings(db, doc_record.id, candidate_id, chunks)

    return True, "success", {
        "filename": filename,
        "status": "success",
        "candidate_id": candidate_id,
        "document_id": doc_record.id,
        "total_chunks": len(saved_chunks),
        "candidate": cand_profile.model_dump()
    }


def process_batch_upload(db: Session = None, files: List[Tuple[str, bytes]] = None, **kwargs) -> Dict[str, Any]:
    if files is None and isinstance(db, list):
        files = db
        db = kwargs.get("db")
    if db is None and "db" in kwargs:
        db = kwargs["db"]
    results = []
    success_count = 0
    failed_count = 0

    for filename, content in files:
        ok, status_code, result = ingest_resume_bytes(db, filename, content)
        if ok:
            success_count += 1
            results.append(result)
        else:
            failed_count += 1
            results.append({
                "filename": filename,
                "status": "failed",
                "error": status_code
            })

    return {
        "total_files": len(files),
        "successful": success_count,
        "failed": failed_count,
        "file_results": results
    }
