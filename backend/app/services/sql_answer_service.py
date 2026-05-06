from app.services.sql_agent_service import SQLAgentService


class SQLAnswerService:

    @staticmethod
    def answer(dataset_id: str, user_id: str, question: str):
        generated = SQLAgentService.generate_sql(dataset_id, user_id, question)
        sql = generated["sql"]

        executed = SQLAgentService.execute_sql(dataset_id, user_id, sql)

        # Convert SQL result into readable text
        columns = executed["columns"]
        rows = executed["rows"]

        if not rows:
            return {
                "answer": "Query executed successfully but returned no results.",
                "confidence": 0.9,
                "query_type": "SQL",
                "sources": [{"sql": sql}],
                "data": executed
            }

        # Basic text summary for chatbot answer
        answer = f"Here are the results:\nColumns: {columns}\nTop Row: {rows[0]}"

        return {
            "answer": answer,
            "confidence": 0.9,
            "query_type": "SQL",
            "sources": [{"sql": sql}],
            "data": executed
        }