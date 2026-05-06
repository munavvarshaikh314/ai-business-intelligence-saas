import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict
from app.rag.reranking import rerank_chunks


class HybridSearchEngine:
    def __init__(self, index: faiss.Index, metadata: List[Dict]):
        self.index = index
        self.metadata = metadata
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        query_embedding = self.model.encode([query])
        query_embedding = np.array(query_embedding).astype("float32")

        distances, indices = self.index.search(query_embedding, top_k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue

            meta = self.metadata[idx]
            results.append({
                "chunk_index": meta.get("chunk_index"),
                "page_number": meta.get("page_number"),
                "text": meta.get("text", ""),
                "distance": float(dist)
            })

        results = rerank_chunks(query, results)
        return results