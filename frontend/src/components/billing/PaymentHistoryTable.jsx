"use client";

import { useState } from "react";
import { downloadInvoice } from "@/lib/paymentHistoryApi";
import { downloadBlobFile } from "@/lib/downloadFile";

export default function PaymentHistoryTable({ payments }) {
  const [loadingInvoiceId, setLoadingInvoiceId] = useState(null);

  const handleDownload = async (payment) => {
    setLoadingInvoiceId(payment.id);

    try {
      const blob = await downloadInvoice(payment.id);
      downloadBlobFile(blob, `invoice_${payment.id}.pdf`);
    } catch (err) {
      alert("Invoice download failed");
    } finally {
      setLoadingInvoiceId(null);
    }
  };

  return (
    <div className="bg-white rounded shadow overflow-x-auto">
      <table className="w-full text-sm">
        <thead className="bg-gray-100">
          <tr>
            <th className="p-3 text-left">Payment ID</th>
            <th className="p-3 text-left">Credits</th>
            <th className="p-3 text-left">Amount</th>
            <th className="p-3 text-left">Status</th>
            <th className="p-3 text-left">Date</th>
            <th className="p-3 text-left">Invoice</th>
          </tr>
        </thead>

        <tbody>
          {payments.map((p) => (
            <tr key={p.id} className="border-t">
              <td className="p-3">
                {p.razorpay_payment_id || p.id}
              </td>

              <td className="p-3">{p.credits_added}</td>

              <td className="p-3">
                {p.amount_paid} {p.currency}
              </td>

              <td className="p-3">
                <span
                  className={`px-2 py-1 rounded text-xs font-semibold ${
                    p.status === "SUCCESS"
                      ? "bg-green-100 text-green-700"
                      : "bg-red-100 text-red-700"
                  }`}
                >
                  {p.status}
                </span>
              </td>

              <td className="p-3">
                {new Date(p.created_at).toLocaleString()}
              </td>

              <td className="p-3">
                {p.status === "SUCCESS" ? (
                  <button
                    onClick={() => handleDownload(p)}
                    className="text-blue-600 underline"
                    disabled={loadingInvoiceId === p.id}
                  >
                    {loadingInvoiceId === p.id
                      ? "Downloading..."
                      : "Download PDF"}
                  </button>
                ) : (
                  <span className="text-gray-400">Not Available</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}