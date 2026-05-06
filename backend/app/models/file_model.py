import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class File(Base):
    __tablename__ = "files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False)

    file_name = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)  # csv/pdf/xlsx
    file_path = Column(String, nullable=False)

    file_size = Column(BigInteger, nullable=False)

    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="files")
    dataset = relationship("Dataset", back_populates="files")
    chunks = relationship("DocumentChunk", back_populates="file", cascade="all, delete-orphan")