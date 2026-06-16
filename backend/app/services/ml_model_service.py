import json
import os
import pandas as pd
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.database import SessionLocal
from app.models.ml_model_registry import MLModelRegistry
from app.models.file_model import File
from app.ml.train_sales_model import train_sales_model
from app.ml.train_churn_model import train_churn_model
from app.ml.feature_engineering import auto_detect_target_column, detect_target_type
from app.services.logging_service import LoggingService


class MLModelService:

    @staticmethod
    def train_model(user_id: str, dataset_id: str, target_col: str, task: str):
        """Manual training — user specifies target column and task."""
        db: Session = SessionLocal()
        try:
            csv_file = db.query(File).filter(
                File.dataset_id == dataset_id,
                File.user_id == user_id,
                File.file_type == "csv"
            ).order_by(File.created_at.desc()).first()

            if not csv_file:
                raise HTTPException(status_code=404, detail="No CSV file found for this dataset. Upload a CSV first.")

            if not os.path.exists(csv_file.file_path):
                raise HTTPException(status_code=404, detail="CSV file not found on disk.")

            return MLModelService._run_training(
                db, user_id, dataset_id, csv_file.file_path, target_col, task
            )
        finally:
            db.close()

    @staticmethod
    def auto_train(user_id: str, dataset_id: str, file_path: str):
        """
        Auto-training triggered after CSV upload.
        Detects target column and task type automatically.
        Non-blocking — errors are logged, not raised.
        """
        db: Session = SessionLocal()
        try:
            df = pd.read_csv(file_path)

            if df.empty or len(df) < 5:
                LoggingService.info(f"Auto-train skipped — too few rows: dataset={dataset_id}")
                return

            target_col, task = auto_detect_target_column(df)
            LoggingService.info(f"Auto-train detected: target={target_col} task={task} dataset={dataset_id}")

            MLModelService._run_training(db, user_id, dataset_id, file_path, target_col, task)
            LoggingService.info(f"Auto-train complete: dataset={dataset_id}")

        except Exception as e:
            # Never crash the upload — just log
            LoggingService.warning(f"Auto-train failed (non-critical): dataset={dataset_id} error={str(e)}")
        finally:
            db.close()

    @staticmethod
    def _run_training(db: Session, user_id: str, dataset_id: str, file_path: str, target_col: str, task: str):
        """Core training logic used by both manual and auto training."""
        model_name = f"{dataset_id}_{task}_model.pkl"

        if task == "regression":
            result = train_sales_model(file_path, target_col, model_name=model_name)
            model_type = "regression"
        elif task == "classification":
            result = train_churn_model(file_path, target_col, model_name=model_name)
            model_type = "classification"
        else:
            raise HTTPException(status_code=400, detail=f"Invalid task type '{task}'. Use 'regression' or 'classification'.")

        # Remove old model record if exists
        db.query(MLModelRegistry).filter(
            MLModelRegistry.dataset_id == dataset_id,
            MLModelRegistry.user_id == user_id
        ).delete()

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
            "target_column": target_col,
            "metrics": result["metrics"]
        }

    @staticmethod
    def get_latest_model(user_id: str, dataset_id: str):
        db: Session = SessionLocal()
        try:
            model = db.query(MLModelRegistry).filter(
                MLModelRegistry.user_id == user_id,
                MLModelRegistry.dataset_id == dataset_id
            ).order_by(MLModelRegistry.created_at.desc()).first()

            if not model:
                raise HTTPException(
                    status_code=404,
                    detail="No ML model trained for this dataset. Upload a CSV and wait for auto-training, or train manually via /api/v1/ml/train."
                )
            return model
        finally:
            db.close()

    @staticmethod
    def get_model_info(user_id: str, dataset_id: str):
        model = MLModelService.get_latest_model(user_id, dataset_id)
        metrics = {}
        try:
            metrics = json.loads(model.metrics_json) if model.metrics_json else {}
        except Exception:
            pass
        return {
            "model_id": str(model.id),
            "model_name": model.model_name,
            "model_type": model.model_type,
            "target_column": model.target_column,
            "metrics": metrics,
            "trained_at": model.created_at.isoformat() if model.created_at else None,
        }



# import json
# from sqlalchemy.orm import Session
# from fastapi import HTTPException

# from app.database import SessionLocal
# from app.models.ml_model_registry import MLModelRegistry
# from app.models.file_model import File
# from app.ml.train_sales_model import train_sales_model
# from app.ml.train_churn_model import train_churn_model


# class MLModelService:

#     @staticmethod
#     def train_model(user_id: str, dataset_id: str, target_col: str, task: str):
#         """
#         task = regression | classification
#         """
#         db: Session = SessionLocal()

#         # Find latest CSV file uploaded for dataset
#         csv_file = db.query(File).filter(
#             File.dataset_id == dataset_id,
#             File.user_id == user_id,
#             File.file_type == "csv"
#         ).order_by(File.created_at.desc()).first()

#         if not csv_file:
#             raise HTTPException(status_code=404, detail="No CSV file found for this dataset")

#         model_name = f"{dataset_id}_{task}_model.pkl"

#         if task == "regression":
#             result = train_sales_model(csv_file.file_path, target_col, model_name=model_name)
#             model_type = "regression"

#         elif task == "classification":
#             result = train_churn_model(csv_file.file_path, target_col, model_name=model_name)
#             model_type = "classification"

#         else:
#             raise HTTPException(status_code=400, detail="Invalid task type")

#         # Save model record
#         model_record = MLModelRegistry(
#             user_id=user_id,
#             dataset_id=dataset_id,
#             model_name=model_name,
#             model_type=model_type,
#             target_column=target_col,
#             metrics_json=json.dumps(result["metrics"])
#         )

#         db.add(model_record)
#         db.commit()
#         db.refresh(model_record)

#         return {
#             "message": "Model trained successfully",
#             "model_id": str(model_record.id),
#             "model_name": model_record.model_name,
#             "model_type": model_record.model_type,
#             "metrics": result["metrics"]
#         }

#     @staticmethod
#     def get_latest_model(user_id: str, dataset_id: str):
#         db: Session = SessionLocal()

#         model = db.query(MLModelRegistry).filter(
#             MLModelRegistry.user_id == user_id,
#             MLModelRegistry.dataset_id == dataset_id
#         ).order_by(MLModelRegistry.created_at.desc()).first()

#         if not model:
#             raise HTTPException(status_code=404, detail="No ML model trained for this dataset")

#         return model