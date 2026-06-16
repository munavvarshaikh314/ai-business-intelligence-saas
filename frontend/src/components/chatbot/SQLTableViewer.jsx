"use client";

// Detect if a value looks like money
function isMonetary(colName, value) {
  return /price|amount|revenue|sales|profit|cost|income|salary|value|avg|average/i.test(colName) &&
    !isNaN(parseFloat(value));
}

// Detect if numeric
function isNumeric(value) {
  return !isNaN(parseFloat(value)) && isFinite(value);
}

// Format cell value based on column name and value type
function formatCell(colName, value) {
  if (value === null || value === undefined) return "—";
  if (isMonetary(colName, value)) {
    return `₹${Number(value).toLocaleString("en-IN", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`;
  }
  if (isNumeric(value) && String(value).includes(".")) {
    return Number(value).toLocaleString("en-IN", { maximumFractionDigits: 2 });
  }
  return String(value);
}

export default function SQLTableViewer({ data }) {
  if (!data || !Array.isArray(data.rows) || data.rows.length === 0) {
    return (
      <div className="mt-3 rounded-lg border border-slate-200 bg-slate-50 px-4 py-3">
        <p className="text-sm text-slate-500">Query returned no results.</p>
      </div>
    );
  }

  const columns = data.columns || Object.keys(data.rows[0]);
  const rows = data.rows;
  const showingAll = rows.length <= 50;
  const displayRows = rows.slice(0, 50);

  return (
    <div className="mt-3 rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">

      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2.5 border-b border-slate-100 bg-slate-50">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            SQL Result
          </span>
          <span className="rounded-full bg-slate-200 px-2 py-0.5 text-xs font-semibold text-slate-600">
            {rows.length} row{rows.length !== 1 ? "s" : ""}
          </span>
        </div>
        <span className="text-xs text-slate-400">
          {columns.length} column{columns.length !== 1 ? "s" : ""}
        </span>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50">
              <th className="w-8 px-3 py-2 text-left text-xs font-semibold text-slate-400">
                #
              </th>
              {columns.map((col) => (
                <th
                  key={col}
                  className="px-3 py-2 text-left text-xs font-semibold uppercase tracking-wide text-slate-600 whitespace-nowrap"
                >
                  {col.replace(/_/g, " ")}
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
            {displayRows.map((row, idx) => (
              <tr
                key={idx}
                className={`border-b border-slate-100 transition-colors hover:bg-emerald-50 ${
                  idx % 2 === 0 ? "bg-white" : "bg-slate-50/50"
                }`}
              >
                <td className="px-3 py-2 text-xs text-slate-300 font-mono">
                  {idx + 1}
                </td>
                {columns.map((col) => {
                  const val = row[col];
                  const formatted = formatCell(col, val);
                  const monetary = isMonetary(col, val);
                  const numeric = isNumeric(val);

                  return (
                    <td
                      key={col}
                      className={`px-3 py-2 whitespace-nowrap ${
                        monetary
                          ? "font-semibold text-emerald-700"
                          : numeric
                          ? "font-mono text-slate-700"
                          : "text-slate-700"
                      }`}
                    >
                      {formatted}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Footer */}
      {!showingAll && (
        <div className="px-4 py-2 border-t border-slate-100 bg-slate-50">
          <p className="text-xs text-slate-400">
            Showing first 50 of {rows.length} rows
          </p>
        </div>
      )}
    </div>
  );
}


// "use client";

// export default function SQLTableViewer({ data }) {
//   if (!data || !Array.isArray(data.rows) || data.rows.length === 0) {
//     return <p className="text-sm text-gray-600 mt-2">No SQL result rows.</p>;
//   }

//   const columns = Object.keys(data.rows[0]);

//   return (
//     <div className="overflow-x-auto mt-3 border rounded bg-white">
//       <table className="w-full text-sm">
//         <thead className="bg-gray-100">
//           <tr>
//             {columns.map((col) => (
//               <th key={col} className="text-left p-2 border">
//                 {col}
//               </th>
//             ))}
//           </tr>
//         </thead>

//         <tbody>
//           {data.rows.map((row, idx) => (
//             <tr key={idx} className="border">
//               {columns.map((col) => (
//                 <td key={col} className="p-2 border">
//                   {String(row[col])}
//                 </td>
//               ))}
//             </tr>
//           ))}
//         </tbody>
//       </table>
//     </div>
//   );
// }