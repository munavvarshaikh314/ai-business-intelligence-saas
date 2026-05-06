import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base


class MLModelRegistry(Base):
    __tablename__ = "ml_models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False)

    model_name = Column(String(255), nullable=False)   # saved file name
    model_type = Column(String(50), nullable=False)    # regression / classification
    target_column = Column(String(255), nullable=False)

    metrics_json = Column(Text, nullable=True)         # store metrics as JSON string

    created_at = Column(DateTime(timezone=True), server_default=func.now())