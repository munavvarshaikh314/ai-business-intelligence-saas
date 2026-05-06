"use client";

import { useDataset } from "@/context/DatasetContext";

export default function DatasetSelector() {
  const { datasets, activeDataset, selectDataset, loading } = useDataset();

  if (loading) return <p className="text-sm">Loading datasets...</p>;

  if (!datasets.length) {
    return <p className="text-sm text-red-500">No datasets found</p>;
  }

  return (
    <select
      className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm outline-none focus:border-emerald-400"
      value={activeDataset?.id || ""}
      onChange={(e) => {
        const selected = datasets.find((d) => d.id === e.target.value);
        if (selected) selectDataset(selected);
      }}
    >
      {datasets.map((dataset) => (
        <option key={dataset.id} value={dataset.id}>
          {dataset.dataset_name}
        </option>
      ))}
    </select>
  );
}
