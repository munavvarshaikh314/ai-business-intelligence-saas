"use client";

import { useState } from "react";
import { uploadCSV } from "@/lib/uploadApi";
import UploadProgress from "./UploadProgress";
import { useDataset } from "@/context/DatasetContext";

export default function UploadCSV() {
  const { activeDataset } = useDataset();

  const [file, setFile] = useState(null);
  const [progress, setProgress] = useState(0);

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const handleUpload = async () => {
    setMessage("");
    setError("");

    if (!activeDataset) {
      setError("No active dataset selected.");
      return;
    }

    if (!file) {
      setError("Please select a CSV file.");
      return;
    }

    setLoading(true);
    setProgress(0);

    try {
      const res = await uploadCSV(activeDataset.id, file, setProgress);
      setMessage(res.message || "CSV uploaded successfully!");
      setFile(null);
    } catch (err) {
      setError(err?.response?.data?.detail || "CSV upload failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2 className="mb-2 text-lg font-bold text-slate-950">Upload CSV Dataset</h2>

      <p className="text-sm text-gray-600 mb-3">
        Upload CSV to create SQL table + analytics dashboard.
      </p>

      {message && <p className="text-green-600 mb-2">{message}</p>}
      {error && <p className="text-red-600 mb-2">{error}</p>}

      <input
        type="file"
        accept=".csv"
        className="mb-3 w-full rounded-md border border-slate-200 p-2 text-sm"
        onChange={(e) => setFile(e.target.files[0])}
      />

      {loading && <UploadProgress progress={progress} />}

      <button
        onClick={handleUpload}
        disabled={loading}
        className="mt-3 rounded-md bg-slate-950 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:bg-slate-300"
      >
        {loading ? "Uploading..." : "Upload CSV"}
      </button>
    </div>
  );
}
