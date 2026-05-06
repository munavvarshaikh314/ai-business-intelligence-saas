from sqlalchemy.orm import Session
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, CrossEncoder
import numpy as np

from app.database import SessionLocal
from app.models.document_chunk_model import DocumentChunk
from app.utils.faiss_utils import load_faiss_index


class HybridSearchService:

    embed_model = None
    reranker = None

    @staticmethod
    def get_embed_model():
        if HybridSearchService.embed_model is None:
            HybridSearchService.embed_model = SentenceTransformer("all-MiniLM-L6-v2")
        return HybridSearchService.embed_model

    @staticmethod
    def get_reranker():
        if HybridSearchService.reranker is None:
            HybridSearchService.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        return HybridSearchService.reranker

    @staticmethod
    def bm25_search(chunks, query, top_k=5):
        tokenized_chunks = [c.split() for c in chunks]
        bm25 = BM25Okapi(tokenized_chunks)

        scores = bm25.get_scores(query.split())
        top_indices = np.argsort(scores)[::-1][:top_k]

        return [(int(i), float(scores[i])) for i in top_indices]

    @staticmethod
    def faiss_search(dataset_id: str, query: str, top_k=5):
        index, meta = load_faiss_index(dataset_id)
        if not index:
            return []

        query_embedding = HybridSearchService.get_embed_model().encode([query])
        query_embedding = np.array(query_embedding).astype("float32")

        distances, indices = index.search(query_embedding, top_k)

        results = []
        for i in range(len(indices[0])):
            idx = int(indices[0][i])
            dist = float(distances[0][i])

            if idx == -1:
                continue

            similarity = float(1 / (1 + dist))  # convert L2 distance -> similarity
            results.append((idx, similarity))

        return results

    @staticmethod
    def hybrid_search(dataset_id: str, query: str, top_k=5):
        db: Session = SessionLocal()

        all_chunks = db.query(DocumentChunk).filter(
            DocumentChunk.dataset_id == dataset_id
        ).order_by(DocumentChunk.chunk_index.asc()).all()

        if not all_chunks:
            return []

        chunk_texts = [c.chunk_text for c in all_chunks]

        # Get BM25 results
        bm25_results = HybridSearchService.bm25_search(chunk_texts, query, top_k=top_k)

        # Get FAISS results
        faiss_results = HybridSearchService.faiss_search(dataset_id, query, top_k=top_k)

        # Combine scores
        score_map = {}

        # BM25 weight
        for idx, score in bm25_results:
            score_map[idx] = score_map.get(idx, 0) + (0.4 * score)

        # FAISS weight
        for idx, score in faiss_results:
            score_map[idx] = score_map.get(idx, 0) + (0.6 * score)

        # Sort by combined score
        combined_sorted = sorted(score_map.items(), key=lambda x: x[1], reverse=True)

        # Take top_k candidates for reranking
        candidate_indices = [idx for idx, _ in combined_sorted[:top_k * 2]]

        candidates = []
        for idx in candidate_indices:
            chunk_obj = all_chunks[idx]
            candidates.append(chunk_obj)

        return candidates

    @staticmethod
    def rerank(query: str, chunk_objects, top_k=5):
        """
        Cross encoder reranking (very accurate)
        """
        pairs = [(query, c.chunk_text) for c in chunk_objects]
        scores = HybridSearchService.get_reranker().predict(pairs)

        scored = list(zip(chunk_objects, scores))
        scored.sort(key=lambda x: x[1], reverse=True)

        return scored[:top_k]
