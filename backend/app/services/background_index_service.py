import os
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.dataset_model import Dataset
from app.services.upload_service import UploadService


class BackgroundIndexService:

    @staticmethod
    def index_pdf(dataset_id: str, user_id: str, file_path: str):
        db: Session = SessionLocal()

        dataset = db.query(Dataset).filter(
            Dataset.id == dataset_id,
            Dataset.user_id == user_id
        ).first()

        if not dataset:
            return

        try:
            dataset.index_status = "PROCESSING"
            dataset.index_progress = 10
            db.commit()

            # call your PDF indexing logic
            UploadService.build_pdf_faiss_index(dataset_id, user_id, file_path)

            dataset.index_status = "COMPLETED"
            dataset.index_progress = 100
            db.commit()

        except Exception:
            dataset.index_status = "FAILED"
            dataset.index_progress = 0
            db.commit()