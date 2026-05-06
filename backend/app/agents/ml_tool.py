from app.services.ml_prediction_service import MLPredictionService


class MLTool:

    @staticmethod
    def run(user_id: str, dataset_id: str, query: str):
        """
        Convert natural language → simple feature dict (basic version)
        """
        # For now: we assume frontend sends structured input
        # Later we can upgrade to LLM-based extraction

        return {
            "note": "ML prediction requires structured input",
            "example": {
                "Region": "West",
                "Category": "Electronics",
                "Quantity": 5
            }
        }