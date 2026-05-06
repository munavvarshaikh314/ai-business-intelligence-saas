"use client";

import { useState } from "react";
import { useDataset } from "@/context/DatasetContext";

export default function CreateDatasetForm() {
  const { addDataset } = useDataset();

  const [name, setName] = useState("");
  const [datasetType, setDatasetType] = useState("CSV");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleCreate = async (e) => {
    e.preventDefault();
    setError("");

    if (!name.trim()) {
      setError("Dataset name is required");
      return;
    }

    setLoading(true);

    try {
      await addDataset(name, description, datasetType);
      setName("");
      setDescription("");
    } catch (err) {
      setError("Failed to create dataset");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleCreate} className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="text-lg font-bold text-slate-950 mb-3">Create Dataset</h2>

      {error && <p className="text-red-500 mb-2">{error}</p>}

      <input
        className="mb-2 w-full rounded-md border border-slate-200 p-2 outline-none focus:border-emerald-400"
        placeholder="Dataset Name"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />

      <select
        className="mb-2 w-full rounded-md border border-slate-200 p-2 outline-none focus:border-emerald-400"
        value={datasetType}
        onChange={(e) => setDatasetType(e.target.value)}
      >
        <option value="CSV">CSV analytics</option>
        <option value="PDF">PDF document</option>
        <option value="EXCEL">Excel analytics</option>
      </select>

      <textarea
        className="mb-3 w-full rounded-md border border-slate-200 p-2 outline-none focus:border-emerald-400"
        placeholder="Description (optional)"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />

      <button
        disabled={loading}
        className="rounded-md bg-slate-950 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:bg-slate-300"
      >
        {loading ? "Creating..." : "Create"}
      </button>
    </form>
  );
}
