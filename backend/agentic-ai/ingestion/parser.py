"""
parser.py
Multi-format Document Parsers for PDF, DOCX, and TXT.
Extracts text while preserving explicit page numbers, section headers, and character locations.
"""

import io
from typing import List, Dict, Any, Tuple


def parse_pdf(content: bytes) -> Tuple[str, List[Dict[str, Any]], Dict[str, Any]]:
    """
    Parses PDF bytes preserving page numbers and per-page text layout.
    Returns (full_text, pages_list, metadata).
    Each page in pages_list is {"page_number": int, "text": str, "char_count": int}.
    """
    pages = []
    full_text_parts = []

    # Attempt PyMuPDF (fitz) first, fallback to pypdf
    try:
        import fitz
        doc = fitz.open(stream=content, filetype="pdf")
        if doc.is_encrypted:
            raise ValueError("encrypted_pdf_unsupported")

        for page_idx in range(len(doc)):
            page = doc[page_idx]
            page_text = page.get_text("text") or ""
            pages.append({
                "page_number": page_idx + 1,
                "text": page_text,
                "char_count": len(page_text)
            })
            full_text_parts.append(page_text)
        doc.close()

    except Exception:
        # Fallback to pypdf
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(content))
            if reader.is_encrypted:
                raise ValueError("encrypted_pdf_unsupported")

            for page_idx, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                pages.append({
                    "page_number": page_idx + 1,
                    "text": page_text,
                    "char_count": len(page_text)
                })
                full_text_parts.append(page_text)

        except Exception as e:
            if "encrypted" in str(e).lower():
                raise ValueError("encrypted_pdf_unsupported")
            raise ValueError(f"pdf_parsing_failed: {str(e)}")

    full_text = "\n\n".join(full_text_parts)

    # Scanned PDF check
    if not full_text.strip():
        return "", pages, {"status": "scanned_pdf_no_text", "warning": "No selectable text found in PDF. Scanned or image-only document."}

    return full_text, pages, {"status": "success", "total_pages": len(pages)}


def parse_docx(content: bytes) -> Tuple[str, List[Dict[str, Any]], Dict[str, Any]]:
    """
    Parses DOCX bytes extracting paragraphs, headings, and tables.
    Returns (full_text, sections_list, metadata).
    """
    try:
        import docx
        doc = docx.Document(io.BytesIO(content))
        sections = []
        full_text_parts = []
        current_section = "General Information"
        section_text_parts = []

        for p in doc.paragraphs:
            text = p.text.strip()
            if not text:
                continue

            if p.style and p.style.name.startswith("Heading"):
                if section_text_parts:
                    sec_text = "\n".join(section_text_parts)
                    sections.append({"section_title": current_section, "text": sec_text, "page_number": 1})
                    full_text_parts.append(sec_text)
                    section_text_parts = []
                current_section = text

            section_text_parts.append(text)

        # Include tables
        for table in doc.tables:
            table_rows = []
            for row in table.rows:
                row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_cells:
                    table_rows.append(" | ".join(row_cells))
            if table_rows:
                section_text_parts.append("\n".join(table_rows))

        if section_text_parts:
            sec_text = "\n".join(section_text_parts)
            sections.append({"section_title": current_section, "text": sec_text, "page_number": 1})
            full_text_parts.append(sec_text)

        full_text = "\n\n".join(full_text_parts)
        return full_text, sections, {"status": "success", "total_sections": len(sections)}

    except Exception as e:
        raise ValueError(f"docx_parsing_failed: {str(e)}")


def parse_txt(content: bytes) -> Tuple[str, List[Dict[str, Any]], Dict[str, Any]]:
    """Parses plain text bytes."""
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        text = content.decode("latin-1", errors="ignore")

    pages = [{"page_number": 1, "text": text, "char_count": len(text)}]
    return text, pages, {"status": "success", "total_pages": 1}


def parse_document(filename: str, content: bytes) -> Tuple[str, List[Dict[str, Any]], Dict[str, Any]]:
    """Unified document parser dispatcher."""
    ext = "." + filename.split(".")[-1].lower() if "." in filename else ""
    if ext == ".pdf":
        return parse_pdf(content)
    elif ext == ".docx":
        return parse_docx(content)
    elif ext == ".txt":
        return parse_txt(content)
    else:
        raise ValueError(f"unsupported_file_extension: {ext}")
