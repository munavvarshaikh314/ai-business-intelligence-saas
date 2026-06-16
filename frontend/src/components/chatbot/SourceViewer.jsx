"use client";

export default function SourceViewer({ sources }) {
  if (!sources || sources.length === 0) return null;

  // Filter out SQL sources — only show document sources
  const docSources = sources.filter(s => s.text_snippet || s.page);
  if (docSources.length === 0) return null;

  return (
    <div className="mt-3 rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">

      {/* Header */}
      <div className="flex items-center gap-2 border-b border-slate-100 bg-slate-50 px-4 py-2.5">
        <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">
          Sources
        </span>
        <span className="rounded-full bg-slate-200 px-2 py-0.5 text-xs font-semibold text-slate-600">
          {docSources.length}
        </span>
      </div>

      {/* Source items */}
      <div className="divide-y divide-slate-100">
        {docSources.map((s, idx) => {
          const confidence = s.score;
          const confidencePercent = confidence
            ? Math.round(
                confidence > 1
                  ? Math.min(99, (1 / (1 + Math.exp(-confidence))) * 100)
                  : confidence * 100
              )
            : null;

          const confidenceColor =
            confidencePercent >= 75
              ? "text-emerald-600 bg-emerald-50 border-emerald-200"
              : confidencePercent >= 45
              ? "text-amber-600 bg-amber-50 border-amber-200"
              : "text-slate-500 bg-slate-50 border-slate-200";

          return (
            <div key={idx} className="px-4 py-3">
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-semibold text-slate-700">
                    📄 {s.file_name || `Chunk ${(s.chunk_index ?? idx) + 1}`}
                  </span>
                  {s.page && (
                    <span className="rounded bg-slate-100 px-1.5 py-0.5 text-xs text-slate-500">
                      Page {s.page}
                    </span>
                  )}
                </div>
                {confidencePercent !== null && (
                  <span className={`rounded-full border px-2 py-0.5 text-xs font-semibold ${confidenceColor}`}>
                    {confidencePercent}% match
                  </span>
                )}
              </div>
              {s.text_snippet && (
                <p className="text-xs leading-relaxed text-slate-500 line-clamp-3">
                  {s.text_snippet}
                </p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

// "use client";

// export default function SourceViewer({ sources }) {
//   if (!sources || sources.length === 0) return null;

//   return (
//     <div className="mt-3 bg-gray-50 border rounded p-3">
//       <h3 className="font-semibold mb-2 text-sm">Sources</h3>

//       <ul className="text-xs text-gray-700 space-y-2">
//         {sources.map((s, idx) => (
//           <li key={idx} className="border p-2 rounded bg-white">
//             <p>
//               <span className="font-semibold">File:</span> {s.file_name || "Unknown"}
//             </p>
//             <p>
//               <span className="font-semibold">Page:</span> {s.page || "N/A"}
//             </p>
//             <p className="mt-1 text-gray-600">{s.text_snippet}</p>
//           </li>
//         ))}
//       </ul>
//     </div>
//   );
// }