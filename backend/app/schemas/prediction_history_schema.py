from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any, Optional


class PredictionHistoryResponse(BaseModel):
    id: str
    user_id: str
    dataset_id: str
    model_name: str
    input_data: Dict[str, Any]
    prediction_result: Dict[str, Any]
    confidence: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True