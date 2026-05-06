"use client";

export default function StatsCards({ summary }) {
  if (!summary) return null;

  const formatNumber = (value) => {
    if (value === null || value === undefined) return "N/A";
    return new Intl.NumberFormat("en-IN", { maximumFractionDigits: 2 }).format(value);
  };

  const cards = [
    { label: "Rows", value: summary.total_rows },
    { label: "Orders", value: summary.total_orders },
    { label: "Revenue", value: summary.total_revenue },
    { label: "Avg Value", value: summary.avg_order_value },
  ];

  return (
    <div className="mb-6 grid gap-4 md:grid-cols-4">
      {cards.map((c, idx) => (
        <div key={idx} className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">{c.label}</p>
          <p className="mt-2 text-2xl font-bold text-slate-950">{formatNumber(c.value)}</p>
        </div>
      ))}
    </div>
  );
}
