"""
similarity.py
Cosine similarity calculations for text, skills, and vector embeddings.
"""

import re
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine_similarity
from .embeddings import embed_text


def semantic_similarity(text_a: str, text_b: str) -> float:
    """
    Computes cosine similarity (0.0 to 1.0) between two text strings using embeddings.
    Combines vector similarity with token overlap for robust similarity scoring across vector models.
    """
    if not text_a or not text_b:
        return 0.0

    vec_a = embed_text(text_a)
    vec_b = embed_text(text_b)

    if np.all(vec_a == 0) or np.all(vec_b == 0):
        return 0.0

    similarity = float(np.clip(sklearn_cosine_similarity([vec_a], [vec_b])[0][0], 0.0, 1.0))

    # Token-level overlap boost for text similarity
    words_a = set(re.findall(r'\b\w+\b', text_a.lower()))
    words_b = set(re.findall(r'\b\w+\b', text_b.lower()))
    stop_words = {"with", "and", "or", "the", "a", "an", "in", "on", "for", "to", "of", "is", "at"}
    content_a = words_a - stop_words
    content_b = words_b - stop_words

    if content_a and content_b:
        intersection = content_a.intersection(content_b)
        token_sim = len(intersection) / max(min(len(content_a), len(content_b)), 1)
        similarity = max(similarity, float(token_sim))

    return float(np.clip(similarity, 0.0, 1.0))
