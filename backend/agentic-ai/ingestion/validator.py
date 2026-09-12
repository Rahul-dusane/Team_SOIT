"""
validator.py
Server-side File Validation for Resume Ingestion.
Validates file extension, size limits, SHA-256 duplicate hash, PDF encryption, and DOCX decompression safety.
"""

import hashlib
import zipfile
from typing import Tuple, Dict, Any

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def calculate_file_hash(content: bytes) -> str:
    """Calculates SHA-256 hex digest of file contents for deduplication."""
    return hashlib.sha256(content).hexdigest()


def validate_file(filename: str, content: bytes) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Validates a file upload.
    Returns (is_valid, error_code_or_message, metadata_dict).
    """
    if not filename:
        return False, "empty_filename", {}

    ext = "." + filename.split(".")[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"unsupported_file_type: '{ext}'. Allowed: {list(ALLOWED_EXTENSIONS)}", {}

    file_size = len(content)
    if file_size == 0:
        return False, "empty_file", {}
    if file_size > MAX_FILE_SIZE_BYTES:
        return False, f"file_size_exceeded: {file_size} bytes exceeds max 10MB limit.", {}

    file_hash = calculate_file_hash(content)

    # Extension specific safety checks
    if ext == ".pdf":
        if not content.startswith(b"%PDF"):
            return False, "corrupted_pdf_header", {}
        # Check for encrypted PDF signature
        if b"/Encrypt" in content:
            return False, "encrypted_pdf_unsupported", {}

    elif ext == ".docx":
        # DOCX is a zip file containing word/document.xml
        try:
            with zipfile.ZipFile(bytes_io(content)) as zf:
                # Check for zip bomb / decompression ratio limit
                total_uncompressed = sum(file_detail.file_size for file_detail in zf.infolist())
                if total_uncompressed > 50 * 1024 * 1024:  # 50MB decompressed limit
                    return False, "docx_decompression_limit_exceeded", {}
                if "word/document.xml" not in zf.namelist():
                    return False, "invalid_docx_structure", {}
        except Exception:
            return False, "corrupted_docx_archive", {}

    metadata = {
        "filename": filename,
        "extension": ext,
        "size_bytes": file_size,
        "file_hash": file_hash
    }

    return True, "valid", metadata


def bytes_io(content: bytes):
    import io
    return io.BytesIO(content)
