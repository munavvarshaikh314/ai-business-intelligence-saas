import json
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.database import SessionLocal
from app.models.ml_model_registry import MLModelRegistry
from app.models.file_model import File
from app.ml.train_sales_model import train_sales_model
from app.ml.train_churn_model import train_churn_model


class MLModelService:

    @staticmethod
    def train_model(user_id: str, dataset_id: str, target_col: str, task: str):
        """
        task = regression | classification
        """
        db: Session = SessionLocal()

        # Find latest CSV file uploaded for dataset
        csv_file = db.query(File).filter(
            File.dataset_id == dataset_id,
            File.user_id == user_id,
            File.file_type == "csv"
        ).order_by(File.created_at.desc()).first()

        if not csv_file:
            raise HTTPException(status_code=404, detail="No CSV file found for this dataset")

        model_name = f"{dataset_id}_{task}_model.pkl"

        if task == "regression":
            result = train_sales_model(csv_file.file_path, target_col, model_name=model_name)
            model_type = "regression"

        elif task == "classification":
            result = train_churn_model(csv_file.file_path, target_col, model_name=model_name)
            model_type = "classification"

        else:
            raise HTTPException(status_code=400, detail="Invalid task type")

        # Save model record
        model_record = MLModelRegistry(
            user_id=user_id,
            dataset_id=dataset_id,
            model_name=model_name,
            model_type=model_type,
            target_column=target_col,
            metrics_json=json.dumps(result["metrics"])
        )

        db.add(model_record)
        db.commit()
        db.refresh(model_record)

        return {
            "message": "Model trained successfully",
            "model_id": str(model_record.id),
            "model_name": model_record.model_name,
            "model_type": model_record.model_type,
            "metrics": result["metrics"]
        }

    @staticmethod
    def get_latest_model(user_id: str, dataset_id: str):
        db: Session = SessionLocal()

        model = db.query(MLModelRegistry).filter(
            MLModelRegistry.user_id == user_id,
            MLModelRegistry.dataset_id == dataset_id
        ).order_by(MLModelRegistry.created_at.desc()).first()

        if not model:
            raise HTTPException(status_code=404, detail="No ML model trained for this dataset")

        return model