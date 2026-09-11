"""
vector_store.py
Vector Embedding Storage and Similarity Search Engine for HireLens.
Generates 384-dimensional sentence-transformer embeddings, stores vectors in document_chunks,
and executes candidate-isolated cosine similarity retrieval.
"""

import numpy as np
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from db.models import DocumentChunkModel
from db.connection import IS_SQLITE

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
EXPECTED_DIMENSION = 384

_embedding_model_cache = None


class FallbackVectorModel:
    """Fallback 384-dim vector model if PyTorch/Transformers hits system memory limits."""
    def encode(self, text: str, normalize_embeddings: bool = True) -> np.ndarray:
        import hashlib
        vec = np.zeros(EXPECTED_DIMENSION, dtype=np.float32)
        words = text.lower().split()
        for idx, w in enumerate(words):
            h = int(hashlib.sha256(w.encode('utf-8')).hexdigest(), 16)
            dim_idx = h % EXPECTED_DIMENSION
            vec[dim_idx] += 1.0 / (idx + 1)
        norm = np.linalg.norm(vec)
        if norm > 0 and normalize_embeddings:
            vec = vec / norm
        return vec


def get_embedding_model():
    """Lazy loader for SentenceTransformer embedding model with memory limit fallback."""
    global _embedding_model_cache
    if _embedding_model_cache is None:
        try:
            from sentence_transformers import SentenceTransformer
            _embedding_model_cache = SentenceTransformer(EMBEDDING_MODEL_NAME)
        except Exception as e:
            print(f"[Warning] SentenceTransformer load failed ({e}), using FallbackVectorModel.")
            _embedding_model_cache = FallbackVectorModel()
    return _embedding_model_cache


def embed_text(text: str) -> List[float]:
    """Generates 384-dimensional normalized vector embedding for text."""
    if not text.strip():
        return [0.0] * EXPECTED_DIMENSION
    model = get_embedding_model()
    vector = model.encode(text, normalize_embeddings=True)
    
    # Validate dimension configuration
    if len(vector) != EXPECTED_DIMENSION:
        raise ValueError(f"Embedding dimension mismatch: expected {EXPECTED_DIMENSION}, got {len(vector)}")
    return vector.tolist()


def store_chunks_with_embeddings(
    db: Session,
    document_id: str,
    candidate_id: str,
    chunks: List[Dict[str, Any]]
) -> List[DocumentChunkModel]:
    """
    Computes vector embeddings for chunks and persists them into document_chunks.
    """
    from db.repositories import DocumentRepository
    
    chunks_with_vectors = []
    for chunk in chunks:
        vec = embed_text(chunk["content"])
        chunk_copy = dict(chunk)
        chunk_copy["embedding"] = vec
        chunk_copy["embedding_model"] = EMBEDDING_MODEL_NAME
        chunks_with_vectors.append(chunk_copy)

    doc_repo = DocumentRepository(db)
    return doc_repo.save_chunks(document_id, candidate_id, chunks_with_vectors)


def retrieve_evidence_from_vector_store(
    db: Session,
    candidate_id: str,
    query_text: str,
    top_k: int = 3
) -> List[Dict[str, Any]]:
    """
    Candidate-Isolated Vector Similarity Search.
    Queries stored document chunks filtered strictly by candidate_id.
    Uses pgvector cosine distance (<->) on PostgreSQL, or NumPy cosine similarity fallback on SQLite.
    Returns list of dicts:
    [{"content": str, "page_number": int, "section_title": str, "similarity": float}]
    """
    if not candidate_id or not query_text.strip():
        return []

    query_vector = embed_text(query_text)

    # 1. PostgreSQL + pgvector query path
    if not IS_SQLITE:
        try:
            from sqlalchemy import text
            sql = text("""
                SELECT content, page_number, section_title, start_char, end_char,
                       1 - (embedding <=> :query_vec) AS similarity
                FROM document_chunks
                WHERE candidate_id = :candidate_id AND embedding IS NOT NULL
                ORDER BY embedding <=> :query_vec
                LIMIT :top_k
            """)
            result = db.execute(sql, {
                "candidate_id": candidate_id,
                "query_vec": str(query_vector),
                "top_k": top_k
            }).fetchall()

            return [
                {
                    "content": row.content,
                    "page_number": row.page_number or 1,
                    "section_title": row.section_title or "",
                    "similarity": round(float(row.similarity), 4)
                } for row in result
            ]
        except Exception:
            pass  # Fallback to python-side cosine similarity if pgvector extension query fails

    # 2. In-memory / SQLite fallback path
    chunks = db.query(DocumentChunkModel).filter(
        DocumentChunkModel.candidate_id == candidate_id
    ).all()

    if not chunks:
        return []

    q_arr = np.array(query_vector, dtype=np.float32)
    q_norm = np.linalg.norm(q_arr)
    if q_norm == 0:
        q_norm = 1.0

    scored_chunks = []
    for chunk in chunks:
        if not chunk.embedding:
            continue
        c_arr = np.array(chunk.embedding, dtype=np.float32)
        c_norm = np.linalg.norm(c_arr)
        if c_norm == 0:
            continue
        sim = float(np.dot(q_arr, c_arr) / (q_norm * c_norm))
        scored_chunks.append((sim, chunk))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)

    results = []
    for sim, chunk in scored_chunks[:top_k]:
        results.append({
            "content": chunk.content,
            "page_number": chunk.page_number or 1,
            "section_title": chunk.section_title or "",
            "similarity": round(sim, 4)
        })

    return results
