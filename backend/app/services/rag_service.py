from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.dataset_model import Dataset
from app.models.document_chunk_model import DocumentChunk
from app.services.hybrid_search_service import HybridSearchService


class RAGService:

    @staticmethod
    def retrieve(dataset_id: str, user_id: str, query: str, top_k: int = 5):
        db: Session = SessionLocal()
        try:
            dataset = db.query(Dataset).filter(
                Dataset.id == dataset_id,
                Dataset.user_id == user_id
            ).first()

            if not dataset:
                raise HTTPException(status_code=404, detail="Dataset not found")

            if dataset.index_status in {"QUEUED", "PROCESSING"}:
                raise HTTPException(
                    status_code=409,
                    detail=f"PDF indexing is still {dataset.index_status.lower()}. Please wait."
                )

            if dataset.index_status == "FAILED":
                raise HTTPException(
                    status_code=400,
                    detail="PDF indexing failed. Please re-upload the PDF."
                )
        finally:
            db.close()

        # Fast hybrid search. CrossEncoder reranking is skipped in normal chat
        # because loading it can add 10-20 seconds on local machines.
        ranked_chunks = HybridSearchService.hybrid_search_with_scores(dataset_id, query, top_k=top_k)

        if not ranked_chunks:
            return {"chunks": [], "scores": [], "sources": []}

        chunks = []
        scores = []
        sources = []

        for chunk_obj, score in ranked_chunks:
            # Support both field names — content (current) and chunk_text (future)
            text = getattr(chunk_obj, "content", None) or getattr(chunk_obj, "chunk_text", None)

            if not text or not text.strip():
                continue

            chunks.append(text)
            scores.append(float(score))
            sources.append({
                "chunk_index": getattr(chunk_obj, "chunk_index", None),
                "score": float(score),
                "text_snippet": text[:150] + "..." if len(text) > 150 else text,
            })

        return {
            "chunks": chunks,
            "scores": scores,
            "sources": sources,
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
                    "chunk_text": chunk.content,
                    "chunk_index": chunk.chunk_index,
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
                raise HTTPException(
                    status_code=400,
                    detail="No PDF file found. Please upload a PDF first."
                )

            UploadService.build_pdf_faiss_index(dataset_id, user_id, file.file_path)
            return {"message": "PDF index rebuilt successfully"}
        finally:
            db.close()

# from fastapi import HTTPException
# from sqlalchemy.orm import Session
# from sentence_transformers import SentenceTransformer
# import numpy as np

# from app.database import SessionLocal
# from app.models.dataset_model import Dataset
# from app.models.document_chunk_model import DocumentChunk
# from app.utils.faiss_utils import load_faiss_index
# from app.services.hybrid_search_service import HybridSearchService



# class RAGService:

#     @staticmethod
#     def retrieve(dataset_id: str, user_id: str, query: str, top_k: int = 5):
#         db: Session = SessionLocal()

#         dataset = db.query(Dataset).filter(
#             Dataset.id == dataset_id,
#             Dataset.user_id == user_id
#         ).first()

#         if not dataset:
#             raise HTTPException(status_code=404, detail="Dataset not found")

#         if dataset.index_status in {"QUEUED", "PROCESSING"}:
#             raise HTTPException(
#                 status_code=409,
#                 detail=f"PDF indexing is still {dataset.index_status.lower()}. Please wait until it reaches 100%."
#             )

#         if dataset.index_status == "FAILED":
#             raise HTTPException(
#                 status_code=400,
#                 detail="PDF indexing failed. Please upload the PDF again or try another readable PDF."
#             )

#         # Hybrid Search (BM25 + FAISS)
#         candidates = HybridSearchService.hybrid_search(dataset_id, query, top_k=top_k)

#         if not candidates:
#             return {"chunks": [], "scores": [], "sources": []}

#         # Cross Encoder Reranking
#         reranked = HybridSearchService.rerank(query, candidates, top_k=top_k)

#         chunks = []
#         scores = []
#         sources = []

#         for chunk_obj, score in reranked:
#             chunks.append(chunk_obj.content)
#             scores.append(float(score))

#             sources.append({
#                 "page": None,
#                 "chunk_index": chunk_obj.chunk_index,
#                 "score": float(score)
#             })

#         return {
#             "chunks": chunks,
#             "scores": scores,
#             "sources": sources
#         }

#     @staticmethod
#     def get_chunks(dataset_id: str, user_id: str):
#         db: Session = SessionLocal()
#         try:
#             dataset = db.query(Dataset).filter(
#                 Dataset.id == dataset_id,
#                 Dataset.user_id == user_id
#             ).first()

#             if not dataset:
#                 raise HTTPException(status_code=404, detail="Dataset not found")

#             chunks = db.query(DocumentChunk).filter(
#                 DocumentChunk.dataset_id == dataset_id
#             ).order_by(DocumentChunk.chunk_index.asc()).all()

#             return [
#                 {
#                     "id": str(chunk.id),
#                     "chunk_text": chunk.content,
#                     "chunk_index": chunk.chunk_index,
#                     "page_number": None,
#                 }
#                 for chunk in chunks
#             ]
#         finally:
#             db.close()

#     @staticmethod
#     def build_index(dataset_id: str, user_id: str):
#         from app.models.file_model import File
#         from app.services.upload_service import UploadService

#         db: Session = SessionLocal()
#         try:
#             dataset = db.query(Dataset).filter(
#                 Dataset.id == dataset_id,
#                 Dataset.user_id == user_id
#             ).first()

#             if not dataset:
#                 raise HTTPException(status_code=404, detail="Dataset not found")

#             file = db.query(File).filter(
#                 File.dataset_id == dataset_id,
#                 File.user_id == user_id,
#                 File.file_type == "pdf"
#             ).order_by(File.uploaded_at.desc()).first()

#             if not file:
#                 raise HTTPException(status_code=400, detail="No PDF file found for this dataset")

#             UploadService.build_pdf_faiss_index(dataset_id, user_id, file.file_path)
#             return {"message": "PDF index built successfully"}
#         finally:
#             db.close()
