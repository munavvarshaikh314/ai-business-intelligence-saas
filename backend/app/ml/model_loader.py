import os
import joblib

MODEL_DIR = "app/storage/models"


class ModelLoader:

    @staticmethod
    def load_model(model_name: str):
        model_path = os.path.join(MODEL_DIR, model_name)

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found: {model_path}")

        return joblib.load(model_path)