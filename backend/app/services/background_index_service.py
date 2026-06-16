import os
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.dataset_model import Dataset
from app.services.upload_service import UploadService
from app.services.logging_service import LoggingService


class BackgroundIndexService:

    @staticmethod
    def index_pdf(dataset_id: str, user_id: str, file_path: str, file_id: str = None):
        db: Session = SessionLocal()
        dataset = None
        try:
            LoggingService.info(f"Starting offline PDF indexing for {dataset_id}")

            dataset = db.query(Dataset).filter(
                Dataset.id == dataset_id,
                Dataset.user_id == user_id
            ).first()

            if not dataset:
                return

            dataset.index_status = "PROCESSING"
            dataset.index_progress = 10
            db.commit()

            # call your PDF indexing logic
            UploadService.build_pdf_faiss_index(dataset_id, user_id, file_path, file_id=file_id)

            dataset.index_status = "COMPLETED"
            dataset.index_progress = 100
            db.commit()
            LoggingService.info(f"Successfully completed offline PDF indexing for {dataset_id}")

        except Exception as exc:
            LoggingService.error(f"PDF indexing failed for {dataset_id}: {exc}")
            if dataset:
                dataset.index_status = "FAILED"
                dataset.index_progress = 0
                db.commit()
        finally:
            db.close()
