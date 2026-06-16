"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { CreditCard, History, Wallet } from "lucide-react";
import { createOrder, verifyPayment } from "@/lib/paymentApi";
import { loadRazorpay } from "@/lib/loadRazorpay";
import { useCredits } from "@/context/CreditsContext";
import { useAuth } from "@/context/AuthContext";

const creditPacks = [
  { credits: 50, label: "Starter", note: "Good for testing workflows" },
  { credits: 100, label: "Growth", note: "Balanced for regular use" },
  { credits: 200, label: "Team", note: "More room for analytics" },
  { credits: 500, label: "Scale", note: "Best for heavy usage" },
];

export default function BillingPage() {
  const { user } = useAuth();
  const { credits: currentCredits, loadCredits } = useCredits();

  const [selectedCredits, setSelectedCredits] = useState(100);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("info");

  const selectedPack = useMemo(
    () => creditPacks.find((pack) => pack.credits === selectedCredits),
    [selectedCredits]
  );

  const showMessage = (text, type = "info") => {
    setMessage(text);
    setMessageType(type);
  };

  const handlePayment = async () => {
    setLoading(true);
    showMessage("");

    try {
      const loaded = await loadRazorpay();
      if (!loaded) {
        showMessage("Razorpay SDK failed to load. Please check your internet connection.", "error");
        return;
      }

      const order = await createOrder(selectedCredits);
      const razorpayKey = order.key;

      if (!razorpayKey) {
        showMessage("Payment configuration error: Razorpay key is missing. Check backend RAZORPAY_KEY_ID or frontend NEXT_PUBLIC_RAZORPAY_KEY_ID.", "error");
        console.error("Missing Razorpay key in order response:", order);
        return;
      }

      const options = {
        key: razorpayKey,
        amount: order.amount,
        currency: order.currency,
        name: "AI BI RAG Dashboard",
        description: `Buy ${order.credits} credits`,
        order_id: order.order_id,
        prefill: {
          name: user?.name || "",
          email: user?.email || "",
        },
        handler: async function (response) {
          try {
            const verifyRes = await verifyPayment({
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
            });

            await loadCredits();
            showMessage(`Payment successful. ${verifyRes.credits_added || order.credits} credits added.`, "success");
          } catch (err) {
            showMessage(err?.response?.data?.detail || "Payment verification failed. Please contact support.", "error");
          }
        },
        modal: {
          ondismiss: () => showMessage("Payment cancelled before completion.", "info"),
        },
        theme: {
          color: "#0f172a",
        },
      };

      const razorpay = new window.Razorpay(options);
      razorpay.on("payment.failed", function (response) {
        showMessage(response?.error?.description || "Payment failed.", "error");
        console.error("Razorpay payment failed:", response?.error);
      });
      razorpay.open();
    } catch (err) {
      showMessage(err?.response?.data?.detail || "Payment failed. Please try again.", "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-emerald-600">Billing</p>
            <h1 className="mt-2 text-3xl font-bold text-slate-950">Credits & Payments</h1>
            <p className="mt-2 text-sm text-slate-500">Buy credits securely through Razorpay checkout.</p>
          </div>
          <div className="rounded-lg border border-slate-200 px-4 py-3">
            <p className="text-sm text-slate-500">Available Credits</p>
            <p className="mt-1 text-2xl font-bold text-slate-950">{currentCredits}</p>
          </div>
        </div>
      </section>

      <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
        <section className="grid gap-4 md:grid-cols-2">
          {creditPacks.map((pack) => (
            <button
              key={pack.credits}
              onClick={() => setSelectedCredits(pack.credits)}
              className={`rounded-lg border bg-white p-5 text-left shadow-sm transition hover:-translate-y-0.5 hover:shadow-md ${
                selectedCredits === pack.credits
                  ? "border-emerald-400 ring-2 ring-emerald-100"
                  : "border-slate-200"
              }`}
            >
              <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-md bg-slate-950 text-white">
                <Wallet size={20} />
              </div>
              <p className="text-sm font-semibold text-emerald-700">{pack.label}</p>
              <h2 className="mt-1 text-2xl font-bold text-slate-950">{pack.credits} Credits</h2>
              <p className="mt-2 text-sm text-slate-500">{pack.note}</p>
              <p className="mt-4 text-sm font-semibold text-slate-700">Pay Rs {pack.credits}</p>
            </button>
          ))}
        </section>

        <aside className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <div className="mb-5 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-md bg-emerald-50 text-emerald-700">
              <CreditCard size={20} />
            </div>
            <div>
              <h2 className="font-bold text-slate-950">Checkout</h2>
              <p className="text-sm text-slate-500">{selectedPack?.label} pack selected</p>
            </div>
          </div>

          <div className="space-y-3 rounded-md bg-slate-50 p-4 text-sm">
            <div className="flex justify-between">
              <span className="text-slate-500">Credits</span>
              <span className="font-semibold text-slate-900">{selectedCredits}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Amount</span>
              <span className="font-semibold text-slate-900">Rs {selectedCredits}</span>
            </div>
          </div>

          <button
            onClick={handlePayment}
            disabled={loading}
            className="mt-5 w-full rounded-md bg-slate-950 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            {loading ? "Opening Checkout..." : "Buy Credits"}
          </button>

          <Link
            href="/dashboard/payments"
            className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-emerald-700 hover:text-emerald-800"
          >
            <History size={16} />
            View Payment History
          </Link>

          {message && (
            <p
              className={`mt-4 rounded-md px-3 py-2 text-sm ${
                messageType === "error"
                  ? "border border-red-200 bg-red-50 text-red-700"
                  : messageType === "success"
                    ? "border border-emerald-200 bg-emerald-50 text-emerald-700"
                    : "border border-slate-200 bg-slate-50 text-slate-600"
              }`}
            >
              {message}
            </p>
          )}
        </aside>
      </div>
    </div>
  );
}
