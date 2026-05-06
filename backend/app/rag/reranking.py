from typing import List, Dict


def rerank_chunks(query: str, chunks: List[Dict]) -> List[Dict]:
    """
    Simple reranker (keyword match scoring).
    Later you can replace with CrossEncoder reranking.
    """

    query_words = set(query.lower().split())

    def score(chunk):
        text = chunk.get("text", "").lower()
        score_val = sum(1 for w in query_words if w in text)
        return score_val

    return sorted(chunks, key=score, reverse=True)