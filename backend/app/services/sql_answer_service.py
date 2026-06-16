import json
from app.services.sql_agent_service import SQLAgentService
from app.services.llm import LLMService  # ← fixed import
from app.services.logging_service import LoggingService


def generate_chart_title(question):
    q = question.lower()

    if "above average" in q:
        return "Top Products Above Average Sales"

    if "category average" in q:
        return "Product Sales vs Category Average"

    if "region" in q:
        return "Sales by Region"

    if "profit" in q:
        return "Profit Analysis"

    return "Business Analysis"

class SQLAnswerService:

    @staticmethod
    def answer(dataset_id: str, user_id: str, question: str):
        generated = SQLAgentService.generate_sql(dataset_id, user_id, question)
        sql = generated["sql"]
        executed = SQLAgentService.execute_sql(dataset_id, user_id, sql)
        columns = executed["columns"]
        rows = executed["rows"]  # rows are dicts after sql_agent_service fix
        
        kpis = {}

        if rows:
            kpis["total_results"] = len(rows)

            first_row = rows[0]

            if "product_id" in first_row:
             kpis["top_product"] = first_row["product_id"]

            if "total_sales" in first_row:
             kpis["top_sales"] = first_row["total_sales"]

        if not rows:
            return {
                "answer": (
            "No matching records were found for this query. "
            "The query executed successfully, but the dataset "
            "does not contain any rows that satisfy the requested conditions."
        ),
        "insight": (
            "No matching records were found in the current dataset."
        ),
                # "answer": "The query ran successfully but returned no matching results.",
                "confidence": 0.75,
                "confidence_label": "medium",
                "guardrail": "no_results",
                "query_type": "SQL",
                "sources": [{"sql": sql}],
                "data": executed,
            }

        try:
            # rows are dicts — serialize safely
            sample_rows = rows[:5]
            format_prompt = f"""You are a senior business analyst..
Summarize these SQL query results in 2-3 clear, specific sentences.
 Focus on trends, top performers, anomalies, comparisons
Use exact numbers from the data. Do not guess or add external knowledge.
"Always use ₹ symbol for all monetary values. Never use $."

Question: {question}
SQL: {sql}
Columns: {columns}
Results (first 5 rows): {json.dumps(sample_rows, default=str)}
Total rows: {len(rows)}"""

            # answer = LLMService.generate_text(format_prompt)
            # confidence = 0.92
            # confidence_label = "high"
            # guardrail = None
            
            insight = LLMService.generate_text(format_prompt)
            
            

            answer = insight
            chart_title = generate_chart_title(question)

            confidence = 0.92
            confidence_label = "high"
            guardrail = None


        except Exception as e:
            LoggingService.warning(f"SQL formatting failed: {e}")
            # rows[0] is already a dict — no need for zip
            top = rows[0] if rows else {}
            insight = f"Query returned {len(rows)} results."
            # answer = f"Query returned {len(rows)} result(s). Top result: {top}"
            answer = insight
            confidence = 0.80
            confidence_label = "high"
            guardrail = None

        return {
            "answer": answer,
            "insight": insight,
            "chart_title": chart_title,
            "confidence": confidence,
            "confidence_label": confidence_label,
            "guardrail": guardrail,
            "total_rows": len(rows),
            "kpis": kpis,
            "query_type": "SQL",
            "sources": [{"sql": sql}],
            "data": executed,
        }

# import json
# from app.services.sql_agent_service import SQLAgentService
# from app.services.llm import LLMService
# from app.services.logging_service import LoggingService


# class SQLAnswerService:

#     @staticmethod
#     def answer(dataset_id: str, user_id: str, question: str):
#         generated = SQLAgentService.generate_sql(dataset_id, user_id, question)
#         sql = generated["sql"]
#         executed = SQLAgentService.execute_sql(dataset_id, user_id, sql)
#         columns = executed["columns"]
#         rows = executed["rows"]

#         if not rows:
#             return {
#                 "answer": "The query ran successfully but returned no matching results. Your data may not contain records for this query.",
#                 "confidence": 0.75,
#                 "confidence_label": "medium",
#                 "guardrail": "no_results",
#                 "query_type": "SQL",
#                 "sources": [{"sql": sql}],
#                 "data": executed,
#             }

#         # Use Gemini to produce a natural language summary
#         try:
#             format_prompt = f"""
# You are a business data analyst.
# Summarize these SQL query results in 2-3 clear, specific sentences.
# Use exact numbers from the data. Do not guess or add external knowledge.

# Question: {question}
# SQL executed: {sql}
# Columns: {columns}
# Results (first 5 rows): {json.dumps(rows[:5], default=str)}
# Total rows returned: {len(rows)}
# """
#             answer = LLMService.generate_text(format_prompt)
#             confidence = 0.92
#             confidence_label = "high"
#             guardrail = None

#         except Exception as e:
#             LoggingService.warning(f"SQL natural language formatting failed: {e}")
#             top = dict(zip(columns, rows[0])) if rows else {}
#             answer = f"Query returned {len(rows)} result(s). Top result: {top}"
#             confidence = 0.80
#             confidence_label = "high"
#             guardrail = None

#         return {
#             "answer": answer,
#             "confidence": confidence,
#             "confidence_label": confidence_label,
#             "guardrail": guardrail,
#             "query_type": "SQL",
#             "sources": [{"sql": sql}],
#             "data": executed,
#         }



# from app.services.sql_agent_service import SQLAgentService


# class SQLAnswerService:

#     @staticmethod
#     def answer(dataset_id: str, user_id: str, question: str):
#         generated = SQLAgentService.generate_sql(dataset_id, user_id, question)
#         sql = generated["sql"]

#         executed = SQLAgentService.execute_sql(dataset_id, user_id, sql)

#         # Convert SQL result into readable text
#         columns = executed["columns"]
#         rows = executed["rows"]

#         if not rows:
#             return {
#                 "answer": "Query executed successfully but returned no results.",
#                 "confidence": 0.9,
#                 "query_type": "SQL",
#                 "sources": [{"sql": sql}],
#                 "data": executed
#             }

#         # Basic text summary for chatbot answer
#         answer = f"Here are the results:\nColumns: {columns}\nTop Row: {rows[0]}"

#         return {
#             "answer": answer,
#             "confidence": 0.9,
#             "query_type": "SQL",
#             "sources": [{"sql": sql}],
#             "data": executed
#         }