from app.celery_app import celery
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.dataset_model import Dataset
from app.services.upload_service import UploadService


@celery.task(bind=True)
def index_pdf_task(self, dataset_id: str, user_id: str, file_path: str):
    db: Session = SessionLocal()

    dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id,
        Dataset.user_id == user_id
    ).first()

    if not dataset:
        return {"status": "FAILED", "error": "Dataset not found"}

    try:
        dataset.index_status = "PROCESSING"
        dataset.index_progress = 10
        db.commit()

        # Build FAISS index
        UploadService.build_pdf_faiss_index(dataset_id, user_id, file_path)

        dataset.index_status = "COMPLETED"
        dataset.index_progress = 100
        db.commit()

        return {"status": "COMPLETED"}

    except Exception as e:
        dataset.index_status = "FAILED"
        dataset.index_progress = 0
        db.commit()

        return {"status": "FAILED", "error": str(e)}