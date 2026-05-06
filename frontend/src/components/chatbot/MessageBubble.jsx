"use client";

export default function MessageBubble({ role, text }) {
  const isUser = role === "user";

  return (
    <div className={`w-full flex ${isUser ? "justify-end" : "justify-start"} mb-3`}>
      <div
        className={`max-w-[82%] whitespace-pre-wrap rounded-lg px-4 py-3 text-sm leading-6 shadow-sm ${
          isUser
            ? "bg-slate-950 text-white"
            : "border border-slate-200 bg-white text-slate-800"
        }`}
      >
        {text}
      </div>
    </div>
  );
}
