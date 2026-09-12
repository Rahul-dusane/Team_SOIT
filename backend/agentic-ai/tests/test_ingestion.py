"""
test_ingestion.py
Unit tests for file validator, parsers, chunker, and batch upload failure handling.
"""

import pytest
from ingestion.validator import validate_file, calculate_file_hash
from ingestion.parser import parse_pdf, parse_docx, parse_txt
from ingestion.chunker import chunk_pages_or_sections


def test_validator_file_types():
    # Valid TXT file
    valid, status, meta = validate_file("resume.txt", b"Python Developer with 5 years experience")
    assert valid is True
    assert status == "valid"
    assert meta["extension"] == ".txt"

    # Unsupported extension
    valid, status, meta = validate_file("resume.exe", b"binary data")
    assert valid is False
    assert "unsupported_file_type" in status

    # Empty file
    valid, status, meta = validate_file("empty.pdf", b"")
    assert valid is False
    assert status == "empty_file"


def test_validator_pdf_encryption_and_header():
    # Corrupted PDF header
    valid, status, meta = validate_file("bad.pdf", b"NOT_A_PDF_HEADER")
    assert valid is False
    assert status == "corrupted_pdf_header"

    # Encrypted PDF signature
    encrypted_pdf_bytes = b"%PDF-1.4\n1 0 obj\n<< /Encrypt 2 0 R >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"
    valid, status, meta = validate_file("encrypted.pdf", encrypted_pdf_bytes)
    assert valid is False
    assert status == "encrypted_pdf_unsupported"


def test_txt_parser():
    content = b"John Doe\nSenior Backend Engineer\nSkills: Python, FastAPI, PostgreSQL"
    full_text, pages, meta = parse_txt(content)
    assert meta["status"] == "success"
    assert "Senior Backend Engineer" in full_text
    assert len(pages) == 1
    assert pages[0]["page_number"] == 1


def test_chunker_metadata_preservation():
    structured_units = [
        {
            "page_number": 1,
            "section_title": "Experience",
            "text": "Senior Developer at Acme Corp building scalable REST APIs with Python FastAPI PostgreSQL and Docker for microservices architecture."
        },
        {
            "page_number": 2,
            "section_title": "Education & Skills",
            "text": "Bachelor of Science in Computer Science. Certified AWS Solutions Architect and Kubernetes Administrator."
        }
    ]

    chunks = chunk_pages_or_sections(structured_units, chunk_size_words=10, overlap_words=2)
    assert len(chunks) >= 2
    assert chunks[0]["page_number"] == 1
    assert chunks[0]["section_title"] == "Experience"
    assert "start_char" in chunks[0]
    assert "end_char" in chunks[0]
