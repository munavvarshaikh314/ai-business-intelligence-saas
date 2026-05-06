"use client";

import { useEffect, useState } from "react";
import PaymentHistoryTable from "@/components/billing/PaymentHistoryTable";
import { fetchPaymentHistory } from "@/lib/paymentHistoryApi";

export default function PaymentsPage() {
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadPayments = async () => {
      try {
        const data = await fetchPaymentHistory();
        setPayments(data);
      } catch {
        setError("Failed to load payment history.");
      } finally {
        setLoading(false);
      }
    };

    loadPayments();
  }, []);

  return (
    <div className="p-6">
      <h1 className="mb-2 text-2xl font-bold text-slate-950">Payment History</h1>
      <p className="mb-6 text-sm text-slate-500">View all payments and download invoices.</p>

      {error && <p className="mb-4 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}
      {loading ? <p>Loading payments...</p> : <PaymentHistoryTable payments={payments} />}
    </div>
  );
}
