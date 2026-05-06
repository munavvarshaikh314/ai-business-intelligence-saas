"use client";

export default function ChatSidebar({ sessions, activeSessionId, onSelect, onNewChat }) {
  return (
    <aside className="hidden w-72 shrink-0 overflow-y-auto rounded-lg border border-slate-200 bg-white p-4 shadow-sm lg:block">
      <div className="mb-4 flex items-center justify-between gap-3">
        <h2 className="text-lg font-bold text-slate-950">Chat Sessions</h2>
        <button
          onClick={onNewChat}
          className="rounded-md border border-slate-200 px-3 py-1.5 text-sm font-semibold text-slate-700 transition hover:border-emerald-300 hover:text-emerald-700"
        >
          New
        </button>
      </div>

      {sessions.length === 0 ? (
        <p className="rounded-md bg-slate-50 p-3 text-sm text-slate-500">No sessions found.</p>
      ) : (
        <ul className="space-y-2">
          {sessions.map((s) => (
            <li
              key={s.id}
              onClick={() => onSelect(s.id)}
              className={`cursor-pointer rounded-md border p-3 text-sm transition ${
                activeSessionId === s.id
                  ? "border-emerald-300 bg-emerald-50 font-semibold text-emerald-900"
                  : "border-slate-200 hover:border-slate-300 hover:bg-slate-50"
              }`}
            >
              <p>{s.session_name || s.title || "New Chat"}</p>
              <p className="mt-1 text-xs text-slate-500">
                {new Date(s.created_at).toLocaleString()}
              </p>
            </li>
          ))}
        </ul>
      )}
    </aside>
  );
}
