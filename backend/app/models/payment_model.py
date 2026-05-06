import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    razorpay_order_id = Column(String(255), nullable=False)
    razorpay_payment_id = Column(String(255), nullable=True)
    razorpay_signature = Column(String(500), nullable=True)
    invoice_number = Column(String(50), unique=True, nullable=True)
    invoice_pdf_path = Column(String(500), nullable=True)

    amount = Column(Integer, nullable=False)  # in paise
    credits_added = Column(Integer, nullable=False)

    status = Column(String(50), default="CREATED")  # CREATED / SUCCESS / FAILED

    created_at = Column(DateTime(timezone=True), server_default=func.now())