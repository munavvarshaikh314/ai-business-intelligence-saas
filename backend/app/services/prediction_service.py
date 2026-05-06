from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.dataset_model import Dataset
from app.models.prediction_model import Prediction


class PredictionService:
    @staticmethod
    def _ensure_dataset(dataset_id: str, user_id: str):
        db: Session = SessionLocal()
        try:
            dataset = db.query(Dataset).filter(
                Dataset.id == dataset_id,
                Dataset.user_id == user_id
            ).first()

            if not dataset:
                raise HTTPException(status_code=404, detail="Dataset not found")

            return dataset
        finally:
            db.close()

    @staticmethod
    def _save_prediction(user_id: str, dataset_id: str, model_name: str, input_data: dict, result: dict):
        db: Session = SessionLocal()
        try:
            prediction = Prediction(
                user_id=user_id,
                dataset_id=dataset_id,
                model_name=model_name,
                input_data=input_data,
                prediction_result=result,
                confidence=result.get("confidence"),
            )
            db.add(prediction)
            db.commit()
            db.refresh(prediction)
            return prediction
        finally:
            db.close()

    @staticmethod
    def predict_sales(dataset_id: str, user_id: str, payload):
        PredictionService._ensure_dataset(dataset_id, user_id)

        marketing_spend = payload.marketing_spend or 0
        base_prediction = 10000.0
        spend_lift = float(marketing_spend) * 1.2
        month_lift = 1.08 if "next" in payload.month.lower() else 1.0

        result = {
            "prediction": round((base_prediction + spend_lift) * month_lift, 2),
            "confidence": 0.72,
            "model_name": "baseline_sales_forecast",
        }

        PredictionService._save_prediction(
            user_id=user_id,
            dataset_id=dataset_id,
            model_name=result["model_name"],
            input_data=payload.model_dump(),
            result=result,
        )
        return result

    @staticmethod
    def predict_churn(dataset_id: str, user_id: str, payload):
        PredictionService._ensure_dataset(dataset_id, user_id)

        contract_risk = {
            "month-to-month": 0.32,
            "monthly": 0.32,
            "one year": 0.16,
            "two year": 0.08,
        }.get(payload.contract_type.lower(), 0.2)
        tenure_discount = min(max(payload.tenure, 0), 72) / 72 * 0.18
        charge_risk = min(payload.monthly_charges / 250, 1) * 0.3
        churn_probability = max(0.02, min(0.95, contract_risk + charge_risk - tenure_discount))

        result = {
            "churn_probability": round(churn_probability, 4),
            "confidence": 0.68,
            "model_name": "baseline_churn_estimator",
        }

        PredictionService._save_prediction(
            user_id=user_id,
            dataset_id=dataset_id,
            model_name=result["model_name"],
            input_data=payload.model_dump(),
            result=result,
        )
        return result

    @staticmethod
    def get_history(dataset_id: str, user_id: str):
        PredictionService._ensure_dataset(dataset_id, user_id)
        db: Session = SessionLocal()
        try:
            rows = db.query(Prediction).filter(
                Prediction.dataset_id == dataset_id,
                Prediction.user_id == user_id
            ).order_by(Prediction.created_at.desc()).limit(50).all()

            return [
                {
                    "id": str(row.id),
                    "model_name": row.model_name,
                    "input_data": row.input_data,
                    "prediction_result": row.prediction_result,
                    "confidence": row.confidence,
                    "created_at": row.created_at,
                }
                for row in rows
            ]
        finally:
            db.close()
