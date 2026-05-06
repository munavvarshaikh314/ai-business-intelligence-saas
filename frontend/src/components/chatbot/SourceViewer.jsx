"use client";

export default function SourceViewer({ sources }) {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-3 bg-gray-50 border rounded p-3">
      <h3 className="font-semibold mb-2 text-sm">Sources</h3>

      <ul className="text-xs text-gray-700 space-y-2">
        {sources.map((s, idx) => (
          <li key={idx} className="border p-2 rounded bg-white">
            <p>
              <span className="font-semibold">File:</span> {s.file_name || "Unknown"}
            </p>
            <p>
              <span className="font-semibold">Page:</span> {s.page || "N/A"}
            </p>
            <p className="mt-1 text-gray-600">{s.text_snippet}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}