from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class ModelRegistryResponse(BaseModel):
    id: str
    dataset_id: str
    model_name: str
    model_type: str
    model_path: str
    metrics: Optional[Dict[str, Any]] = None
    trained_at: datetime

    class Config:
        from_attributes = True