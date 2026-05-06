"use client";

import { useDataset } from "@/context/DatasetContext";

export default function DatasetList() {
  const { datasets, activeDataset, selectDataset, removeDataset } = useDataset();

  if (!datasets.length) return <p>No datasets created yet.</p>;

  return (
    <div className="mt-4 rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <h2 className="text-lg font-bold mb-3">Your Datasets</h2>

      <ul className="space-y-2">
        {datasets.map((d) => (
          <li
            key={d.id}
            className={`flex justify-between items-center border p-2 rounded ${
              activeDataset?.id === d.id ? "bg-gray-100" : ""
            }`}
          >
            <div
              className="cursor-pointer"
              onClick={() => selectDataset(d)}
            >
              <p className="font-semibold">{d.dataset_name}</p>
              <p className="text-sm text-gray-600">{d.description}</p>
            </div>

            <button
              className="text-red-500 text-sm"
              onClick={() => removeDataset(d.id)}
            >
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
