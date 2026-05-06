from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.schemas.ql_schema import SQLGenerateRequest
from app.services.sql_agent_service import SQLAgentService

router = APIRouter()


@router.post("/generate/{dataset_id}")
def generate_sql(dataset_id: str, payload: SQLGenerateRequest, current_user=Depends(get_current_user)):
    return SQLAgentService.generate_sql(dataset_id, current_user.id, payload.question)


@router.post("/execute/{dataset_id}")
def execute_sql(dataset_id: str, payload: dict, current_user=Depends(get_current_user)):
    sql = payload.get("sql")
    return SQLAgentService.execute_sql(dataset_id, current_user.id, sql)
