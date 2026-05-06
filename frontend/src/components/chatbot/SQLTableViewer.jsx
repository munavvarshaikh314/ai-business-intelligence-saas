"use client";

export default function SQLTableViewer({ data }) {
  if (!data || !Array.isArray(data.rows) || data.rows.length === 0) {
    return <p className="text-sm text-gray-600 mt-2">No SQL result rows.</p>;
  }

  const columns = Object.keys(data.rows[0]);

  return (
    <div className="overflow-x-auto mt-3 border rounded bg-white">
      <table className="w-full text-sm">
        <thead className="bg-gray-100">
          <tr>
            {columns.map((col) => (
              <th key={col} className="text-left p-2 border">
                {col}
              </th>
            ))}
          </tr>
        </thead>

        <tbody>
          {data.rows.map((row, idx) => (
            <tr key={idx} className="border">
              {columns.map((col) => (
                <td key={col} className="p-2 border">
                  {String(row[col])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}