from fastapi import HTTPException
from app.services.ml_model_service import MLModelService
from app.ml.predictor import Predictor


class MLPredictionService:

    @staticmethod
    def predict(user_id: str, dataset_id: str, input_data: dict):
        model = MLModelService.get_latest_model(user_id, dataset_id)

        result = Predictor.predict(model.model_name, input_data)

        return {
            "model_name": model.model_name,
            "model_type": model.model_type,
            "target_column": model.target_column,
            "prediction": result["prediction"],
            "confidence": result["confidence"]
        }