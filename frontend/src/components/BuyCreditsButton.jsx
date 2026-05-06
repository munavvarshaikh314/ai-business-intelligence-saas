"use client";

import { loadRazorpayScript } from "@/services/payment";

export default function BuyCreditsButton({ token }) {
  const handlePayment = async () => {
    const ok = await loadRazorpayScript();
    if (!ok) {
      alert("Razorpay SDK failed to load");
      return;
    }

    // Create order from backend
    const res = await fetch("http://localhost:8000/api/v1/payments/create-order", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ amount: 10000 }), // ₹100
    });

    const data = await res.json();

    const options = {
      key: data.razorpay_key_id,
      amount: data.amount,
      currency: "INR",
      name: "AI BI SaaS",
      description: `Buy ${data.credits} credits`,
      order_id: data.order_id,

      handler: async function (response) {
        // Verify payment in backend
        const verifyRes = await fetch("http://localhost:8000/api/v1/payments/verify", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            razorpay_order_id: response.razorpay_order_id,
            razorpay_payment_id: response.razorpay_payment_id,
            razorpay_signature: response.razorpay_signature,
          }),
        });

        const verifyData = await verifyRes.json();
        alert("Payment Success: " + verifyData.message);
      },

      theme: {
        color: "#0f172a",
      },
    };

    const paymentObject = new window.Razorpay(options);
    paymentObject.open();
  };

  return (
    <button
      onClick={handlePayment}
      className="px-4 py-2 bg-black text-white rounded-lg"
    >
      Buy Credits ₹100
    </button>
  );
}