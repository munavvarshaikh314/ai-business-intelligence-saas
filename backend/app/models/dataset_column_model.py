import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class DatasetColumn(Base):
    __tablename__ = "dataset_columns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False)

    column_name = Column(String(200), nullable=False)
    data_type = Column(String(50), nullable=False)

    is_nullable = Column(Boolean, default=True)

    # Relationships
    dataset = relationship("Dataset", back_populates="columns")