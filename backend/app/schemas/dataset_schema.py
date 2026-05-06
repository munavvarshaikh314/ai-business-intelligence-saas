from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID


class DatasetCreateRequest(BaseModel):
    dataset_name: str
    dataset_type: str  # CSV / PDF / EXCEL
    description: Optional[str] = None


class DatasetResponse(BaseModel):
    id: UUID
    user_id: UUID
    dataset_name: str
    dataset_type: str
    description: Optional[str] = None
    row_count: int
    column_count: int
    created_at: datetime

    class Config:
        from_attributes = True