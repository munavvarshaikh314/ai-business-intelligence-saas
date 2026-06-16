"use client";

import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer
} from "recharts";

const COLORS = ["#059669","#3b82f6","#f59e0b","#8b5cf6","#ef4444","#06b6d4","#84cc16","#f97316"];

function isIdCol(col) {
  return /^id$|_id$|^product_id|^customer_id|^order_id|^transaction_id/i.test(col);
}
function isMonetaryCol(col) {
  return /sales|revenue|profit|income|amount|price|cost|salary|expense/i.test(col);
}
function isDateCol(col) {
  return /date|month|year|time|period|day/i.test(col);
}
function isCategoryCol(col) {
  return /region|category|type|department|status|class|segment|name|rep|channel|method/i.test(col);
}
function isNumericCol(col, val) {
  return !isIdCol(col) && typeof val === "number";
}


function formatValue(value, colName) {
  if (typeof value !== "number") return value;
  const monetary = isMonetaryCol(colName || "");
  if (monetary) {
    if (value >= 100000) return `₹${(value / 100000).toFixed(1)}L`;
    if (value >= 1000) return `₹${(value / 1000).toFixed(1)}K`;
    return `₹${value.toFixed(0)}`;
  }
  if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
  if (value >= 1000) return `${(value / 1000).toFixed(1)}K`;
  return value.toLocaleString("en-IN", { maximumFractionDigits: 2 });
}

function prepareData(columns, rows) {
  return rows.map(row => {
    const entry = {};
    columns.forEach(col => {
      const val = row[col] ?? row[col.toLowerCase()] ?? null;
      entry[col] = typeof val === "string" && !isNaN(parseFloat(val)) && isFinite(val)
        ? parseFloat(val) : val;
    });
    return entry;
  });
}

function detectChartType(columns, data) {
  if (!data?.length) return null;

  const first = data[0];

  const numericCols = columns.filter(
    col => isNumericCol(col, first[col])
  );

  const categoryCols = columns.filter(
    col => isCategoryCol(col)
  );

  const dateCols = columns.filter(
    col => isDateCol(col)
  );

  // Time-series → Line chart
  if (dateCols.length > 0 && numericCols.length > 0) {
    return "line";
  }

  // Category vs Value → Bar chart
  if (categoryCols.length > 0 && numericCols.length > 0) {
    return "bar";
  }

  // Small categorical distribution → Pie chart
  if (
    categoryCols.length > 0 &&
    numericCols.length === 1 &&
    data.length <= 8
  ) {
    return "pie";
  }

  // Default
  if (numericCols.length > 0) {
    return "bar";
  }

  return null;
}


