"use client";

import { useEffect, useRef, useState } from "react";
import MessageBubble from "./MessageBubble";
import SourceViewer from "./SourceViewer";
import SQLTableViewer from "./SQLTableViewer";
import MLResultViewer from "./MLResultViewer";

export default function ChatWindow({ messages, lastResponse }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, lastResponse]);

  return (
    <div className="h-[560px] overflow-y-auto rounded-lg border border-slate-200 bg-slate-50 p-4 shadow-inner">
      {messages.length === 0 ? (
        <div className="flex h-full items-center justify-center text-center">
          <div>
            <p className="text-lg font-semibold text-slate-800">Ask your first question</p>
            <p className="mt-1 text-sm text-slate-500">Try revenue summaries, document questions, or prediction prompts.</p>
          </div>
        </div>
      ) : (
        messages.map((m, idx) => (
          <MessageBubble key={idx} role={m.role} text={m.text} />
        ))
      )}

      {/* Render last AI response type */}
      {lastResponse?.type === "RAG" && (
        <SourceViewer sources={lastResponse.sources} />
      )}

      {lastResponse?.type === "SQL" && (
        <SQLTableViewer data={lastResponse.response} />
      )}

      {lastResponse?.type === "ML" && (
        <MLResultViewer result={lastResponse.response} />
      )}

      <div ref={bottomRef} />
    </div>
  );
}
