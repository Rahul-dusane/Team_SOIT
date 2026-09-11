"""
Basic text normalization used before any extraction/matching step.
"""

import re


def clean_text(text: str) -> str:
    """
    Lowercase, collapse whitespace, and strip characters that don't help
    matching (keeps letters, digits, +, #, ., / and whitespace so tokens
    like 'c++', 'c#', 'node.js', 'ci/cd' survive intact).
    """
    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"[^a-z0-9+#./\s\-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
