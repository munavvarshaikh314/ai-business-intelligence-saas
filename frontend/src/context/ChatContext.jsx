"use client";

import { createContext, useContext, useState, useCallback } from "react";
import { sendChatMessage, createChatSession, fetchChatSessions, fetchChatHistory } from "@/lib/chatApi";

export const ChatContext = createContext();

export function ChatProvider({ children }) {
  const [sessions, setSessions] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [lastResponse, setLastResponse] = useState(null);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");

  const loadSessions = useCallback(async (datasetId) => {
    if (!datasetId) return;
    const data = await fetchChatSessions(datasetId);
    setSessions(data);
    return data;
  }, []);

  const selectSession = useCallback(async (id) => {
    setSessionId(id);
    setMessages([]);
    setLastResponse(null);
    if (!id) return;
    const history = await fetchChatHistory(id);
    const formatted = history.map((m) => ({ role: m.sender, text: m.message_text }));
    setMessages(formatted);
  }, []);

  const startNewSession = useCallback(async (datasetId) => {
    const newSession = await createChatSession(datasetId);
    setSessionId(newSession.session_id);
    setMessages([]);
    setLastResponse(null);
    const updated = await fetchChatSessions(datasetId);
    setSessions(updated);
    return newSession.session_id;
  }, []);

  const sendMessage = useCallback(async (datasetId, question) => {
    if (!question.trim() || !sessionId || !datasetId) return;
    setError("");
    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setSending(true);
    try {
      const response = await sendChatMessage(datasetId, { session_id: sessionId, question });
      setLastResponse(response);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: response.answer || "No answer returned." },
      ]);
    } catch (err) {
      setError(err?.response?.data?.detail || "Chat failed.");
    } finally {
      setSending(false);
    }
  }, [sessionId]);

  return (
    <ChatContext.Provider value={{
      sessions, sessionId, messages, lastResponse, sending, error,
      loadSessions, selectSession, startNewSession, sendMessage, setError,
    }}>
      {children}
    </ChatContext.Provider>
  );
}

export function useChat() {
  return useContext(ChatContext);
}
