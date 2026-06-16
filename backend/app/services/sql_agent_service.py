from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import SessionLocal
from app.models.dataset_model import Dataset
from app.models.dataset_column_model import DatasetColumn
from app.utils.sql_utils import is_safe_select_query
from app.services.llm import LLMService  # ← FIXED import
from app.services.sql_prompt_templates import build_sql_prompt
from app.security.sql_guard import SQLGuard
from app.services.logging_service import LoggingService


class SQLAgentService:

    @staticmethod
    def get_dataset_table(dataset_id: str, user_id: str):
        db: Session = SessionLocal()
        try:
            dataset = db.query(Dataset).filter(
                Dataset.id == dataset_id,
                Dataset.user_id == user_id
            ).first()

            if not dataset:
                raise HTTPException(status_code=404, detail="Dataset not found")

            if not dataset.table_name:
                raise HTTPException(
                    status_code=400,
                    detail="Dataset table not created yet. Please upload a CSV file first."
                )

            return dataset.table_name
        finally:
            db.close()

    @staticmethod
    def get_schema_text(dataset_id: str):
        db: Session = SessionLocal()
        try:
            cols = db.query(DatasetColumn).filter(
                DatasetColumn.dataset_id == dataset_id
            ).all()

            if not cols:
                raise HTTPException(
                    status_code=400,
                    detail="Dataset schema not found. Please re-upload your CSV."
                )

            return "\n".join(
                f"- {col.column_name} ({col.data_type})"
                for col in cols
            )
        finally:
            db.close()

    @staticmethod
    def generate_sql(dataset_id: str, user_id: str, question: str):
        table_name = SQLAgentService.get_dataset_table(dataset_id, user_id)
        schema_text = SQLAgentService.get_schema_text(dataset_id)

        prompt = build_sql_prompt(table_name, schema_text, question)
        sql = LLMService.generate_sql(prompt)
        sql = sql.replace("```sql", "").replace("```", "").strip()

        if not sql:
            raise HTTPException(
                status_code=400,
                detail="Could not generate SQL for this question. Please try rephrasing."
            )

        if not is_safe_select_query(sql):
            raise HTTPException(status_code=400, detail="Generated SQL contains unsafe operations.")

        if table_name not in sql:
            raise HTTPException(
                status_code=400,
                detail=f"Generated SQL must reference table: {table_name}"
            )

        LoggingService.info(f"Generated SQL: {sql[:200]}")
        return {"sql": sql}

    @staticmethod
    def execute_sql(dataset_id: str, user_id: str, sql: str):
        table_name = SQLAgentService.get_dataset_table(dataset_id, user_id)
        sql = sql.rstrip(";").strip()
        sql = sql.rstrip(";").strip()
        SQLGuard.validate(sql)

        if not is_safe_select_query(sql):
            raise HTTPException(status_code=400, detail="Only SELECT queries are allowed.")

        if table_name not in sql:
            raise HTTPException(
                status_code=400,
                detail=f"Query must use dataset table: {table_name}"
            )

        db: Session = SessionLocal()
        try:
            result = db.execute(text(sql))
            rows = result.fetchall()
            columns = list(result.keys())

            # ← FIXED: return dicts not lists — SQLTableViewer needs dicts
            dict_rows = [dict(zip(columns, row)) for row in rows]

            return {
                "columns": columns,
                "rows": dict_rows,
                "row_count": len(dict_rows),
            }

        except Exception as e:
            error_msg = str(e)
            LoggingService.error(f"SQL execution failed: {error_msg}")
            
            try:
                db.rollback()
            except Exception:
               pass

            # Self-correction — ask Gemini to fix the SQL
            try:
                fix_prompt = f"""The following PostgreSQL query failed with this error:

Error: {error_msg}

Failed SQL:
{sql}

Fix the SQL query. Return ONLY the corrected SQL, no explanation."""

                fixed_sql = LLMService.generate_sql(fix_prompt)
                fixed_sql = fixed_sql.replace("```sql", "").replace("```", "").strip()

                if fixed_sql and is_safe_select_query(fixed_sql) and table_name in fixed_sql:
                    LoggingService.info(f"Self-corrected SQL: {fixed_sql[:200]}")
                    result2 = db.execute(text(fixed_sql))
                    rows2 = result2.fetchall()
                    columns2 = list(result2.keys())
                    dict_rows2 = [dict(zip(columns2, row)) for row in rows2]
                    return {
                        "columns": columns2,
                        "rows": dict_rows2,
                        "row_count": len(dict_rows2),
                    }
            except Exception as fix_error:
                LoggingService.warning(f"Self-correction also failed: {fix_error}")

            raise HTTPException(
                status_code=400,
                detail=f"Could not execute this query. Please try rephrasing your question."
            )
        finally:
            db.close()


