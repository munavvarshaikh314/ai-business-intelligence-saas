"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "@/context/AuthContext";
import PaymentHistoryTable from "@/components/billing/PaymentHistoryTable";
import { fetchPaymentHistory } from "@/lib/paymentHistoryApi";

export default function PaymentsPage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  const [payments, setPayments] = useState([]);
  const [loadingPayments, setLoadingPayments] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!loading && !user) router.push("/login");
  }, [user, loading]);

  useEffect(() => {
    const loadPayments = async () => {
      setLoadingPayments(true);
      setError("");

      try {
        const data = await fetchPaymentHistory();
        setPayments(data);
      } catch (err) {
        setError("Failed to load payment history.");
      } finally {
        setLoadingPayments(false);
      }
    };

    loadPayments();
  }, []);

  if (loading) return <p className="p-4">Loading...</p>;
  if (!user) return null;

  return (
    <div className="p-6 bg-gray-100 min-h-screen">
      <h1 className="text-2xl font-bold mb-2">Payment History</h1>
      <p className="text-gray-600 mb-6">
        View all payments and download invoices.
      </p>

      {error && <p className="text-red-600 mb-4">{error}</p>}

      {loadingPayments ? (
        <p>Loading payments...</p>
      ) : payments.length === 0 ? (
        <p className="text-gray-500">No payments found.</p>
      ) : (
        <PaymentHistoryTable payments={payments} />
      )}
    </div>
  );
}