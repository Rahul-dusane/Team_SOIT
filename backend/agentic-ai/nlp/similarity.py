"""
similarity.py
Cosine similarity calculations for text, skills, and vector embeddings.
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine_similarity
from .embeddings import embed_text


def semantic_similarity(text_a: str, text_b: str) -> float:
    """
    Computes cosine similarity (0.0 to 1.0) between two text strings using embeddings.
    """
    if not text_a or not text_b:
        return 0.0

    vec_a = embed_text(text_a)
    vec_b = embed_text(text_b)

    if np.all(vec_a == 0) or np.all(vec_b == 0):
        return 0.0

    similarity = sklearn_cosine_similarity([vec_a], [vec_b])[0][0]
    return float(np.clip(similarity, 0.0, 1.0))