# from fastapi import HTTPException
# from sqlalchemy.orm import Session
# from sqlalchemy import text

# from app.database import SessionLocal
# from app.models.dataset_model import Dataset
# from app.models.dataset_column_model import DatasetColumn
# from app.utils.sql_utils import is_safe_select_query
# #from app.services.llm_service import LLMService
# from app.services.llm import LLMService
# from app.services.sql_prompt_templates import build_sql_prompt
# from app.security.sql_guard import SQLGuard


# class SQLAgentService:

#     @staticmethod
#     def get_dataset_table(dataset_id: str, user_id: str):
#         db: Session = SessionLocal()

#         dataset = db.query(Dataset).filter(
#             Dataset.id == dataset_id,
#             Dataset.user_id == user_id
#         ).first()

#         if not dataset:
#             raise HTTPException(status_code=404, detail="Dataset not found")

#         if not dataset.table_name:
#             raise HTTPException(status_code=400, detail="Dataset table not created yet. Upload CSV first.")

#         return dataset.table_name

#     @staticmethod
#     def get_schema_text(dataset_id: str):
#         db: Session = SessionLocal()

#         cols = db.query(DatasetColumn).filter(
#             DatasetColumn.dataset_id == dataset_id
#         ).all()

#         if not cols:
#             raise HTTPException(status_code=400, detail="Dataset schema not found")

#         schema_lines = []
#         for col in cols:
#             schema_lines.append(f"- {col.column_name} ({col.data_type})")

#         return "\n".join(schema_lines)

#     @staticmethod
#     def generate_sql(dataset_id: str, user_id: str, question: str):
#         table_name = SQLAgentService.get_dataset_table(dataset_id, user_id)
#         schema_text = SQLAgentService.get_schema_text(dataset_id)
        

#         prompt = build_sql_prompt(table_name, schema_text, question)

#         sql = LLMService.generate_sql(prompt)

#         # Remove accidental ```sql blocks
#         sql = sql.replace("```sql", "").replace("```", "").strip()

#         if not is_safe_select_query(sql):
#             raise HTTPException(status_code=400, detail="Generated SQL is unsafe")

#         # Ensure correct table is used
#         if table_name not in sql:
#             raise HTTPException(status_code=400, detail=f"Generated SQL must use table: {table_name}")

#         return {"sql": sql}

#     @staticmethod
#     def execute_sql(dataset_id: str, user_id: str, sql: str):
#         table_name = SQLAgentService.get_dataset_table(dataset_id, user_id)
#         sql = sql.rstrip(";").strip()
        sql = sql.rstrip(";").strip()
        SQLGuard.validate(sql)

#         if not is_safe_select_query(sql):
#             raise HTTPException(status_code=400, detail="Only safe SELECT queries are allowed")

#         if table_name not in sql:
#             raise HTTPException(status_code=400, detail=f"Query must use dataset table: {table_name}")

#         db: Session = SessionLocal()

#         try:
#             result = db.execute(text(sql))
#             rows = result.fetchall()
#             columns = list(result.keys())

#             return {
#                 "columns": columns,
#                 "rows": [list(r) for r in rows]
#             }

#         except Exception as e:
#             raise HTTPException(status_code=400, detail=f"SQL execution failed: {str(e)}")

