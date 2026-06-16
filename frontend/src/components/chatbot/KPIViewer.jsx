// KPIViewer.jsx

export default function KPIViewer({ kpis }) {
  if (!kpis) return null;

  return (
    <div className="grid grid-cols-3 gap-3 mt-3">

      <div className="rounded-xl border bg-white p-4">
        <p className="text-xs text-slate-500">
          Products Found
        </p>
        <p className="text-2xl font-bold">
          {kpis.total_results}
        </p>
      </div>

      <div className="rounded-xl border bg-white p-4">
        <p className="text-xs text-slate-500">
          Top Product
        </p>
        <p className="text-2xl font-bold">
          {kpis.top_product}
        </p>
      </div>

      <div className="rounded-xl border bg-white p-4">
        <p className="text-xs text-slate-500">
          Top Sales
        </p>
        <p className="text-2xl font-bold">
          ₹{Number(kpis.top_sales).toLocaleString("en-IN")}
        </p>
      </div>

    </div>
  );
}