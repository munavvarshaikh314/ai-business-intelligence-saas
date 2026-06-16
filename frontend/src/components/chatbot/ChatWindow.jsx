"use client";

import { useEffect, useRef } from "react";
import { getToken } from "@/lib/auth";
import MessageBubble from "./MessageBubble";
import SourceViewer from "./SourceViewer";
import SQLTableViewer from "./SQLTableViewer";
import MLResultViewer from "./MLResultViewer";
import AutoChart from "./AutoChart";
import AIInsightCard from "./AIInsightCard";
import KPIViewer from "./KPIViewer";

export default function ChatWindow({ messages, lastResponse, sessionId }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, lastResponse]);

  const exportChat = async () => {
    if (!sessionId) return;
    try {
      const token = getToken();
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/chatbot/export/pdf/${sessionId}`,
        { method: "POST", headers: { Authorization: `Bearer ${token}` } }
      );
      if (!res.ok) { alert("Export failed. Please try again."); return; }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `chat_export_${sessionId.slice(0, 8)}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      alert("Export failed. Please try again.");
    }
  };

  const queryType = lastResponse?.query_type;

  return (
    <div className="flex flex-col rounded-lg border border-slate-200 bg-slate-50 shadow-inner">

      {/* Toolbar */}
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-2">
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
          Chat
        </span>
        {messages.length > 0 && sessionId && (
          <button
            onClick={exportChat}
            className="flex items-center gap-1.5 rounded-md border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-600 transition hover:border-slate-300 hover:bg-slate-50"
          >
            ↓ Export PDF
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="h-[480px] overflow-y-auto p-4">
        {messages.length === 0 ? (
          <div className="flex h-full items-center justify-center text-center">
            <div>
              <p className="text-lg font-semibold text-slate-800">Ask your first question</p>
              <p className="mt-1 text-sm text-slate-500">
                Try revenue summaries, document questions, or prediction prompts.
              </p>
            </div>
          </div>
        ) : (
          <>
            {messages.map((m, idx) => {
  const isLastMessage = idx === messages.length - 1;

  const hidePredictionAssistantMessage =
    queryType === "PREDICTION" &&
    m.role === "assistant" &&
    isLastMessage;

  if (hidePredictionAssistantMessage) {
    return null;
  }

  const hideSqlAssistantMessage =
  queryType === "SQL" &&
  m.role === "assistant" &&
  isLastMessage;

if (hideSqlAssistantMessage) {
  return null;
}

  return (
    <MessageBubble
      key={idx}
      role={m.role}
      text={m.text}
    />
  );
})}

            {/* Result viewers — shown below last AI message */}
            {lastResponse && queryType === "RAG" && (
              <SourceViewer sources={lastResponse.sources} />
            )}

            {lastResponse && queryType === "SQL" && (
  <>
    <AIInsightCard
      insight={lastResponse.insight}
    />

    <KPIViewer kpis={lastResponse.kpis} />

    <AutoChart
  data={lastResponse.data}
  title={lastResponse.chart_title}
/>

    <SQLTableViewer
      data={lastResponse.data}
    />
  </>
)}
            {lastResponse && queryType === "PREDICTION" && (
              <MLResultViewer result={lastResponse} />
            )}
          </>
        )}

        {lastResponse?.empty_result && (
  <div className="mt-3 rounded-xl border border-amber-200 bg-amber-50 p-4">
    <h3 className="font-semibold text-amber-700">
      No Matching Results
    </h3>

    <p className="mt-2 text-sm text-slate-600">
      No records matched the conditions in your query.
    </p>

    <div className="mt-3 text-sm text-slate-500">
      Try:
      <ul className="mt-1 list-disc pl-5">
        <li>Show top products</li>
        <li>Show category averages</li>
        <li>Compare categories</li>
      </ul>
    </div>
  </div>
)}

        <div ref={bottomRef} />
      </div>
    </div>
  );
}

// "use client";

// import { useEffect, useRef, useState } from "react";
// import MessageBubble from "./MessageBubble";
// import SourceViewer from "./SourceViewer";
// import SQLTableViewer from "./SQLTableViewer";
// import MLResultViewer from "./MLResultViewer";

// export default function ChatWindow({ messages, lastResponse }) {
//   const bottomRef = useRef(null);

//   useEffect(() => {
//     bottomRef.current?.scrollIntoView({ behavior: "smooth" });
//   }, [messages, lastResponse]);

//   const exportChat = async () => {
//   const token = getToken();
//   const res = await fetch(
//     `${process.env.NEXT_PUBLIC_API_URL}/chatbot/export/pdf/${sessionId}`,
//     { method: "POST", headers: { Authorization: `Bearer ${token}` } }
//   );
//   const blob = await res.blob();
//   const url = URL.createObjectURL(blob);
//   const a = document.createElement("a");
//   a.href = url;
//   a.download = "chat_export.pdf";
//   a.click();
// };

//   return (
//     <div className="h-[560px] overflow-y-auto rounded-lg border border-slate-200 bg-slate-50 p-4 shadow-inner">
//       {messages.length === 0 ? (
//         <div className="flex h-full items-center justify-center text-center">
//           <div>
//             <p className="text-lg font-semibold text-slate-800">Ask your first question</p>
//             <p className="mt-1 text-sm text-slate-500">Try revenue summaries, document questions, or prediction prompts.</p>
//           </div>
//           <button onClick={exportChat} className="rounded-md border border-slate-200 px-3 py-2 text-xs text-slate-600 hover:bg-slate-50">
//   Export PDF
// </button>
//         </div>
//       ) : (
//         messages.map((m, idx) => (
//           <MessageBubble key={idx} role={m.role} text={m.text} />
//         ))
//       )}

//       {/* Render last AI response type */}
//       {lastResponse?.type === "RAG" && (
//         <SourceViewer sources={lastResponse.sources} />
//       )}

//       {lastResponse?.type === "SQL" && (
//         <SQLTableViewer data={lastResponse.response} />
//       )}

//       {lastResponse?.type === "ML" && (
//         <MLResultViewer result={lastResponse.response} />
//       )}

//       <div ref={bottomRef} />
//     </div>
//   );
// }
