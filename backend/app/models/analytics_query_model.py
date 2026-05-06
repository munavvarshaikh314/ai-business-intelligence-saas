import uuid
from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database import Base


class AnalyticsQuery(Base):
    __tablename__ = "analytics_queries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False)

    query_text = Column(Text, nullable=False)
    query_type = Column(String(50), nullable=False)  # SQL / PANDAS / RAG

    sql_generated = Column(Text, nullable=True)

    executed_success = Column(Boolean, default=True)
    execution_time_ms = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())