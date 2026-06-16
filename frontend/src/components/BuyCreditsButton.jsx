"use client";

import { loadRazorpayScript } from "@/services/payment";
import { getToken } from "@/lib/auth";
import { useCredits } from "@/context/CreditsContext";

export default function BuyCreditsButton({ credits = 100, amount = 10000 }) {
  const { loadCredits } = useCredits();

  const handlePayment = async () => {
    const token = getToken();
    if (!token) {
      alert("Session expired. Please login again.");
      window.location.href = "/login";
      return;
    }

    const ok = await loadRazorpayScript();
    if (!ok) {
      alert("Razorpay SDK failed to load. Check your internet connection.");
      return;
    }

    let data;
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/payments/create-order`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ amount, credits }),
      });

      data = await res.json();

      if (!res.ok) {
        alert("Order creation failed: " + (data.detail || "Unknown error"));
        return;
      }
    } catch (err) {
      alert("Could not reach payment server. Is the backend running?");
      return;
    }

    if (!data.razorpay_key_id) {
      alert("Payment configuration error. Contact support.");
      console.error("Missing razorpay_key_id in response:", data);
      return;
    }

    const options = {
      key: data.razorpay_key_id,
      amount: data.amount,
      currency: data.currency || "INR",
      name: "NeuralStack AI",
      description: `Buy ${data.credits} credits`,
      order_id: data.order_id,

      handler: async function (response) {
        try {
          const freshToken = getToken();
          const verifyRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/payments/verify`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "Authorization": `Bearer ${freshToken}`,
            },
            body: JSON.stringify({
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
            }),
          });

          const verifyData = await verifyRes.json();

          if (!verifyRes.ok) {
            alert("Verification failed: " + (verifyData.detail || "Unknown error"));
            return;
          }

          alert(`Payment successful! ${verifyData.credits_added} credits added.`);
          await loadCredits();
        } catch (err) {
          alert("Verification failed. Please contact support.");
          console.error("Verify error:", err);
        }
      },

      theme: { color: "#0f172a" },

      modal: {
        ondismiss: () => console.log("Payment modal closed."),
      },
    };

    const paymentObject = new window.Razorpay(options);

    paymentObject.on("payment.failed", function (response) {
      console.error("Payment failed:", response.error);
      alert("Payment failed: " + response.error.description);
    });

    paymentObject.open();
  };

  return (
    <button
      onClick={handlePayment}
      className="px-4 py-2 bg-black text-white rounded-lg hover:bg-gray-800 transition font-medium"
    >
      Buy {credits} Credits — ₹{amount / 100}
    </button>
  );
}
