from fastapi import APIRouter, Depends
from app.schemas.dataset_schema import DatasetCreateRequest, DatasetResponse
from app.dependencies import get_current_user
from app.services.dataset_service import DatasetService

router = APIRouter()

@router.post("/create", response_model=DatasetResponse)
def create_dataset(payload: DatasetCreateRequest, current_user=Depends(get_current_user)):
    return DatasetService.create_dataset(payload, current_user.id)

@router.get("/status/{dataset_id}")
def get_dataset_status(dataset_id: str, current_user=Depends(get_current_user)):
    dataset = DatasetService.get_dataset(dataset_id, current_user.id)

    return {
        "dataset_id": str(dataset.id),
        "index_status": dataset.index_status,
        "index_progress": dataset.index_progress
    }

@router.get("/", response_model=list[DatasetResponse])
def get_user_datasets(current_user=Depends(get_current_user)):
    return DatasetService.get_datasets(current_user.id)

@router.get("/{dataset_id}", response_model=DatasetResponse)
def get_dataset(dataset_id: str, current_user=Depends(get_current_user)):
    return DatasetService.get_dataset(dataset_id, current_user.id)

@router.delete("/{dataset_id}")
def delete_dataset(dataset_id: str, current_user=Depends(get_current_user)):
    return DatasetService.delete_dataset(dataset_id, current_user.id)