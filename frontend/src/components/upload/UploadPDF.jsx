"use client";

import { useState } from "react";
import { uploadPDF } from "@/lib/uploadApi";
import UploadProgress from "./UploadProgress";
import { useDataset } from "@/context/DatasetContext";
import { UploadErrors } from "@/lib/errors";

export default function UploadPDF() {
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
      setError("No dataset selected. Please create or select a dataset first.");
      return;
    }

    if (!file) {
      setError("Please select a PDF file to upload.");
      return;
    }

    if (!file.name.endsWith(".pdf")) {
      setError("Only .pdf files are supported. Please select a valid PDF file.");
      return;
    }

    const maxSize = 50 * 1024 * 1024; // 50MB
    if (file.size > maxSize) {
      setError("File is too large. Maximum allowed size is 50MB.");
      return;
    }

    setLoading(true);
    setProgress(0);

    try {
      const res = await uploadPDF(activeDataset.id, file, setProgress);
      setMessage(res.message || "PDF uploaded and indexed successfully. You can now ask questions about it.");
      setFile(null);
    } catch (err) {
      setError(UploadErrors.pdf(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2 className="mb-2 text-lg font-bold text-slate-950">Upload PDF Document</h2>
      <p className="text-sm text-gray-600 mb-3">
        Upload a PDF to enable document Q&A and RAG-powered answers with citations.
      </p>

      {message && (
        <div className="mb-3 rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
          ✓ {message}
        </div>
      )}

      {error && (
        <div className="mb-3 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </div>
      )}

      <input
        type="file"
        accept=".pdf"
        className="mb-3 w-full rounded-md border border-slate-200 p-2 text-sm"
        onChange={(e) => {
          setError("");
          setMessage("");
          setFile(e.target.files[0]);
        }}
      />

      {loading && <UploadProgress progress={progress} />}

      <button
        onClick={handleUpload}
        disabled={loading}
        className="mt-3 rounded-md bg-slate-950 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:bg-slate-300 disabled:cursor-not-allowed"
      >
        {loading ? "Uploading..." : "Upload PDF"}
      </button>
    </div>
  );
}


// "use client";

// import { useState } from "react";
// import { uploadPDF } from "@/lib/uploadApi";
// import UploadProgress from "./UploadProgress";
// import { useDataset } from "@/context/DatasetContext";

// export default function UploadPDF() {
//   const { activeDataset } = useDataset();

//   const [file, setFile] = useState(null);
//   const [progress, setProgress] = useState(0);

//   const [loading, setLoading] = useState(false);
//   const [message, setMessage] = useState("");
//   const [error, setError] = useState("");

//   const handleUpload = async () => {
//     setMessage("");
//     setError("");

//     if (!activeDataset) {
//       setError("No active dataset selected.");
//       return;
//     }

//     if (!file) {
//       setError("Please select a PDF file.");
//       return;
//     }

//     setLoading(true);
//     setProgress(0);

//     try {
//       const res = await uploadPDF(activeDataset.id, file, setProgress);
//       setMessage(res.message || "PDF uploaded successfully!");
//       setFile(null);
//     } catch (err) {
//       setError(err?.response?.data?.detail || "PDF upload failed.");
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <div>
//       <h2 className="mb-2 text-lg font-bold text-slate-950">Upload PDF Document</h2>

//       <p className="text-sm text-gray-600 mb-3">
//         Upload PDF to enable RAG chatbot and document Q&A.
//       </p>

//       {message && <p className="text-green-600 mb-2">{message}</p>}
//       {error && <p className="text-red-600 mb-2">{error}</p>}

//       <input
//         type="file"
//         accept=".pdf"
//         className="mb-3 w-full rounded-md border border-slate-200 p-2 text-sm"
//         onChange={(e) => setFile(e.target.files[0])}
//       />

//       {loading && <UploadProgress progress={progress} />}

//       <button
//         onClick={handleUpload}
//         disabled={loading}
//         className="mt-3 rounded-md bg-slate-950 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:bg-slate-300"
//       >
//         {loading ? "Uploading..." : "Upload PDF"}
//       </button>
//     </div>
//   );
// }
