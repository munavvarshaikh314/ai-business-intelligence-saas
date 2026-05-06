from pydantic import BaseModel


class UploadResponse(BaseModel):
    message: str
    rows: int = 0
    columns: int = 0
    chunks: int = 0