"""
embeddings.py
Lazy singleton EmbeddingService wrapping sentence-transformers with MD5/SHA-256 text hash caching.
"""

import hashlib
from typing import List, Dict, Union
import numpy as np

class EmbeddingService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            cls._instance._model = None
            cls._instance._cache: Dict[str, np.ndarray] = {}
        return cls._instance

    def _get_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
        return self._model

    def _hash_text(self, text: str) -> str:
        return hashlib.sha256(text.strip().lower().encode("utf-8")).hexdigest()

    def embed_text(self, text: str) -> np.ndarray:
        """Embed a single string text into a numpy vector embedding."""
        if not text or not text.strip():
            return np.zeros(384, dtype=np.float32)

        key = self._hash_text(text)
        if key in self._cache:
            return self._cache[key]

        model = self._get_model()
        vector = model.encode(text, convert_to_numpy=True)
        self._cache[key] = vector
        return vector

    def embed_skills(self, skills: List[str]) -> List[np.ndarray]:
        """Embed a list of skill strings into a list of numpy vectors."""
        return [self.embed_text(s) for s in skills]


# Global singleton helper functions
_embedding_service = EmbeddingService()


def embed_text(text: str) -> np.ndarray:
    return _embedding_service.embed_text(text)


def embed_skills(skills: List[str]) -> List[np.ndarray]:
    return _embedding_service.embed_skills(skills)
