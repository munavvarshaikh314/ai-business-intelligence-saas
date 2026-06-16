"use client";

export default function AIInsightCard({ insight }) {
  if (!insight) return null;

  return (
    <div className="mb-3 rounded-xl border border-emerald-200 bg-emerald-50 shadow-sm">
      <div className="border-b border-emerald-100 px-4 py-2">
        <h3 className="text-sm font-semibold text-emerald-700">
          AI Insight
        </h3>
      </div>

      <div className="p-4">
        <p className="text-sm leading-relaxed text-slate-700">
          {insight}
        </p>
      </div>
    </div>
  );
}