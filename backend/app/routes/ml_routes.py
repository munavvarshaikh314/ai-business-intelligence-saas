from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.schemas.ml_schema import TrainModelRequest, PredictRequest
from app.services.ml_model_service import MLModelService
from app.services.ml_prediction_service import MLPredictionService

router = APIRouter()


@router.post("/train/{dataset_id}")
def train_model(dataset_id: str, payload: TrainModelRequest, current_user=Depends(get_current_user)):
    """Manually train ML model on uploaded CSV with specified target column."""
    return MLModelService.train_model(
        user_id=current_user.id,
        dataset_id=dataset_id,
        target_col=payload.target_column,
        task=payload.task
    )


@router.post("/predict/{dataset_id}")
def predict(dataset_id: str, payload: PredictRequest, current_user=Depends(get_current_user)):
    """Run prediction using trained model with structured input."""
    return MLPredictionService.predict(
        user_id=current_user.id,
        dataset_id=dataset_id,
        input_data=payload.input_data
    )


@router.get("/model-info/{dataset_id}")
def get_model_info(dataset_id: str, current_user=Depends(get_current_user)):
    """Get info about the trained model for this dataset."""
    return MLModelService.get_model_info(
        user_id=current_user.id,
        dataset_id=dataset_id
    )


# from fastapi import APIRouter, Depends
# from app.dependencies import get_current_user
# from app.schemas.ml_schema import TrainModelRequest, PredictRequest
# from app.services.ml_model_service import MLModelService
# from app.services.ml_prediction_service import MLPredictionService

# router = APIRouter()


# @router.post("/train/{dataset_id}")
# def train_model(dataset_id: str, payload: TrainModelRequest, current_user=Depends(get_current_user)):
#     return MLModelService.train_model(
#         user_id=current_user.id,
#         dataset_id=dataset_id,
#         target_col=payload.target_column,
#         task=payload.task
#     )


# @router.post("/predict/{dataset_id}")
# def predict(dataset_id: str, payload: PredictRequest, current_user=Depends(get_current_user)):
#     return MLPredictionService.predict(
#         user_id=current_user.id,
#         dataset_id=dataset_id,
#         input_data=payload.input_data
#     )