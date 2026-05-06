from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user_credit_model import UserCredit


class CreditService:

    @staticmethod
    def get_or_create_credit(user_id: str):
        db: Session = SessionLocal()

        credit = db.query(UserCredit).filter(UserCredit.user_id == user_id).first()

        if not credit:
            credit = UserCredit(user_id=user_id, credits=100)
            db.add(credit)
            db.commit()
            db.refresh(credit)

        return credit

    @staticmethod
    def check_credits(user_id: str, required: int = 1):
        credit = CreditService.get_or_create_credit(user_id)

        if credit.credits < required:
            raise HTTPException(status_code=403, detail="Insufficient credits")

        return credit

    @staticmethod
    def deduct_credits(user_id: str, amount: int = 1):
        db: Session = SessionLocal()

        credit = db.query(UserCredit).filter(UserCredit.user_id == user_id).first()

        if not credit:
            raise HTTPException(status_code=404, detail="Credit record not found")

        if credit.credits < amount:
            raise HTTPException(status_code=403, detail="Insufficient credits")

        credit.credits -= amount
        db.commit()
        db.refresh(credit)

        return credit

    @staticmethod
    def add_credits(user_id: str, amount: int):
        db: Session = SessionLocal()

        credit = db.query(UserCredit).filter(UserCredit.user_id == user_id).first()

        if not credit:
            credit = UserCredit(user_id=user_id, credits=0)
            db.add(credit)

        credit.credits += amount
        db.commit()
        db.refresh(credit)

        return credit