import razorpay
from app.config import settings


class RazorpayService:
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    @staticmethod
    def create_order(amount: int, currency: str = "INR"):
        """
        amount is in paise (50000 = ₹500)
        """
        order = RazorpayService.client.order.create({
            "amount": amount,
            "currency": currency,
            "payment_capture": 1
        })
        return order

    @staticmethod
    def verify_signature(order_id: str, payment_id: str, signature: str):
        try:
            RazorpayService.client.utility.verify_payment_signature({
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature
            })
            return True
        except:
            return False