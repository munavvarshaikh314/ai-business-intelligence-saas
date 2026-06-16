from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.dataset_model import Dataset


class PredictionService:

    @staticmethod
    def predict_sales(dataset_id: str, user_id: str, payload):
        db: Session = SessionLocal()

        dataset = db.query(Dataset).filter(
            Dataset.id == dataset_id,
            Dataset.user_id == user_id
        ).first()

        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        # TODO: Load ML model from storage/models/
        # TODO: Feature engineering
        # TODO: Predict

        return {
            "prediction": 0,
            "confidence": 0.0
        }

    @staticmethod
    def predict_churn(dataset_id: str, user_id: str, payload):
        # TODO: churn prediction
        return {"churn_probability": 0.0}

    @staticmethod
    def get_history(dataset_id: str, user_id: str):
        # TODO: fetch from predictions table
        return []