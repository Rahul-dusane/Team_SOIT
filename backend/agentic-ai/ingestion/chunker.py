"""
chunker.py
Context-Aware Document Chunker.
Splits text into overlapping sliding-window chunks while preserving page numbers, start/end character offsets, and section titles.
"""

from typing import List, Dict, Any


def chunk_pages_or_sections(
    structured_units: List[Dict[str, Any]],
    chunk_size_words: int = 250,
    overlap_words: int = 50
) -> List[Dict[str, Any]]:
    """
    Chunks structured units (pages or sections) into overlapping text chunks with exact source metadata.
    Returns list of dicts:
    {
        "content": str,
        "page_number": int,
        "start_char": int,
        "end_char": int,
        "section_title": str,
        "word_count": int
    }
    """
    chunks = []
    global_char_offset = 0

    for unit in structured_units:
        page_num = unit.get("page_number", 1)
        sec_title = unit.get("section_title", "Document Content")
        text = unit.get("text", "")
        if not text.strip():
            continue

        words = text.split()
        if not words:
            continue

        step = max(1, chunk_size_words - overlap_words)
        for i in range(0, len(words), step):
            chunk_words = words[i:i + chunk_size_words]
            chunk_text = " ".join(chunk_words)
            
            # Estimate character boundaries within unit
            try:
                start_in_unit = text.index(chunk_words[0])
            except (ValueError, IndexError):
                start_in_unit = 0

            start_char = global_char_offset + start_in_unit
            end_char = start_char + len(chunk_text)

            chunks.append({
                "content": chunk_text,
                "page_number": page_num,
                "start_char": start_char,
                "end_char": end_char,
                "section_title": sec_title,
                "word_count": len(chunk_words)
            })

            if i + chunk_size_words >= len(words):
                break

        global_char_offset += len(text) + 2

    return chunks
