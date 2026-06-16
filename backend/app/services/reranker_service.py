from sentence_transformers import CrossEncoder
from typing import List, Tuple

_reranker = None

def get_reranker() -> CrossEncoder:
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    return _reranker

class RerankerService:

    @staticmethod
    def rerank(query: str, chunks: List[object], top_k: int = 5) -> List[Tuple[object, float]]:
        reranker = get_reranker()
        pairs = [(query, chunk.content) for chunk in chunks]
        scores = reranker.predict(pairs)
        scored = list(zip(chunks, scores))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    @staticmethod
    def rerank_texts(query: str, texts: List[str], top_k: int = 5) -> List[Tuple[str, float]]:
        reranker = get_reranker()
        pairs = [(query, text) for text in texts]
        scores = reranker.predict(pairs)
        scored = list(zip(texts, scores))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]
