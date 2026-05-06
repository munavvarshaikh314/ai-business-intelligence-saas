from app.services.rag_service import RAGService
from app.services.sql_agent_service import SQLAgentService
from app.services.ml_prediction_service import MLPredictionService
import json


class ToolExecutor:

    @staticmethod
    def execute(plan, user_id, dataset_id, query, ml_input=None):

        plan = json.loads(plan)

        intent = plan["intent"]

        if intent == "RAG":
            return {
                "type": "RAG",
                "result": RAGService.answer(query, dataset_id)
            }

        if intent == "SQL":
            return {
                "type": "SQL",
                "result": SQLAgentService.run_query(user_id, dataset_id, query)
            }

        if intent == "ML":
            return {
                "type": "ML",
                "result": MLPredictionService.predict(
                    user_id,
                    dataset_id,
                    ml_input or {}
                )
            }

        return {
            "type": "UNKNOWN",
            "result": "Cannot execute plan"
        }