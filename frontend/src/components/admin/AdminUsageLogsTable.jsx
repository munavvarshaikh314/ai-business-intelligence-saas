"use client";

export default function AdminUsageLogsTable({ logs }) {
  return (
    <div className="bg-white rounded shadow overflow-x-auto">
      <table className="w-full text-sm">
        <thead className="bg-gray-100">
          <tr>
            <th className="p-3 text-left">User</th>
            <th className="p-3 text-left">Endpoint</th>
            <th className="p-3 text-left">Tokens Used</th>
            <th className="p-3 text-left">Credits Used</th>
            <th className="p-3 text-left">Date</th>
          </tr>
        </thead>

        <tbody>
          {logs.map((log) => (
            <tr key={log.id} className="border-t">
              <td className="p-3">{log.user_email || log.user_id}</td>
              <td className="p-3">{log.endpoint}</td>
              <td className="p-3">{log.tokens_used}</td>
              <td className="p-3">{log.credits_used}</td>
              <td className="p-3">
                {new Date(log.created_at).toLocaleString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}