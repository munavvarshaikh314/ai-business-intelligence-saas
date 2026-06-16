"use client";

import {
  AreaChart, Area, XAxis, YAxis, Tooltip,
  CartesianGrid, ResponsiveContainer, Legend,
} from "recharts";

export default function ProfitChart({ data }) {
  if (!data || data.length === 0) return null;

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="mb-1 text-lg font-bold text-slate-950">Profit Over Time</h2>
      <p className="mb-3 text-xs text-slate-400">Revenue vs Cost trend analysis</p>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
          <defs>
            <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#047857" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#047857" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="colorProfit" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="date" tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip
            contentStyle={{ borderRadius: "8px", border: "1px solid #e2e8f0", fontSize: "12px" }}
          />
          <Legend />
          <Area type="monotone" dataKey="revenue" stroke="#047857" strokeWidth={2}
            fill="url(#colorRevenue)" name="Revenue" />
          <Area type="monotone" dataKey="profit" stroke="#3b82f6" strokeWidth={2}
            fill="url(#colorProfit)" name="Profit" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
