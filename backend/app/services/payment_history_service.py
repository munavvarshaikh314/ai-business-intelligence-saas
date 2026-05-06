from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.payment_model import Payment


class PaymentHistoryService:

    @staticmethod
    def get_user_payments(user_id: str):
        db: Session = SessionLocal()

        payments = db.query(Payment).filter(
            Payment.user_id == user_id
        ).order_by(Payment.created_at.desc()).all()

        return payments