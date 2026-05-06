import pandas as pd
from app.ml.model_loader import ModelLoader


class Predictor:

    @staticmethod
    def predict(model_name: str, input_data: dict):
        """
        input_data: {"feature1": value1, "feature2": value2}
        """
        model = ModelLoader.load_model(model_name)

        df = pd.DataFrame([input_data])
        prediction = model.predict(df)[0]

        # Probability support for classification
        proba = None
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(df)[0]
            proba = float(max(probs))

        return {
            "prediction": float(prediction) if isinstance(prediction, (int, float)) else int(prediction),
            "confidence": proba
        }