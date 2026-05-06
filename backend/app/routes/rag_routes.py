from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.schemas.rag_schema import RetrieveRequest
from app.services.rag_service import RAGService

router = APIRouter()

@router.post("/retrieve/{dataset_id}")
def retrieve_chunks(dataset_id: str, payload: RetrieveRequest, current_user=Depends(get_current_user)):
    return RAGService.retrieve(dataset_id, current_user.id, payload.query, payload.top_k)

@router.post("/build-index/{dataset_id}")
def build_index(dataset_id: str, current_user=Depends(get_current_user)):
    return RAGService.build_index(dataset_id, current_user.id)

@router.get("/chunks/{dataset_id}")
def get_chunks(dataset_id: str, current_user=Depends(get_current_user)):
    return RAGService.get_chunks(dataset_id, current_user.id)