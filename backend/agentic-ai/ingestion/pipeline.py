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
    Factual candidate extractor that builds a CandidateProfile from raw resume text.
    Strictly preserves factual evidence: unmentioned education or experience arrays are left empty ([]).
    Never invents degrees, placeholder roles, or fake companies.
    """
    if not candidate_id:
        candidate_id = f"CAND_{uuid.uuid4().hex[:8].upper()}"

    import os
    # Try Member 1 Structured Agent Extractor first if available
    try:
        from app.agents.resume_agent import extract_candidate_profile as member1_extract
        agent_profile = member1_extract(candidate_id, raw_text)
        if agent_profile:
            p_name = getattr(agent_profile, "name", "") or ""
            # Filter out hardcoded MockLLM Alex Johnson profile if resume belongs to a different candidate
            if p_name == "Alex Johnson" and "alex johnson" not in raw_text.lower():
                agent_profile = None
            else:
                if not hasattr(agent_profile, "unmapped_fields") or agent_profile.unmapped_fields is None:
                    agent_profile.unmapped_fields = {}
                agent_profile.unmapped_fields["source_filename"] = filename
                
                # Convert app.schemas CandidateProfile to contracts CandidateProfile if necessary
                if not isinstance(agent_profile, CandidateProfile):
                    dumped = agent_profile.model_dump() if hasattr(agent_profile, "model_dump") else dict(agent_profile)
                    if "skills" in dumped and isinstance(dumped["skills"], list):
                        norm_skills = []
                        for s in dumped["skills"]:
                            if isinstance(s, dict):
                                raw_s = s.get("name") or s.get("raw_skill") or "Skill"
                                norm_skills.append({
                                    "raw_skill": raw_s,
                                    "normalized_skill": raw_s.lower(),
                                    "confidence": s.get("confidence", 1.0),
                                    "evidence": s.get("evidence")
                                })
                        dumped["skills"] = norm_skills
                    if "experience" in dumped and "experiences" not in dumped:
                        dumped["experiences"] = dumped.pop("experience")
                    agent_profile = CandidateProfile(**dumped)
                return agent_profile
    except Exception:
        pass

    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    
    # Candidate name heuristic
    name = "Anonymous Candidate"
    if lines:
        first_line = lines[0]
        if len(first_line) < 50 and not any(k in first_line.lower() for k in ["resume", "cv", "curriculum", "page", "profile"]):
            name = first_line

    if (name == "Anonymous Candidate" or len(name) > 60) and filename:
        clean_file_name = os.path.splitext(filename)[0]
        clean_file_name = re.sub(r'\s*\([^)]*\)', '', clean_file_name).strip()
        if clean_file_name:
            name = clean_file_name.title()

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
        # Cybersecurity & Information Security
        "Vulnerability Assessment", "Penetration Testing", "Ethical Hacking", "CEH", "Cybersecurity",
        "Network Security", "Information Security", "Wireshark", "Metasploit", "Nmap", "Burp Suite",
        "SIEM", "Firewalls", "Incident Response", "Risk Assessment", "CISSP", "OWASP", "Linux",
        # Software & Cloud
        "Python", "FastAPI", "Flask", "Django", "PostgreSQL", "MySQL", "MongoDB", "SQLite",
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "React", "Node.js", "Java",
        "JavaScript", "TypeScript", "C++", "C#", "Go", "SQL", "Git", "CI/CD", "REST API",
        # Accounting & Finance
        "General Ledger", "Bookkeeping", "Financial Close", "Auditing", "Taxation", "Payroll",
        # Healthcare & Nursing
        "Patient Care", "Clinical Nursing", "ICU", "Triage", "Phlebotomy", "EHR", "IV Administration"
    ]
    
    from nlp.evidence_retriever import contains_negation

    for kw in known_skill_keywords:
        if re.search(r'\b' + re.escape(kw) + r'\b', raw_text, re.IGNORECASE):
            if contains_negation(raw_text, kw):
                continue
            skills_found.append(CandidateSkill(raw_skill=kw, normalized_skill=kw.lower(), confidence=1.0))

    # Experience entries extraction (strictly factual)
    experiences = []
    role_matches = re.findall(r'(?:Senior|Lead|Staff|Junior|Associate)?\s*(?:Software Engineer|Backend Developer|Developer|Accountant|Financial Analyst|Nurse|Clinical Nurse|Security Analyst|Penetration Tester|Ethical Hacker|Manager|Consultant)', raw_text, re.IGNORECASE)
    for role in set(role_matches):
        experiences.append(CandidateExperience(
            role=role,
            company=None,
            duration_months=exp_months,
            description=None
        ))

    # Education entries extraction (strictly factual)
    education = []
    edu_matches = re.findall(r'\b(?:B\.?Tech|M\.?Tech|B\.?E|B\.?Sc|M\.?Sc|BCA|MCA|MBA|Bachelor|Master|Diploma|B\.?Com)\b[^\.\n]*', raw_text, re.IGNORECASE)
    for edu_str in edu_matches[:2]:
        education.append(CandidateEducation(
            degree=edu_str.strip(),
            field=None,
            institution=None
        ))

    # Extract certifications and domains
    certifications = []
    cert_matches = re.findall(r'\b(?:CPA|RN|AWS Certified|PMP|CFA|ACCA|CKA|CEH|CISSP|CompTIA|Security\+|Network\+)\b[^\.\n]*', raw_text, re.IGNORECASE)
    for c in cert_matches:
        certifications.append(c.strip())

    domains = ["General"]
    raw_lower = raw_text.lower()
    if any(k in raw_lower for k in ["cybersecurity", "penetration testing", "vulnerability assessment", "ceh", "ethical hacking", "security"]):
        domains = ["Cybersecurity & Information Security"]
    elif any(k in raw_lower for k in ["python", "java", "fastapi", "react", "developer", "software"]):
        domains = ["Engineering & IT"]
    elif any(k in raw_lower for k in ["accounting", "ledger", "bookkeeping", "audit", "tax"]):
        domains = ["Finance & Accounting"]
    elif any(k in raw_lower for k in ["nurse", "patient", "clinical", "icu", "triage"]):
        domains = ["Healthcare"]

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
        domains=domains,
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
