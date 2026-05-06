from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import SessionLocal
from app.models.dataset_model import Dataset
from app.models.dataset_column_model import DatasetColumn
from app.utils.sql_utils import is_safe_select_query
from app.services.llm_service import LLMService
from app.services.sql_prompt_templates import build_sql_prompt


class SQLAgentService:

    @staticmethod
    def get_dataset_table(dataset_id: str, user_id: str):
        db: Session = SessionLocal()

        dataset = db.query(Dataset).filter(
            Dataset.id == dataset_id,
            Dataset.user_id == user_id
        ).first()

        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        if not dataset.table_name:
            raise HTTPException(status_code=400, detail="Dataset table not created yet. Upload CSV first.")

        return dataset.table_name

    @staticmethod
    def get_schema_text(dataset_id: str):
        db: Session = SessionLocal()

        cols = db.query(DatasetColumn).filter(
            DatasetColumn.dataset_id == dataset_id
        ).all()

        if not cols:
            raise HTTPException(status_code=400, detail="Dataset schema not found")

        schema_lines = []
        for col in cols:
            schema_lines.append(f"- {col.column_name} ({col.data_type})")

        return "\n".join(schema_lines)

    @staticmethod
    def generate_sql(dataset_id: str, user_id: str, question: str):
        table_name = SQLAgentService.get_dataset_table(dataset_id, user_id)
        schema_text = SQLAgentService.get_schema_text(dataset_id)

        prompt = build_sql_prompt(table_name, schema_text, question)

        sql = LLMService.generate_sql(prompt)

        # Remove accidental ```sql blocks
        sql = sql.replace("```sql", "").replace("```", "").strip()

        if not is_safe_select_query(sql):
            raise HTTPException(status_code=400, detail="Generated SQL is unsafe")

        # Ensure correct table is used
        if table_name not in sql:
            raise HTTPException(status_code=400, detail=f"Generated SQL must use table: {table_name}")

        return {"sql": sql}

    @staticmethod
    def execute_sql(dataset_id: str, user_id: str, sql: str):
        table_name = SQLAgentService.get_dataset_table(dataset_id, user_id)

        if not is_safe_select_query(sql):
            raise HTTPException(status_code=400, detail="Only safe SELECT queries are allowed")

        if table_name not in sql:
            raise HTTPException(status_code=400, detail=f"Query must use dataset table: {table_name}")

        db: Session = SessionLocal()

        try:
            result = db.execute(text(sql))
            rows = result.fetchall()
            columns = list(result.keys())

            return {
                "columns": columns,
                "rows": [list(r) for r in rows]
            }

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"SQL execution failed: {str(e)}")