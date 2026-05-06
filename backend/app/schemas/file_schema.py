from pydantic import BaseModel
from datetime import datetime


class FileResponse(BaseModel):
    id: str
    user_id: str
    dataset_id: str
    file_name: str
    file_type: str
    file_path: str
    file_size: int
    uploaded_at: datetime

    class Config:
        from_attributes = True