import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.dependencies import get_current_user
from app.models.payment_model import Payment

router = APIRouter()


@router.get("/download/{payment_id}")
def download_invoice(payment_id: str, current_user=Depends(get_current_user)):
    db: Session = SessionLocal()

    payment = db.query(Payment).filter(
        Payment.id == payment_id,
        Payment.user_id == current_user.id
    ).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if not payment.invoice_pdf_path:
        raise HTTPException(status_code=404, detail="Invoice not generated")

    if not os.path.exists(payment.invoice_pdf_path):
        raise HTTPException(status_code=404, detail="Invoice file missing")

    return FileResponse(
        payment.invoice_pdf_path,
        media_type="application/pdf",
        filename=f"{payment.invoice_number}.pdf"
    )