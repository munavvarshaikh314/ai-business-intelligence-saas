from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.schemas.chat_schema import CreateSessionRequest, AskRequest
from app.services.chat_service import ChatService

router = APIRouter()

@router.post("/session/{dataset_id}")
def create_session(dataset_id: str, payload: CreateSessionRequest, current_user=Depends(get_current_user)):
    return ChatService.create_session(dataset_id, current_user.id, payload.session_name)

@router.get("/sessions/{dataset_id}")
def get_sessions(dataset_id: str, current_user=Depends(get_current_user)):
    return ChatService.get_sessions(dataset_id, current_user.id)

@router.get("/messages/{session_id}")
def get_messages(session_id: str, current_user=Depends(get_current_user)):
    return ChatService.get_messages(session_id, current_user.id)

@router.post("/ask/{dataset_id}")
def ask_question(dataset_id: str, payload: AskRequest, current_user=Depends(get_current_user)):
    return ChatService.ask(dataset_id, current_user.id, payload.session_id, payload.question)

@router.delete("/session/{session_id}")
def delete_session(session_id: str, current_user=Depends(get_current_user)):
    return ChatService.delete_session(session_id, current_user.id)