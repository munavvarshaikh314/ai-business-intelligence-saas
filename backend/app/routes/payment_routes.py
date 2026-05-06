from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.dependencies import get_current_user
from app.services.payment_service import PaymentService

router = APIRouter()


class CreateOrderRequest(BaseModel):
    amount: int  # in paise


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


@router.post("/create-order")
def create_order(payload: CreateOrderRequest, current_user=Depends(get_current_user)):
    return PaymentService.create_payment_order(current_user.id, payload.amount)


@router.post("/verify")
def verify_payment(payload: VerifyPaymentRequest, current_user=Depends(get_current_user)):
    return PaymentService.verify_payment(
        current_user.id,
        payload.razorpay_order_id,
        payload.razorpay_payment_id,
        payload.razorpay_signature
    )