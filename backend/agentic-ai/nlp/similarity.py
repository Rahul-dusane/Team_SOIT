"""
similarity.py
Cosine similarity calculations for text, skills, and vector embeddings.
"""

import re
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine_similarity
from .embeddings import embed_text


SYNONYM_GROUPS = [
    {"developer", "engineer", "programmer", "coder", "dev"},
    {"api", "apis", "rest", "endpoint", "endpoints", "microservice", "microservices", "service", "services"},
    {"backend", "back-end", "server-side"},
    {"frontend", "front-end", "ui", "client-side"},
    {"experience", "background", "history", "expertise", "knowledge"},
    {"build", "building", "create", "creating", "design", "designing", "develop", "developing"}
]


def _stem_word(w: str) -> str:
    w = w.lower()
    if len(w) > 3 and w.endswith('s') and not w.endswith('ss'):
        w = w[:-1]
    if len(w) > 4 and w.endswith('ing'):
        w = w[:-3]
    if len(w) > 4 and w.endswith('ed'):
        w = w[:-2]
    return w


def _words_are_synonyms(w1: str, w2: str) -> bool:
    s1, s2 = _stem_word(w1), _stem_word(w2)
    if s1 == s2:
        return True
    for group in SYNONYM_GROUPS:
        if (w1.lower() in group or s1 in group) and (w2.lower() in group or s2 in group):
            return True
    return False


def semantic_similarity(text_a: str, text_b: str) -> float:
    """
    Computes cosine similarity (0.0 to 1.0) between two text strings using embeddings.
    Combines vector similarity with stem and synonym aware token overlap for robust similarity scoring across vector models.
    """
    if not text_a or not text_b:
        return 0.0

    vec_a = embed_text(text_a)
    vec_b = embed_text(text_b)

    similarity = 0.0
    if not np.all(vec_a == 0) and not np.all(vec_b == 0):
        similarity = float(np.clip(sklearn_cosine_similarity([vec_a], [vec_b])[0][0], 0.0, 1.0))

    # Token-level stem & synonym overlap boost for text similarity
    words_a = re.findall(r'\b\w+\b', text_a.lower())
    words_b = re.findall(r'\b\w+\b', text_b.lower())
    stop_words = {"with", "and", "or", "the", "a", "an", "in", "on", "for", "to", "of", "is", "at"}
    content_a = [w for w in words_a if w not in stop_words]
    content_b = [w for w in words_b if w not in stop_words]

    if content_a and content_b:
        matched_score = 0.0
        used_b = set()
        for wa in content_a:
            for idx_b, wb in enumerate(content_b):
                if idx_b in used_b:
                    continue
                if wa == wb or _stem_word(wa) == _stem_word(wb):
                    matched_score += 1.0
                    used_b.add(idx_b)
                    break
                elif _words_are_synonyms(wa, wb):
                    matched_score += 0.85
                    used_b.add(idx_b)
                    break

        denom = min(len(content_a), len(content_b))
        token_sim = matched_score / denom if denom > 0 else 0.0
        similarity = max(similarity, float(token_sim))

    return float(np.clip(similarity, 0.0, 1.0))

