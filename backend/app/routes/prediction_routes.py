from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.schemas.prediction_schema import SalesPredictionRequest, ChurnPredictionRequest
from app.services.prediction_service import PredictionService

router = APIRouter()

@router.post("/sales/{dataset_id}")
def predict_sales(dataset_id: str, payload: SalesPredictionRequest, current_user=Depends(get_current_user)):
    return PredictionService.predict_sales(dataset_id, current_user.id, payload)

@router.post("/churn/{dataset_id}")
def predict_churn(dataset_id: str, payload: ChurnPredictionRequest, current_user=Depends(get_current_user)):
    return PredictionService.predict_churn(dataset_id, current_user.id, payload)

@router.get("/history/{dataset_id}")
def prediction_history(dataset_id: str, current_user=Depends(get_current_user)):
    return PredictionService.get_history(dataset_id, current_user.id)