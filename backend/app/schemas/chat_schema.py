from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from typing import Any, Optional

class CreateSessionRequest(BaseModel):
    session_name: Optional[str] = "New Chat"


class ChatSessionResponse(BaseModel):
    id: str
    user_id: str
    dataset_id: str
    session_name: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatMessageResponse(BaseModel):
    id: str
    session_id: str
    sender: str
    message_text: str
    created_at: datetime

    class Config:
        from_attributes = True


class AskRequest(BaseModel):
    session_id: str
    question: str


class SourceItem(BaseModel):
    source: str
    page: Optional[int] = None
    chunk_index: Optional[int] = None
    score: Optional[float] = None


class AskResponse(BaseModel):
    answer: str
    confidence: float
    query_type: str
    sources: List = []
    data: Optional[Any] = None

    rewritten_query: Optional[str] = None
    verdict: Optional[str] = None
    reason: Optional[str] = None

    conflict: Optional[bool] = False
    conflicting_points: Optional[List[str]] = []