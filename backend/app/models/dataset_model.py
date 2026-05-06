import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    table_name = Column(String(255), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    dataset_name = Column(String(200), nullable=False)
    dataset_type = Column(String(20), nullable=False)  # CSV / PDF / EXCEL
    description = Column(Text, nullable=True)
    
    index_status = Column(String(50), default="PENDING")  
    index_progress = Column(Integer, default=0)           
    row_count = Column(Integer, default=0)
    column_count = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="datasets")
    chunks = relationship("DocumentChunk", back_populates="dataset", cascade="all, delete-orphan")
    files = relationship("File", back_populates="dataset", cascade="all, delete-orphan")
    columns = relationship("DatasetColumn", back_populates="dataset", cascade="all, delete-orphan")
    
    
    chat_sessions = relationship("ChatSession", back_populates="dataset", cascade="all, delete-orphan")
    rows = relationship("DatasetRow", cascade="all, delete-orphan")
    faiss_indexes = relationship("FAISSIndex", back_populates="dataset", cascade="all, delete-orphan")