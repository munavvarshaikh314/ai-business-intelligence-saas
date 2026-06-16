from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List

_model = None

def get_embedding_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

class EmbeddingService:

    @staticmethod
    def embed_texts(texts: List[str]) -> np.ndarray:
        model = get_embedding_model()
        embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        return embeddings.astype("float32")

    @staticmethod
    def embed_query(query: str) -> np.ndarray:
        model = get_embedding_model()
        embedding = model.encode([query], show_progress_bar=False, convert_to_numpy=True)
        return embedding.astype("float32")

    @staticmethod
    def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        a = a / (np.linalg.norm(a) + 1e-10)
        b = b / (np.linalg.norm(b) + 1e-10)
        return float(np.dot(a, b))
