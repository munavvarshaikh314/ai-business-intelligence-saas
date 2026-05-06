import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class FAISSIndex(Base):
    __tablename__ = "faiss_indexes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False)

    index_path = Column(String, nullable=False)

    embedding_model = Column(String(200), nullable=False)
    vector_dim = Column(Integer, nullable=False)

    chunk_size = Column(Integer, default=500)
    chunk_overlap = Column(Integer, default=100)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    dataset = relationship("Dataset", back_populates="faiss_indexes")