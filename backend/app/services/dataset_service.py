import uuid
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.dataset_model import Dataset


class DatasetService:

    @staticmethod
    def create_dataset(payload, user_id: str):
        db: Session = SessionLocal()

        dataset = Dataset(
            user_id=user_id,
            dataset_name=payload.dataset_name,
            dataset_type=payload.dataset_type,
            description=payload.description
        )

        db.add(dataset)
        db.commit()
        db.refresh(dataset)

        return dataset

    @staticmethod
    def get_datasets(user_id: str):
        db: Session = SessionLocal()
        datasets = db.query(Dataset).filter(Dataset.user_id == user_id).all()
        return datasets

    @staticmethod
    def get_dataset(dataset_id: str, user_id: str):
        db: Session = SessionLocal()

        dataset = db.query(Dataset).filter(
            Dataset.id == dataset_id,
            Dataset.user_id == user_id
        ).first()

        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        return dataset

    @staticmethod
    def delete_dataset(dataset_id: str, user_id: str):
        db: Session = SessionLocal()

        dataset = db.query(Dataset).filter(
            Dataset.id == dataset_id,
            Dataset.user_id == user_id
        ).first()

        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        db.delete(dataset)
        db.commit()

        return {"message": "Dataset deleted successfully"}