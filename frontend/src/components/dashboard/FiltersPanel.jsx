"use client";

import { useState } from "react";
import { Filter, X } from "lucide-react";

export default function FiltersPanel({ onFilter, columns = [] }) {
  const [open, setOpen] = useState(false);
  const [filters, setFilters] = useState({ column: "", operator: "equals", value: "" });

  const operators = ["equals", "contains", "greater than", "less than", "not equals"];

  const handleApply = () => {
    if (filters.column && filters.value) {
      onFilter?.(filters);
      setOpen(false);
    }
  };

  const handleClear = () => {
    setFilters({ column: "", operator: "equals", value: "" });
    onFilter?.(null);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:border-slate-300 hover:bg-slate-50"
      >
        <Filter size={14} />
        Filters
      </button>

      {open && (
        <div className="absolute right-0 top-10 z-20 w-72 rounded-xl border border-slate-200 bg-white p-4 shadow-xl">
          <div className="mb-3 flex items-center justify-between">
            <span className="text-sm font-semibold text-slate-800">Filter Data</span>
            <button onClick={() => setOpen(false)} className="text-slate-400 hover:text-slate-600">
              <X size={14} />
            </button>
          </div>

          <div className="space-y-3">
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-600">Column</label>
              <select
                value={filters.column}
                onChange={(e) => setFilters({ ...filters, column: e.target.value })}
                className="w-full rounded-md border border-slate-200 px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-emerald-500"
              >
                <option value="">Select column...</option>
                {columns.map((col) => (
                  <option key={col} value={col}>{col}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="mb-1 block text-xs font-medium text-slate-600">Operator</label>
              <select
                value={filters.operator}
                onChange={(e) => setFilters({ ...filters, operator: e.target.value })}
                className="w-full rounded-md border border-slate-200 px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-emerald-500"
              >
                {operators.map((op) => (
                  <option key={op} value={op}>{op}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="mb-1 block text-xs font-medium text-slate-600">Value</label>
              <input
                type="text"
                value={filters.value}
                onChange={(e) => setFilters({ ...filters, value: e.target.value })}
                placeholder="Enter value..."
                className="w-full rounded-md border border-slate-200 px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-emerald-500"
              />
            </div>

            <div className="flex gap-2 pt-1">
              <button
                onClick={handleApply}
                className="flex-1 rounded-md bg-slate-950 py-1.5 text-sm font-semibold text-white transition hover:bg-emerald-700"
              >
                Apply
              </button>
              <button
                onClick={handleClear}
                className="flex-1 rounded-md border border-slate-200 py-1.5 text-sm font-medium text-slate-600 transition hover:bg-slate-50"
              >
                Clear
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
