from app.services.prediction_service import PredictionService


class PredictionAnswerService:

    @staticmethod
    def answer(dataset_id: str, user_id: str, question: str):
        """
        This is a placeholder prediction router.
        Later we will parse question into structured payload.
        """

        # Simple example: call sales prediction with dummy payload
        payload = type("obj", (object,), {"month": "next_month", "marketing_spend": None})

        result = PredictionService.predict_sales(dataset_id, user_id, payload)

        return {
            "answer": f"Predicted Sales: {result['prediction']} (confidence: {result.get('confidence', 0)})",
            "confidence": result.get("confidence", 0.0),
            "sources": [],
            "query_type": "PREDICTION"
        }