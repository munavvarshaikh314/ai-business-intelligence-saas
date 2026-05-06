import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB

from app.database import Base


class ModelRegistry(Base):
    __tablename__ = "model_registry"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False)

    model_name = Column(String(200), nullable=False)
    model_type = Column(String(50), nullable=False)  # regression/classification

    model_path = Column(String, nullable=False)

    metrics = Column(JSONB, nullable=True)

    trained_at = Column(DateTime(timezone=True), server_default=func.now())