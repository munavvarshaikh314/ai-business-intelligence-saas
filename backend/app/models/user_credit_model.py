import uuid
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base


class UserCredit(Base):
    __tablename__ = "user_credits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)

    credits = Column(Integer, default=100, nullable=False)  # default free credits

    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())