import uuid
from sqlalchemy import Column, Text, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False)

    chunk_text = Column(Text, nullable=False)

    chunk_index = Column(Integer, nullable=False)

    page_number = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())