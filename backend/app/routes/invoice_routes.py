import io
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import A4  # type: ignore[import-not-found]
from reportlab.pdfgen import canvas  # type: ignore[import-not-found]
from app.database import SessionLocal
from app.dependencies import get_current_user
from app.models.payment_model import Payment
from app.models.user_model import User

router = APIRouter()


@router.get("/download/{payment_id}")
def download_invoice(payment_id: str, current_user=Depends(get_current_user)):
    db: Session = SessionLocal()
    try:
        payment = db.query(Payment).filter(
            Payment.id == payment_id,
            Payment.user_id == current_user.id
        ).first()

        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")

        if payment.status != "SUCCESS":
            raise HTTPException(
                status_code=400,
                detail="Invoice only available for successful payments"
            )

        user = db.query(User).filter(User.id == current_user.id).first()
        user_email = user.email if user else "customer@example.com"

        # Generate PDF in memory — no disk required
        pdf_bytes = _generate_invoice_bytes(payment, user_email)

        invoice_number = payment.invoice_number or f"INV-{str(payment.id)[:8].upper()}"

        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{invoice_number}.pdf"'
            }
        )
    finally:
        db.close()


def _generate_invoice_bytes(payment, user_email: str) -> bytes:
    """Generate invoice PDF in memory and return bytes. No disk writes."""
    

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    invoice_number = payment.invoice_number or f"INV-{str(payment.id)[:8].upper()}"

    # Header
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 60, "NeuralStack AI — Invoice")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 90, f"Invoice Number: {invoice_number}")
    c.drawString(50, height - 110,
        f"Invoice Date: {datetime.now().strftime('%d-%m-%Y')}")

    # Seller
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 150, "Seller:")
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 170, "NeuralStack AI Pvt Ltd")
    c.drawString(50, height - 190, "support@neuralstack.ai")
    c.drawString(50, height - 210, "Mumbai, India")

    # Buyer
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 250, "Buyer:")
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 270, f"Email: {user_email}")

    # Payment details
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 320, "Payment Details:")
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 350,
        f"Order ID: {payment.razorpay_order_id or 'N/A'}")
    c.drawString(50, height - 370,
        f"Payment ID: {payment.razorpay_payment_id or 'N/A'}")
    c.drawString(50, height - 390, f"Status: {payment.status}")

    # Purchase summary
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 440, "Purchase Summary:")
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 470,
        f"Credits Purchased: {payment.credits_added}")
    c.drawString(50, height - 490,
        f"Amount Paid: Rs.{(payment.amount or 0) / 100:.2f}")

    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, 80, "Thank you for using NeuralStack AI Platform.")
    c.drawString(50, 60, "This is a system-generated invoice.")

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer.read()

# import os
# from fastapi import APIRouter, Depends, HTTPException
# from fastapi.responses import FileResponse
# from sqlalchemy.orm import Session

# from app.database import SessionLocal
# from app.dependencies import get_current_user
# from app.models.payment_model import Payment

# router = APIRouter()


# @router.get("/download/{payment_id}")
# def download_invoice(payment_id: str, current_user=Depends(get_current_user)):
#     db: Session = SessionLocal()

#     payment = db.query(Payment).filter(
#         Payment.id == payment_id,
#         Payment.user_id == current_user.id
#     ).first()

#     if not payment:
#         raise HTTPException(status_code=404, detail="Payment not found")

#     if not payment.invoice_pdf_path:
#         raise HTTPException(status_code=404, detail="Invoice not generated")

#     if not os.path.exists(payment.invoice_pdf_path):
#         raise HTTPException(status_code=404, detail="Invoice file missing")

#     return FileResponse(
#         payment.invoice_pdf_path,
#         media_type="application/pdf",
#         filename=f"{payment.invoice_number}.pdf"
#     )