"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "@/context/AuthContext";
import { useDataset } from "@/context/DatasetContext";

import ChatWindow from "@/components/chatbot/ChatWindow";
import ChatSidebar from "@/components/chatbot/ChatSidebar";
import { useCredits } from "@/context/CreditsContext";
import {
  sendChatMessage,
  createChatSession,
  fetchChatHistory,
  fetchChatSessions,
} from "@/lib/chatApi";

export default function ChatbotPage() {
  const { user, loading } = useAuth();
  const { activeDataset } = useDataset();
  const { credits } = useCredits();
  const router = useRouter();

  const [sessions, setSessions] = useState([]);
  const [sessionId, setSessionId] = useState(null);

  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [lastResponse, setLastResponse] = useState(null);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");

  // Auth protection
  useEffect(() => {
    if (!loading && !user) router.push("/login");
  }, [user, loading]);

  // Load sessions whenever dataset changes
  useEffect(() => {
    const loadSessions = async () => {
      if (!activeDataset) return;

      try {
        const data = await fetchChatSessions(activeDataset.id);
        setSessions(data);

        // Auto select first session if exists
        if (data.length > 0) {
          setSessionId(data[0].id);
        } else {
          // create new session
          const newSession = await createChatSession(activeDataset.id);
          setSessionId(newSession.session_id);

          const updatedSessions = await fetchChatSessions(activeDataset.id);
          setSessions(updatedSessions);
        }
      } catch (err) {
        setError("Failed to load sessions");
      }
    };

    loadSessions();
  }, [activeDataset]);

  // Load history when session selected
  useEffect(() => {
    const loadHistory = async () => {
      if (!sessionId) return;

      try {
        const history = await fetchChatHistory(sessionId);

        const formatted = history.map((msg) => ({
          role: msg.sender,
          text: msg.message_text,
        }));

        setMessages(formatted);
      } catch (err) {
        setError("Failed to load history");
      }
    };

    loadHistory();
  }, [sessionId]);

  const handleSend = async () => {
    setError("");

    if (!activeDataset) {
      setError("No dataset selected.");
      return;
    }

    if (!query.trim()) {
      setError("Type a message first.");
      return;
    }

    if (!sessionId) {
      setError("Session not ready.");
      return;
    }

    setMessages((prev) => [...prev, { role: "user", text: query }]);
    setSending(true);

    try {
      const response = await sendChatMessage(activeDataset.id, {
        session_id: sessionId,
        question: query,
      });
      setLastResponse(response);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: response.answer || "I could not create an answer." },
      ]);

      setQuery("");
      setSending(false);
    } catch (err) {
      setError(err?.response?.data?.detail || "Chat failed");
      setSending(false);
    }
  };

  const handleSelectSession = (id) => {
    setSessionId(id);
    setMessages([]);
    setLastResponse(null);
  };

  const handleNewChat = async () => {
    if (!activeDataset) return;

    try {
      const newSession = await createChatSession(activeDataset.id);
      setSessionId(newSession.session_id);

      const updatedSessions = await fetchChatSessions(activeDataset.id);
      setSessions(updatedSessions);
    } catch (err) {
      setError("Failed to create new session");
    }
  };

  if (loading) return <p className="p-4">Loading...</p>;
  if (!user) return null;

  return (
    <div className="flex min-h-[calc(100vh-80px)] gap-5">
      <ChatSidebar
        sessions={sessions}
        activeSessionId={sessionId}
        onSelect={handleSelectSession}
        onNewChat={handleNewChat}
      />

      <div className="flex-1 min-w-0">
        <div className="mb-4 flex flex-col gap-4 rounded-lg border border-slate-200 bg-white p-5 shadow-sm md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-emerald-600">
              RAG + SQL + Prediction
            </p>
            <h1 className="mt-1 text-2xl font-bold text-slate-950">AI Chatbot</h1>
            <p className="mt-1 text-sm text-slate-500">
              Dataset: <span className="font-semibold text-slate-800">{activeDataset ? activeDataset.dataset_name : "None"}</span>
            </p>
          </div>
          <div className="rounded-md border border-slate-200 px-3 py-2 text-sm font-semibold text-slate-700">
            Credits: {credits}
          </div>
        </div>

        {error && <p className="mb-3 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}
        {credits <= 0 && (
          <p className="mb-3 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
            You have no credits. Please buy credits to continue.
          </p>
        )}

        <ChatWindow
          messages={messages}
          lastResponse={lastResponse}
        />

        <div className="mt-4 flex gap-2 rounded-lg border border-slate-200 bg-white p-2 shadow-sm">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) handleSend();
            }}
            placeholder="Ask something..."
            className="min-w-0 flex-1 rounded-md border border-transparent px-3 py-2 outline-none focus:border-slate-300"
          />

          <button
            onClick={handleSend}
            disabled={sending || credits <= 0}
            className="rounded-md bg-slate-950 px-5 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            {sending ? "Thinking..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}
