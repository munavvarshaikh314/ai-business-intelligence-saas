"use client";
import { useEffect, useState } from "react";
import { getToken } from "@/lib/auth";

export default function SuggestedQuestions({ datasetId, onSelect }) {
  const [questions, setQuestions] = useState([]);

  useEffect(() => {
    if (!datasetId) return;
    const token = getToken();
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/chatbot/onboarding/suggested-questions/${datasetId}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(r => r.json())
      .then(data => setQuestions(data.suggested_questions || []))
      .catch(() => {});
  }, [datasetId]);

  if (!questions.length) return null;

  return (
    <div className="flex flex-wrap gap-2 px-2 pb-2">
      {questions.map((q, i) => (
        <button
          key={i}
          onClick={() => onSelect(q)}
          className="rounded-full border border-slate-200 bg-white px-3 py-1 text-xs text-slate-600 hover:border-emerald-400 hover:text-emerald-700 transition"
        >
          {q}
        </button>
      ))}
    </div>
  );
}