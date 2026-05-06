from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.dataset_model import Dataset


class DatasetGuard:

    @staticmethod
    def check_access(user_id: str, dataset_id: str):
        db: Session = SessionLocal()

        dataset = db.query(Dataset).filter(
            Dataset.id == dataset_id,
            Dataset.user_id == user_id
        ).first()

        if not dataset:
            raise HTTPException(status_code=403, detail="Dataset access denied")

        return dataset