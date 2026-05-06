from fastapi import HTTPException
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
import numpy as np

from app.database import SessionLocal
from app.models.dataset_model import Dataset
from app.models.document_chunk_model import DocumentChunk
from app.utils.faiss_utils import load_faiss_index
from app.services.hybrid_search_service import HybridSearchService



class RAGService:

    @staticmethod
    def retrieve(dataset_id: str, user_id: str, query: str, top_k: int = 5):
        db: Session = SessionLocal()

        dataset = db.query(Dataset).filter(
            Dataset.id == dataset_id,
            Dataset.user_id == user_id
        ).first()

        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        # Hybrid Search (BM25 + FAISS)
        candidates = HybridSearchService.hybrid_search(dataset_id, query, top_k=top_k)

        if not candidates:
            return {"chunks": [], "scores": [], "sources": []}

        # Cross Encoder Reranking
        reranked = HybridSearchService.rerank(query, candidates, top_k=top_k)

        chunks = []
        scores = []
        sources = []

        for chunk_obj, score in reranked:
            chunks.append(chunk_obj.chunk_text)
            scores.append(float(score))

            sources.append({
                "page": chunk_obj.page_number,
                "chunk_index": chunk_obj.chunk_index,
                "score": float(score)
            })

        return {
            "chunks": chunks,
            "scores": scores,
            "sources": sources
        }

    @staticmethod
    def get_chunks(dataset_id: str, user_id: str):
        db: Session = SessionLocal()
        try:
            dataset = db.query(Dataset).filter(
                Dataset.id == dataset_id,
                Dataset.user_id == user_id
            ).first()

            if not dataset:
                raise HTTPException(status_code=404, detail="Dataset not found")

            chunks = db.query(DocumentChunk).filter(
                DocumentChunk.dataset_id == dataset_id
            ).order_by(DocumentChunk.chunk_index.asc()).all()

            return [
                {
                    "id": str(chunk.id),
                    "chunk_text": chunk.chunk_text,
                    "chunk_index": chunk.chunk_index,
                    "page_number": chunk.page_number,
                }
                for chunk in chunks
            ]
        finally:
            db.close()

    @staticmethod
    def build_index(dataset_id: str, user_id: str):
        from app.models.file_model import File
        from app.services.upload_service import UploadService

        db: Session = SessionLocal()
        try:
            dataset = db.query(Dataset).filter(
                Dataset.id == dataset_id,
                Dataset.user_id == user_id
            ).first()

            if not dataset:
                raise HTTPException(status_code=404, detail="Dataset not found")

            file = db.query(File).filter(
                File.dataset_id == dataset_id,
                File.user_id == user_id,
                File.file_type == "pdf"
            ).order_by(File.uploaded_at.desc()).first()

            if not file:
                raise HTTPException(status_code=400, detail="No PDF file found for this dataset")

            UploadService.build_pdf_faiss_index(dataset_id, user_id, file.file_path)
            return {"message": "PDF index built successfully"}
        finally:
            db.close()
