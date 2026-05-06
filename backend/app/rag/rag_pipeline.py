import os
import pickle
import faiss
from typing import List, Dict

from app.rag.prompt_template import build_rag_prompt
from app.rag.confidence import compute_confidence
from app.services.llm_service import LLMService


FAISS_DIR = "app/storage/faiss_indexes"


class RAGPipeline:

    @staticmethod
    def load_index(dataset_id: str):
        index_path = os.path.join(FAISS_DIR, f"{dataset_id}.index")
        meta_path = os.path.join(FAISS_DIR, f"{dataset_id}_meta.pkl")

        if not os.path.exists(index_path) or not os.path.exists(meta_path):
            return None, None

        index = faiss.read_index(index_path)

        with open(meta_path, "rb") as f:
            metadata = pickle.load(f)

        return index, metadata

    @staticmethod
    def retrieve(dataset_id: str, query: str, top_k: int = 5) -> Dict:
        index, metadata = RAGPipeline.load_index(dataset_id)

        if index is None:
            return {"chunks": [], "confidence": 0.0}

        from sentence_transformers import SentenceTransformer
        import numpy as np

        model = SentenceTransformer("all-MiniLM-L6-v2")
        q_emb = model.encode([query])
        q_emb = np.array(q_emb).astype("float32")

        distances, indices = index.search(q_emb, top_k)

        chunks = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            meta = metadata[idx]
            chunks.append({
                "chunk_index": meta.get("chunk_index"),
                "page_number": meta.get("page_number"),
                "text": meta.get("text"),
                "distance": float(dist)
            })

        conf = compute_confidence(list(distances[0]))

        return {"chunks": chunks, "confidence": conf}

    @staticmethod
    def answer(dataset_id: str, query: str, top_k: int = 5) -> Dict:
        retrieval = RAGPipeline.retrieve(dataset_id, query, top_k)
        chunks = retrieval["chunks"]

        prompt = build_rag_prompt(query, chunks)

        response = LLMService.generate_text(prompt)

        return {
            "answer": response,
            "chunks": chunks,
            "confidence": retrieval["confidence"]
        }