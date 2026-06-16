from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models.payment_model import Payment
from app.services.razorpay_service import RazorpayService
from app.services.credit_service import CreditService


class PaymentService:

    @staticmethod
    def calculate_credits(amount: int) -> int:
        """
        Amount in paise. 1 rupee = 1 credit.
        ₹100 (10000 paise) = 100 credits
        """
        rupees = amount / 100
        return int(rupees)

    @staticmethod
    def create_payment_order(user_id: str, amount: int):
        """amount in paise"""
        if amount <= 0:
            raise HTTPException(status_code=400, detail="Amount must be greater than 0")

        if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
            raise HTTPException(
                status_code=500,
                detail="Razorpay keys not configured. Add RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET to .env"
            )

        db: Session = SessionLocal()
        try:
            order = RazorpayService.create_order(amount)
            credits = PaymentService.calculate_credits(amount)

            payment = Payment(
                user_id=user_id,
                razorpay_order_id=order["id"],
                amount=amount,
                credits_added=credits,
                status="CREATED"
            )
            db.add(payment)
            db.commit()
            db.refresh(payment)

            return {
                "order_id": order["id"],
                "amount": amount,
                "currency": order.get("currency", "INR"),
                "credits": credits,
                "razorpay_key_id": settings.RAZORPAY_KEY_ID,
                "key_id": settings.RAZORPAY_KEY_ID,
            }
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Payment order creation failed: {str(e)}")
        finally:
            db.close()

    @staticmethod
    def verify_payment(user_id: str, order_id: str, payment_id: str, signature: str):
        db: Session = SessionLocal()
        try:
            payment = db.query(Payment).filter(
                Payment.razorpay_order_id == order_id,
                Payment.user_id == user_id
            ).first()

            if not payment:
                raise HTTPException(status_code=404, detail="Payment order not found")

            if payment.status == "SUCCESS":
                return {"message": "Already verified", "credits_added": payment.credits_added}

            is_valid = RazorpayService.verify_signature(order_id, payment_id, signature)

            if not is_valid:
                payment.status = "FAILED"
                db.commit()
                raise HTTPException(status_code=400, detail="Payment signature verification failed")

            payment.status = "SUCCESS"
            payment.razorpay_payment_id = payment_id
            payment.razorpay_signature = signature
            db.commit()

            CreditService.add_credits(user_id, payment.credits_added)

            return {
                "message": "Payment verified and credits added",
                "credits_added": payment.credits_added
            }
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Payment verification failed: {str(e)}")
        finally:
            db.close()
