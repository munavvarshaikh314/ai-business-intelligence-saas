import pandas as pd
from fastapi import HTTPException
from app.services.ml_model_service import MLModelService
from app.ml.predictor import Predictor
from app.services.logging_service import LoggingService


class MLPredictionService:

    @staticmethod
    def predict(user_id: str, dataset_id: str, input_data: dict):
        """
        Run prediction using trained model.
        input_data: feature dict extracted from user question or sent directly.
        """
        model = MLModelService.get_latest_model(user_id, dataset_id)

        if not input_data:
            raise HTTPException(
                status_code=400,
                detail="No input features provided for prediction."
            )

        try:
            result = Predictor.predict(model.model_name, input_data)
        except FileNotFoundError:
            raise HTTPException(
                status_code=404,
                detail="Trained model file not found. Please retrain the model."
            )
        except Exception as e:
            LoggingService.error(f"Prediction failed: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Prediction failed: {str(e)}"
            )

        return {
            "model_name": model.model_name,
            "model_type": model.model_type,
            "target_column": model.target_column,
            "prediction": result["prediction"],
            "confidence": result.get("confidence"),
        }


# from fastapi import HTTPException
# from app.services.ml_model_service import MLModelService
# from app.ml.predictor import Predictor


# class MLPredictionService:

#     @staticmethod
#     def predict(user_id: str, dataset_id: str, input_data: dict):
#         model = MLModelService.get_latest_model(user_id, dataset_id)

#         result = Predictor.predict(model.model_name, input_data)

#         return {
#             "model_name": model.model_name,
#             "model_type": model.model_type,
#             "target_column": model.target_column,
#             "prediction": result["prediction"],
#             "confidence": result["confidence"]
#         }