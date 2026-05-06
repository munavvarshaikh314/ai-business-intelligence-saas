from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.services.memory_service import MemoryService

router = APIRouter()

@router.get("/{session_id}")
def get_memory(session_id: str, current_user=Depends(get_current_user)):
    summary = MemoryService.get_memory(current_user.id, session_id)
    return {"session_id": session_id, "memory": summary}