export default function AutoChart({ data, title }) {
  if (!data || !data.rows || data.rows.length === 0) return null;

  const columns = data.columns?.length > 0 ? data.columns : Object.keys(data.rows[0]);
  const rows = data.rows.slice(0, 20);
  const chartData = prepareData(columns, rows);
  const first = chartData[0];

  const chartType = detectChartType(columns, chartData);
  if (!chartType) return null;

  const numCols = columns.filter(c => isNumericCol(c, first[c]));
  const catCols = columns.filter(c => isCategoryCol(c) && !isIdCol(c));
  const dateCols = columns.filter(c => isDateCol(c));

  // ... your existing label/valueCol/plotCols logic ...

    // Limit to 2 most meaningful numeric columns (monetary first)
  const plotCols = [...numCols]
    .sort((a, b) => (isMonetaryCol(b) ? 1 : 0) - (isMonetaryCol(a) ? 1 : 0))
    .slice(0, 2);

  // ← ADD HERE — after plotCols is defined


  let finalChartData = chartData;
  if (chartData.length > 8 && catCols.length > 0) {
    const catCol = catCols[0];
    const valCol = plotCols[0];
    finalChartData = Object.values(
      chartData.reduce((acc, row) => {
        const cat = row[catCol];
        if (!acc[cat]) acc[cat] = { [catCol]: cat, [valCol]: 0 };
        acc[cat][valCol] += Number(row[valCol]) || 0;
        return acc;
      }, {})
    );
  }

  // Then replace all chartData references in JSX with finalChartData
  // Example:
  // <BarChart data={finalChartData} ...>
  // <PieChart> <Pie data={finalChartData} ...>
  // Best label column

  const rawLabel = catCols[0] || dateCols[0] ||
  columns.find(c => !isNumericCol(c, first[c]) && !isIdCol(c)) || columns[0];
  // If all label values are identical, use a non-numeric non-category column (e.g. product_id)
  const uniqueLabels = new Set(chartData.map(r => r[rawLabel])).size;

   // Prefer product_id style columns as label when data has repeated categories
const explicitIdLabel = columns.find(c =>
  /^product_id$|^item_id$|^id$/i.test(c)
);




  const labelCol = (explicitIdLabel && uniqueLabels < chartData.length)
  ? explicitIdLabel
  : rawLabel;

  const valueCol = numCols.find(c => isMonetaryCol(c)) || numCols[0];

 const effectiveLabelCol = finalChartData !== chartData ? catCols[0] : labelCol;


  const tooltipFormatter = (value, name) => [formatValue(value, name), name.replace(/_/g, " ")];
  const yTickFormatter = v => formatValue(v, valueCol);
  const xTickFormatter = v => { const s = String(v); return s.length > 12 ? s.slice(0, 12) + "…" : s; };

  return (
    <div className="mt-3 rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
      <div className="flex items-center justify-between px-4 py-2.5 border-b border-slate-100 bg-slate-50">
        <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">{title || "Chart"}</span>
        <span className="rounded-full bg-slate-200 px-2 py-0.5 text-xs font-semibold text-slate-600 capitalize">{chartType} chart</span>
      </div>
      <div className="p-4">
        <ResponsiveContainer width="100%" height={240}>
          {chartType === "bar" ? (
            <BarChart data={finalChartData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey={effectiveLabelCol} tick={{ fontSize: 11, fill: "#64748b" }} tickFormatter={xTickFormatter} />
              <YAxis tick={{ fontSize: 11, fill: "#64748b" }} tickFormatter={yTickFormatter} width={60} />
              <Tooltip formatter={tooltipFormatter} contentStyle={{ fontSize: 12, borderRadius: 8 }} />
              {plotCols.length > 1 && <Legend wrapperStyle={{ fontSize: 11 }} />}
              {plotCols.map((col, i) => (
                <Bar key={col} dataKey={col} fill={COLORS[i % COLORS.length]} radius={[4,4,0,0]} name={col.replace(/_/g," ")} />
              ))}
            </BarChart>
          ) : chartType === "line" ? (
            <LineChart data={finalChartData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey={effectiveLabelCol} tick={{ fontSize: 11, fill: "#64748b" }} tickFormatter={xTickFormatter} />
              <YAxis tick={{ fontSize: 11, fill: "#64748b" }} tickFormatter={yTickFormatter} width={60} />
              <Tooltip formatter={tooltipFormatter} contentStyle={{ fontSize: 12, borderRadius: 8 }} />
              {plotCols.length > 1 && <Legend wrapperStyle={{ fontSize: 11 }} />}
              {plotCols.map((col, i) => (
                <Line key={col} type="monotone" dataKey={col} stroke={COLORS[i % COLORS.length]} strokeWidth={2} dot={{ r: 3 }} name={col.replace(/_/g," ")} />
              ))}
            </LineChart>
          ) : (
            <PieChart>
              <Pie data={finalChartData} dataKey={valueCol} nameKey={effectiveLabelCol}
                cx="50%" cy="50%" outerRadius={100} innerRadius={50} paddingAngle={2}
                label={({ name, percent }) => `${String(name).slice(0,10)} ${(percent*100).toFixed(0)}%`}
                labelLine={false}>
                {chartData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip formatter={tooltipFormatter} contentStyle={{ fontSize: 12, borderRadius: 8 }} />
            </PieChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
}