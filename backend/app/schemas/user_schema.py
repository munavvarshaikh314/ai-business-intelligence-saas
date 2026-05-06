from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID   # ✅ correct


class UserResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True