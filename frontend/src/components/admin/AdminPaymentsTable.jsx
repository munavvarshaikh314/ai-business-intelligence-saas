"use client";

export default function AdminPaymentsTable({ payments }) {
  return (
    <div className="bg-white rounded shadow overflow-x-auto">
      <table className="w-full text-sm">
        <thead className="bg-gray-100">
          <tr>
            <th className="p-3 text-left">Payment ID</th>
            <th className="p-3 text-left">User</th>
            <th className="p-3 text-left">Credits</th>
            <th className="p-3 text-left">Amount</th>
            <th className="p-3 text-left">Status</th>
            <th className="p-3 text-left">Date</th>
          </tr>
        </thead>

        <tbody>
          {payments.map((p) => (
            <tr key={p.id} className="border-t">
              <td className="p-3">{p.razorpay_payment_id || p.id}</td>
              <td className="p-3">{p.user_email || p.user_id}</td>
              <td className="p-3">{p.credits_added}</td>
              <td className="p-3">
                {p.amount_paid} {p.currency}
              </td>
              <td className="p-3">{p.status}</td>
              <td className="p-3">
                {new Date(p.created_at).toLocaleString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}