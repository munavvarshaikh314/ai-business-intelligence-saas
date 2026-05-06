from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.services.payment_history_service import PaymentHistoryService

router = APIRouter()


@router.get("/history")
def payment_history(current_user=Depends(get_current_user)):
    payments = PaymentHistoryService.get_user_payments(current_user.id)

    return [
        {
            "id": str(p.id),
            "order_id": p.razorpay_order_id,
            "payment_id": p.razorpay_payment_id,
            "amount": p.amount,
            "credits_added": p.credits_added,
            "status": p.status,
            "invoice_number": p.invoice_number,
            "created_at": p.created_at
        }
        for p in payments
    ]