from fastapi import APIRouter
from celery.result import AsyncResult
from app.celery_app import celery

router = APIRouter()

@router.get("/status/{task_id}")
def get_task_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery)

    return {
        "task_id": task_id,
        "state": task_result.state,
        "result": task_result.result
    }