from pydantic import BaseModel
from typing import Dict, Any


class TrainModelRequest(BaseModel):
    target_column: str
    task: str  # regression or classification


class PredictRequest(BaseModel):
    input_data: Dict[str, Any]