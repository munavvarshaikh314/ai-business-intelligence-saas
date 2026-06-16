import os
import json
import pandas as pd
from app.ml.model_loader import ModelLoader

MODEL_DIR = "app/storage/models"


class Predictor:

    @staticmethod
    def load_feature_meta(model_name: str) -> dict:
        """Load saved feature columns and defaults for this model."""
        meta_path = os.path.join(MODEL_DIR, model_name.replace(".pkl", "_meta.json"))
        if os.path.exists(meta_path):
            with open(meta_path, "r") as f:
                return json.load(f)
        return {}

    @staticmethod
    def predict(model_name: str, input_data: dict):
        """
        Predict using trained model.
        If input_data is missing columns, fills with defaults from training data.
        This means "predict my sale" with no features still works — uses median values.
        """
        model = ModelLoader.load_model(model_name)
        meta = Predictor.load_feature_meta(model_name)

        feature_columns = meta.get("feature_columns", [])
        defaults = meta.get("defaults", {})

        if feature_columns:
            # Build row using provided values, fill missing with defaults
            row = {}
            for col in feature_columns:
                if col in input_data:
                    row[col] = input_data[col]
                elif col in defaults:
                    row[col] = defaults[col]
                else:
                    row[col] = 0  # Last resort fallback

            df = pd.DataFrame([row])
        else:
            # No meta saved — use input_data as-is (old behavior)
            df = pd.DataFrame([input_data]) if input_data else pd.DataFrame([{}])

        prediction = model.predict(df)[0]

        # Confidence for classification
        proba = None
        if hasattr(model, "predict_proba"):
            try:
                probs = model.predict_proba(df)[0]
                proba = float(max(probs))
            except Exception:
                pass

        used_defaults = [col for col in feature_columns
                        if col not in input_data and col in defaults]

        return {
            "prediction": float(prediction) if isinstance(prediction, (int, float)) else str(prediction),
            "confidence": proba,
            "used_defaults": used_defaults,  # tells frontend which values were assumed
        }


# import pandas as pd
# from app.ml.model_loader import ModelLoader


# class Predictor:

#     @staticmethod
#     def predict(model_name: str, input_data: dict):
#         """
#         input_data: {"feature1": value1, "feature2": value2}
#         """
#         model = ModelLoader.load_model(model_name)

#         df = pd.DataFrame([input_data])
#         prediction = model.predict(df)[0]

#         # Probability support for classification
#         proba = None
#         if hasattr(model, "predict_proba"):
#             probs = model.predict_proba(df)[0]
#             proba = float(max(probs))

#         return {
#             "prediction": float(prediction) if isinstance(prediction, (int, float)) else int(prediction),
#             "confidence": proba
#         }