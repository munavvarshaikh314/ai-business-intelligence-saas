import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base


class UsageLog(Base):
    __tablename__ = "usage_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=True)

    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=True)

    query_type = Column(String(50), nullable=False)  # SQL / RAG / PREDICTION

    question = Column(Text, nullable=False)

    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)

    cost_estimate = Column(Integer, default=0)  # optional (in paise or cents)

    created_at = Column(DateTime(timezone=True), server_default=func.now())