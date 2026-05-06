import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

INVOICE_DIR = "app/storage/invoices"


class InvoiceService:

    @staticmethod
    def ensure_invoice_dir():
        if not os.path.exists(INVOICE_DIR):
            os.makedirs(INVOICE_DIR)

    @staticmethod
    def generate_invoice_number(payment_id: str):
        # Simple invoice format: INV-2026-XXXX
        return f"INV-{datetime.now().year}-{str(payment_id)[:8].upper()}"

    @staticmethod
    def generate_invoice_pdf(payment, user_email: str):
        """
        Generates invoice PDF file and returns file path.
        """
        InvoiceService.ensure_invoice_dir()

        invoice_number = payment.invoice_number
        filename = f"{invoice_number}.pdf"
        file_path = os.path.join(INVOICE_DIR, filename)

        c = canvas.Canvas(file_path, pagesize=A4)
        width, height = A4

        # Header
        c.setFont("Helvetica-Bold", 18)
        c.drawString(50, height - 60, "AI BI RAG Dashboard Invoice")

        c.setFont("Helvetica", 12)
        c.drawString(50, height - 90, f"Invoice Number: {invoice_number}")
        c.drawString(50, height - 110, f"Invoice Date: {datetime.now().strftime('%d-%m-%Y')}")

        # Company Info
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 150, "Seller:")

        c.setFont("Helvetica", 11)
        c.drawString(50, height - 170, "Company: AI BI SaaS Pvt Ltd")
        c.drawString(50, height - 190, "Email: support@aibisaas.com")
        c.drawString(50, height - 210, "Location: Mumbai, India")

        # Customer Info
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 250, "Buyer:")

        c.setFont("Helvetica", 11)
        c.drawString(50, height - 270, f"Customer Email: {user_email}")

        # Payment Details
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 320, "Payment Details:")

        c.setFont("Helvetica", 11)
        c.drawString(50, height - 350, f"Razorpay Order ID: {payment.razorpay_order_id}")
        c.drawString(50, height - 370, f"Razorpay Payment ID: {payment.razorpay_payment_id}")
        c.drawString(50, height - 390, f"Status: {payment.status}")

        # Credits
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 440, "Purchase Summary:")

        c.setFont("Helvetica", 11)
        c.drawString(50, height - 470, f"Credits Added: {payment.credits_added}")
        c.drawString(50, height - 490, f"Amount Paid: ₹{payment.amount / 100:.2f}")

        # Footer
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(50, 80, "Thank you for using AI BI SaaS Platform.")
        c.drawString(50, 60, "This is a system-generated invoice.")

        c.showPage()
        c.save()

        return file_path