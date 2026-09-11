import re
from typing import List, Dict, Any


def chunk_pages_or_sections(
    structured_units: List[Dict[str, Any]],
    chunk_size_words: int = 250,
    overlap_words: int = 50
) -> List[Dict[str, Any]]:
    """
    Chunks structured units (pages or sections) into overlapping text chunks with exact source metadata.
    Uses regex word span indices to guarantee start_char and end_char exactly slice the original text.
    """
    chunks = []
    global_offset = 0

    for unit in structured_units:
        page_num = unit.get("page_number", 1)
        sec_title = unit.get("section_title", "Document Content")
        text = unit.get("text", "")
        if not text.strip():
            continue

        # Find word tokens with their exact character start and end spans in original text
        word_spans = []
        for match in re.finditer(r'\S+', text):
            word_spans.append((match.start(), match.end()))

        if not word_spans:
            continue

        step = max(1, chunk_size_words - overlap_words)
        for i in range(0, len(word_spans), step):
            window = word_spans[i:i + chunk_size_words]
            if not window:
                break
            
            unit_start_char = window[0][0]
            unit_end_char = window[-1][1]
            chunk_text = text[unit_start_char:unit_end_char]
            
            start_char = global_offset + unit_start_char
            end_char = global_offset + unit_end_char

            chunks.append({
                "content": chunk_text,
                "page_number": page_num,
                "start_char": start_char,
                "end_char": end_char,
                "section_title": sec_title,
                "word_count": len(window)
            })

            if i + chunk_size_words >= len(word_spans):
                break

        global_offset += len(text) + 2

    return chunks
