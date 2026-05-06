"use client";

import { useState } from "react";
import { createOrder, verifyPayment } from "@/lib/paymentApi";
import { loadRazorpay } from "@/lib/loadRazorpay";
import { useCredits } from "@/context/CreditsContext";

export default function BillingPage() {
  const { loadCredits } = useCredits();

  const [credits, setCredits] = useState(100);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handlePayment = async () => {
    setLoading(true);
    setMessage("");

    const loaded = await loadRazorpay();

    if (!loaded) {
      setMessage("Razorpay SDK failed to load.");
      setLoading(false);
      return;
    }

    try {
      const order = await createOrder(credits);

      const options = {
        key: order.key_id,
        amount: order.amount,
        currency: "INR",
        name: "AI BI RAG Dashboard",
        description: `Buy ${credits} credits`,
        order_id: order.order_id,

        handler: async function (response) {
          const verifyRes = await verifyPayment({
            razorpay_order_id: response.razorpay_order_id,
            razorpay_payment_id: response.razorpay_payment_id,
            razorpay_signature: response.razorpay_signature,
          });

          setMessage("Payment successful. Credits updated.");
          await loadCredits();
        },

        theme: {
          color: "#000000",
        },
      };

      const razorpay = new window.Razorpay(options);
      razorpay.open();
    } catch (err) {
      setMessage("Payment failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 bg-gray-100 min-h-screen">
      <h1 className="text-2xl font-bold mb-4">Billing & Credits</h1>

      <div className="bg-white p-4 rounded shadow max-w-md">
        <label className="block mb-2 font-semibold">
          Select Credits to Buy
        </label>

        <select
          value={credits}
          onChange={(e) => setCredits(Number(e.target.value))}
          className="border p-2 rounded w-full mb-4"
        >
          <option value={50}>50 Credits</option>
          <option value={100}>100 Credits</option>
          <option value={200}>200 Credits</option>
          <option value={500}>500 Credits</option>
        </select>

        <button
          onClick={handlePayment}
          disabled={loading}
          className="bg-black text-white px-4 py-2 rounded w-full"
        >
          {loading ? "Processing..." : "Buy Credits"}
        </button>
        <a href="/dashboard/payments" className="text-blue-600 underline text-sm">
  View Payment History →
</a>

        {message && <p className="mt-3 text-sm text-blue-600">{message}</p>}
      </div>
    </div>
  );
}