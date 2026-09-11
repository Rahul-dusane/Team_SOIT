"""
embeddings.py
Thread-safe lazy singleton EmbeddingService wrapping sentence-transformers with bounded cache and SHA-256 key hashing.
"""

import hashlib
import threading
from typing import List, Dict
import numpy as np

MAX_CACHE_SIZE = 5000


class EmbeddingService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(EmbeddingService, cls).__new__(cls)
                    cls._instance._model = None
                    cls._instance._cache: Dict[str, np.ndarray] = {}
        return cls._instance

    def _get_model(self):
        if self._model is None:
            with self._lock:
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

        # Enforce bounded LRU-style cache size
        with self._lock:
            if len(self._cache) >= MAX_CACHE_SIZE:
                # Remove oldest entry
                first_key = next(iter(self._cache))
                del self._cache[first_key]
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
