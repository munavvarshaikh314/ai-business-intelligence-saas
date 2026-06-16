"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { useDataset } from "@/context/DatasetContext";
import { useCredits } from "@/context/CreditsContext";
import ChatWindow from "@/components/chatbot/ChatWindow";
import ChatSidebar from "@/components/chatbot/ChatSidebar";
import { sendChatMessage, createChatSession, fetchChatHistory, fetchChatSessions } from "@/lib/chatApi";
import { fetchUploadStatus } from "@/lib/uploadApi";
import { ChatErrors } from "@/lib/errors";

export default function ChatbotPage() {
  const { user, loading } = useAuth();
  const { activeDataset } = useDataset();
  const { credits } = useCredits();
  const router = useRouter();

  const [sessions, setSessions] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [query, setQuery] = useState("");
  const [chatMode, setChatMode] = useState("AUTO");
  const [messages, setMessages] = useState([]);
  const [lastResponse, setLastResponse] = useState(null);
  const [indexStatus, setIndexStatus] = useState(null);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!loading && !user) router.push("/login");
  }, [user, loading]);

  useEffect(() => {
    const loadSessions = async () => {
      if (!activeDataset) return;
      setError("");
      try {
        const data = await fetchChatSessions(activeDataset.id);
        setSessions(data);
        if (data.length > 0) {
          setSessionId(data[0].id);
        } else {
          const newSession = await createChatSession(activeDataset.id);
          setSessionId(newSession.session_id);
          const updated = await fetchChatSessions(activeDataset.id);
          setSessions(updated);
        }
      } catch (err) {
        setError(ChatErrors.session(err));
      }
    };
    loadSessions();
  }, [activeDataset]);

  useEffect(() => {
    let cancelled = false;
    let timer;
    const loadStatus = async () => {
      if (!activeDataset) { setIndexStatus(null); return; }
      try {
        const status = await fetchUploadStatus(activeDataset.id);
        if (!cancelled) setIndexStatus(status);
        if (!cancelled && ["QUEUED", "PROCESSING"].includes(status.status)) {
          timer = setTimeout(loadStatus, 3000);
        }
      } catch {
        if (!cancelled) setIndexStatus(null);
      }
    };
    loadStatus();
    return () => { cancelled = true; if (timer) clearTimeout(timer); };
  }, [activeDataset]);

  useEffect(() => {
    const loadHistory = async () => {
      if (!sessionId) return;
      try {
        const history = await fetchChatHistory(sessionId);
        setMessages(history.map((msg) => ({
          role: msg.sender,
          text: msg.message_text,
        })));
        setLastResponse(null);
      } catch (err) {
        setError(ChatErrors.history(err));
      }
    };
    loadHistory();
  }, [sessionId]);

  const handleSend = async () => {
    setError("");
    if (!activeDataset) { setError("No dataset selected."); return; }
    if (!query.trim()) { setError("Please type a message before sending."); return; }
    if (!sessionId) { setError("Chat session not ready. Please wait."); return; }
    if (credits <= 0) { setError("No credits remaining. Please purchase credits."); return; }
    if (["QUEUED", "PROCESSING"].includes(indexStatus?.status)) {
      setError(`PDF indexing still in progress. Please wait.`); return;
    }

    const userText = query;
    setMessages((prev) => [...prev, { role: "user", text: userText }]);
    setQuery("");
    setSending(true);
    setLastResponse(null);

    try {
      const response = await sendChatMessage(activeDataset.id, {
        session_id: sessionId,
        question: userText,
        mode: chatMode === "AUTO" ? undefined : chatMode,
      });

      // Store full response for result viewers
      setLastResponse(response);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: response.answer || "I wasn't able to generate an answer. Please try rephrasing.",
        },
      ]);
    } catch (err) {
      setError(ChatErrors.send(err));
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setSending(false);
    }
  };

  const handleSelectSession = (id) => {
    setSessionId(id);
    setMessages([]);
    setLastResponse(null);
    setError("");
  };

  const handleNewChat = async () => {
    if (!activeDataset) { setError("No dataset selected."); return; }
    setError("");
    try {
      const newSession = await createChatSession(activeDataset.id);
      setSessionId(newSession.session_id);
      setMessages([]);
      setLastResponse(null);
      const updated = await fetchChatSessions(activeDataset.id);
      setSessions(updated);
    } catch (err) {
      setError(ChatErrors.session(err));
    }
  };

  if (loading) return <p className="p-4 text-slate-500">Loading...</p>;
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
        {/* Header */}
        <div className="mb-4 flex flex-col gap-4 rounded-lg border border-slate-200 bg-white p-5 shadow-sm md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-emerald-600">
              RAG + SQL + Prediction
            </p>
            <h1 className="mt-1 text-2xl font-bold text-slate-950">AI Chatbot</h1>
            <p className="mt-1 text-sm text-slate-500">
              Dataset:{" "}
              <span className="font-semibold text-slate-800">
                {activeDataset ? activeDataset.dataset_name : "None selected"}
              </span>
            </p>
          </div>
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
            <select
              value={chatMode}
              onChange={(e) => setChatMode(e.target.value)}
              className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 outline-none focus:border-emerald-400"
            >
              <option value="AUTO">Auto</option>
              <option value="RAG">PDF / RAG</option>
              <option value="SQL">CSV / SQL</option>
              <option value="PREDICTION">Prediction</option>
            </select>
            <div className="rounded-md border border-slate-200 px-3 py-2 text-sm font-semibold text-slate-700">
              Credits: {credits}
            </div>
          </div>
        </div>

        {/* Alerts */}
        {!activeDataset && (
          <div className="mb-3 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
            No dataset selected. Please select a dataset from the sidebar.
          </div>
        )}
        {credits <= 0 && (
          <div className="mb-3 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
            No credits remaining.{" "}
            <a href="/dashboard/billing" className="underline font-semibold">Buy credits</a>
          </div>
        )}
        {["QUEUED", "PROCESSING"].includes(indexStatus?.status) && (
          <div className="mb-3 rounded-md border border-blue-200 bg-blue-50 px-3 py-2 text-sm text-blue-800">
            PDF indexing {indexStatus.status.toLowerCase()} ({indexStatus.progress || 0}%). Chat available when complete.
          </div>
        )}
        {indexStatus?.status === "FAILED" && (
          <div className="mb-3 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            PDF indexing failed. Please re-upload the PDF.
          </div>
        )}
        {error && (
          <div className="mb-3 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            {error}
          </div>
        )}

        {/* Chat — pass sessionId for export */}
        <ChatWindow
          messages={messages}
          lastResponse={lastResponse}
          sessionId={sessionId}
        />

        {/* Input */}
        <div className="mt-4 flex gap-2 rounded-lg border border-slate-200 bg-white p-2 shadow-sm">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) handleSend(); }}
            placeholder={activeDataset ? "Ask something about your data..." : "Select a dataset to start..."}
            disabled={!activeDataset || sending || ["QUEUED", "PROCESSING"].includes(indexStatus?.status)}
            className="min-w-0 flex-1 rounded-md border border-transparent px-3 py-2 outline-none focus:border-slate-300 disabled:bg-slate-50 disabled:text-slate-400"
          />
          <button
            onClick={handleSend}
            disabled={sending || credits <= 0 || !activeDataset || ["QUEUED", "PROCESSING"].includes(indexStatus?.status)}
            className="rounded-md bg-slate-950 px-5 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            {sending ? "Thinking..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}

// "use client";

// import { useEffect, useState } from "react";
// import { useRouter } from "next/navigation";
// import { useAuth } from "@/context/AuthContext";
// import { useDataset } from "@/context/DatasetContext";
// import { useCredits } from "@/context/CreditsContext";
// import ChatWindow from "@/components/chatbot/ChatWindow";
// import ChatSidebar from "@/components/chatbot/ChatSidebar";
// import { sendChatMessage, createChatSession, fetchChatHistory, fetchChatSessions } from "@/lib/chatApi";
// import { fetchUploadStatus } from "@/lib/uploadApi";
// import { ChatErrors } from "@/lib/errors";

// export default function ChatbotPage() {
//   const { user, loading } = useAuth();
//   const { activeDataset } = useDataset();
//   const { credits } = useCredits();
//   const router = useRouter();

//   const [sessions, setSessions] = useState([]);
//   const [sessionId, setSessionId] = useState(null);
//   const [query, setQuery] = useState("");
//   const [chatMode, setChatMode] = useState("AUTO");
//   const [messages, setMessages] = useState([]);
//   const [lastResponse, setLastResponse] = useState(null);
//   const [indexStatus, setIndexStatus] = useState(null);
//   const [sending, setSending] = useState(false);
//   const [error, setError] = useState("");

//   useEffect(() => {
//     if (!loading && !user) router.push("/login");
//   }, [user, loading]);

//   useEffect(() => {
//     const loadSessions = async () => {
//       if (!activeDataset) return;
//       setError("");
//       try {
//         const data = await fetchChatSessions(activeDataset.id);
//         setSessions(data);
//         if (data.length > 0) {
//           setSessionId(data[0].id);
//         } else {
//           const newSession = await createChatSession(activeDataset.id);
//           setSessionId(newSession.session_id);
//           const updated = await fetchChatSessions(activeDataset.id);
//           setSessions(updated);
//         }
//       } catch (err) {
//         setError(ChatErrors.session(err));
//       }
//     };
//     loadSessions();
//   }, [activeDataset]);

//   useEffect(() => {
//     let cancelled = false;
//     let timer;

//     const loadStatus = async () => {
//       if (!activeDataset) {
//         setIndexStatus(null);
//         return;
//       }

//       try {
//         const status = await fetchUploadStatus(activeDataset.id);
//         if (!cancelled) setIndexStatus(status);

//         if (!cancelled && ["QUEUED", "PROCESSING"].includes(status.status)) {
//           timer = setTimeout(loadStatus, 3000);
//         }
//       } catch {
//         if (!cancelled) setIndexStatus(null);
//       }
//     };

//     loadStatus();

//     return () => {
//       cancelled = true;
//       if (timer) clearTimeout(timer);
//     };
//   }, [activeDataset]);

//   useEffect(() => {
//     const loadHistory = async () => {
//       if (!sessionId) return;
//       try {
//         const history = await fetchChatHistory(sessionId);
//         setMessages(history.map((msg) => ({
//           role: msg.sender,
//           text: msg.message_text,
//         })));
//       } catch (err) {
//         setError(ChatErrors.history(err));
//       }
//     };
//     loadHistory();
//   }, [sessionId]);

//   const handleSend = async () => {
//     setError("");

//     if (!activeDataset) {
//       setError("No dataset selected. Please select or create a dataset first.");
//       return;
//     }
//     if (!query.trim()) {
//       setError("Please type a message before sending.");
//       return;
//     }
//     if (!sessionId) {
//       setError("Chat session is not ready. Please wait a moment and try again.");
//       return;
//     }
//     if (credits <= 0) {
//       setError("You have no credits remaining. Please purchase credits to continue.");
//       return;
//     }
//     if (["QUEUED", "PROCESSING"].includes(indexStatus?.status)) {
//       setError(`PDF indexing is still ${indexStatus.status.toLowerCase()} (${indexStatus.progress || 0}%). Please wait a little longer.`);
//       return;
//     }
//     if (indexStatus?.status === "FAILED") {
//       setError("PDF indexing failed. Please upload the PDF again or try another readable PDF.");
//       return;
//     }

//     setMessages((prev) => [...prev, { role: "user", text: query }]);
//     setQuery("");
//     setSending(true);

//     try {
//       const response = await sendChatMessage(activeDataset.id, {
//         session_id: sessionId,
//         question: query,
//         mode: chatMode === "AUTO" ? undefined : chatMode,
//       });
//       setLastResponse(response);
//       setMessages((prev) => [
//         ...prev,
//         {
//           role: "assistant",
//           text: response.answer || "I wasn't able to generate an answer. Please try rephrasing your question.",
//         },
//       ]);
//     } catch (err) {
//       setError(ChatErrors.send(err));
//       // Remove the optimistic user message on failure
//       setMessages((prev) => prev.slice(0, -1));
//     } finally {
//       setSending(false);
//     }
//   };

//   const handleSelectSession = (id) => {
//     setSessionId(id);
//     setMessages([]);
//     setLastResponse(null);
//     setError("");
//   };

//   const handleNewChat = async () => {
//     if (!activeDataset) {
//       setError("No dataset selected.");
//       return;
//     }
//     setError("");
//     try {
//       const newSession = await createChatSession(activeDataset.id);
//       setSessionId(newSession.session_id);
//       setMessages([]);
//       setLastResponse(null);
//       const updated = await fetchChatSessions(activeDataset.id);
//       setSessions(updated);
//     } catch (err) {
//       setError(ChatErrors.session(err));
//     }
//   };

//   if (loading) return <p className="p-4 text-slate-500">Loading...</p>;
//   if (!user) return null;

//   return (
//     <div className="flex min-h-[calc(100vh-80px)] gap-5">
//       <ChatSidebar
//         sessions={sessions}
//         activeSessionId={sessionId}
//         onSelect={handleSelectSession}
//         onNewChat={handleNewChat}
//       />

//       <div className="flex-1 min-w-0">
//         <div className="mb-4 flex flex-col gap-4 rounded-lg border border-slate-200 bg-white p-5 shadow-sm md:flex-row md:items-center md:justify-between">
//           <div>
//             <p className="text-xs font-semibold uppercase tracking-wide text-emerald-600">
//               RAG + SQL + Prediction
//             </p>
//             <h1 className="mt-1 text-2xl font-bold text-slate-950">AI Chatbot</h1>
//             <p className="mt-1 text-sm text-slate-500">
//               Dataset:{" "}
//               <span className="font-semibold text-slate-800">
//                 {activeDataset ? activeDataset.dataset_name : "None selected"}
//               </span>
//             </p>
//           </div>
//           <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
//             <select
//               value={chatMode}
//               onChange={(e) => setChatMode(e.target.value)}
//               className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 outline-none focus:border-emerald-400"
//             >
//               <option value="AUTO">Auto</option>
//               <option value="RAG">PDF / RAG</option>
//               <option value="SQL">CSV / SQL</option>
//               <option value="PREDICTION">Prediction</option>
//             </select>
//             <div className="rounded-md border border-slate-200 px-3 py-2 text-sm font-semibold text-slate-700">
//               Credits: {credits}
//             </div>
//           </div>
//         </div>

//         {!activeDataset && (
//           <div className="mb-3 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
//             No dataset selected. Please select a dataset from the sidebar to start chatting.
//           </div>
//         )}

//         {credits <= 0 && (
//           <div className="mb-3 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
//             You have no credits remaining.{" "}
//             <a href="/dashboard/billing" className="underline font-semibold">Buy credits</a>{" "}
//             to continue using the chatbot.
//           </div>
//         )}

//         {["QUEUED", "PROCESSING"].includes(indexStatus?.status) && (
//           <div className="mb-3 rounded-md border border-blue-200 bg-blue-50 px-3 py-2 text-sm text-blue-800">
//             PDF indexing is {indexStatus.status.toLowerCase()} ({indexStatus.progress || 0}%). Chat will be available when indexing reaches 100%.
//           </div>
//         )}

//         {indexStatus?.status === "FAILED" && (
//           <div className="mb-3 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
//             PDF indexing failed. Please upload the PDF again or use another readable PDF.
//           </div>
//         )}

//         {error && (
//           <div className="mb-3 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
//             {error}
//           </div>
//         )}

//         <ChatWindow messages={messages} lastResponse={lastResponse} />

//         <div className="mt-4 flex gap-2 rounded-lg border border-slate-200 bg-white p-2 shadow-sm">
//           <input
//             value={query}
//             onChange={(e) => setQuery(e.target.value)}
//             onKeyDown={(e) => {
//               if (e.key === "Enter" && !e.shiftKey) handleSend();
//             }}
//             placeholder={activeDataset ? "Ask something about your data..." : "Select a dataset to start..."}
//             disabled={!activeDataset || sending || ["QUEUED", "PROCESSING"].includes(indexStatus?.status)}
//             className="min-w-0 flex-1 rounded-md border border-transparent px-3 py-2 outline-none focus:border-slate-300 disabled:bg-slate-50 disabled:text-slate-400"
//           />
//           <button
//             onClick={handleSend}
//             disabled={sending || credits <= 0 || !activeDataset || ["QUEUED", "PROCESSING"].includes(indexStatus?.status)}
//             className="rounded-md bg-slate-950 px-5 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:bg-slate-300"
//           >
//             {sending ? "Thinking..." : "Send"}
//           </button>
//         </div>
//       </div>
//     </div>
//   );
// }


// "use client";

// import { useEffect, useState } from "react";
// import { useRouter } from "next/navigation";

// import { useAuth } from "@/context/AuthContext";
// import { useDataset } from "@/context/DatasetContext";

// import ChatWindow from "@/components/chatbot/ChatWindow";
// import ChatSidebar from "@/components/chatbot/ChatSidebar";
// import { useCredits } from "@/context/CreditsContext";
// import {
//   sendChatMessage,
//   createChatSession,
//   fetchChatHistory,
//   fetchChatSessions,
// } from "@/lib/chatApi";

// export default function ChatbotPage() {
//   const { user, loading } = useAuth();
//   const { activeDataset } = useDataset();
//   const { credits } = useCredits();
//   const router = useRouter();

//   const [sessions, setSessions] = useState([]);
//   const [sessionId, setSessionId] = useState(null);

//   const [query, setQuery] = useState("");
//   const [messages, setMessages] = useState([]);
//   const [lastResponse, setLastResponse] = useState(null);
//   const [sending, setSending] = useState(false);
//   const [error, setError] = useState("");

//   // Auth protection
//   useEffect(() => {
//     if (!loading && !user) router.push("/login");
//   }, [user, loading]);

//   // Load sessions whenever dataset changes
//   useEffect(() => {
//     const loadSessions = async () => {
//       if (!activeDataset) return;

//       try {
//         const data = await fetchChatSessions(activeDataset.id);
//         setSessions(data);

//         // Auto select first session if exists
//         if (data.length > 0) {
//           setSessionId(data[0].id);
//         } else {
//           // create new session
//           const newSession = await createChatSession(activeDataset.id);
//           setSessionId(newSession.session_id);

//           const updatedSessions = await fetchChatSessions(activeDataset.id);
//           setSessions(updatedSessions);
//         }
//       } catch (err) {
//         setError("Failed to load sessions");
//       }
//     };

//     loadSessions();
//   }, [activeDataset]);

//   // Load history when session selected
//   useEffect(() => {
//     const loadHistory = async () => {
//       if (!sessionId) return;

//       try {
//         const history = await fetchChatHistory(sessionId);

//         const formatted = history.map((msg) => ({
//           role: msg.sender,
//           text: msg.message_text,
//         }));

//         setMessages(formatted);
//       } catch (err) {
//         setError("Failed to load history");
//       }
//     };

//     loadHistory();
//   }, [sessionId]);

//   const handleSend = async () => {
//     setError("");

//     if (!activeDataset) {
//       setError("No dataset selected.");
//       return;
//     }

//     if (!query.trim()) {
//       setError("Type a message first.");
//       return;
//     }

//     if (!sessionId) {
//       setError("Session not ready.");
//       return;
//     }

//     setMessages((prev) => [...prev, { role: "user", text: query }]);
//     setSending(true);

//     try {
//       const response = await sendChatMessage(activeDataset.id, {
//         session_id: sessionId,
//         question: query,
//       });
//       setLastResponse(response);
//       setMessages((prev) => [
//         ...prev,
//         { role: "assistant", text: response.answer || "I could not create an answer." },
//       ]);

//       setQuery("");
//       setSending(false);
//     } catch (err) {
//       setError(err?.response?.data?.detail || "Chat failed");
//       setSending(false);
//     }
//   };

//   const handleSelectSession = (id) => {
//     setSessionId(id);
//     setMessages([]);
//     setLastResponse(null);
//   };

//   const handleNewChat = async () => {
//     if (!activeDataset) return;

//     try {
//       const newSession = await createChatSession(activeDataset.id);
//       setSessionId(newSession.session_id);

//       const updatedSessions = await fetchChatSessions(activeDataset.id);
//       setSessions(updatedSessions);
//     } catch (err) {
//       setError("Failed to create new session");
//     }
//   };

//   if (loading) return <p className="p-4">Loading...</p>;
//   if (!user) return null;

//   return (
//     <div className="flex min-h-[calc(100vh-80px)] gap-5">
//       <ChatSidebar
//         sessions={sessions}
//         activeSessionId={sessionId}
//         onSelect={handleSelectSession}
//         onNewChat={handleNewChat}
//       />

//       <div className="flex-1 min-w-0">
//         <div className="mb-4 flex flex-col gap-4 rounded-lg border border-slate-200 bg-white p-5 shadow-sm md:flex-row md:items-center md:justify-between">
//           <div>
//             <p className="text-xs font-semibold uppercase tracking-wide text-emerald-600">
//               RAG + SQL + Prediction
//             </p>
//             <h1 className="mt-1 text-2xl font-bold text-slate-950">AI Chatbot</h1>
//             <p className="mt-1 text-sm text-slate-500">
//               Dataset: <span className="font-semibold text-slate-800">{activeDataset ? activeDataset.dataset_name : "None"}</span>
//             </p>
//           </div>
//           <div className="rounded-md border border-slate-200 px-3 py-2 text-sm font-semibold text-slate-700">
//             Credits: {credits}
//           </div>
//         </div>

//         {error && <p className="mb-3 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}
//         {credits <= 0 && (
//           <p className="mb-3 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
//             You have no credits. Please buy credits to continue.
//           </p>
//         )}

//         <ChatWindow
//           messages={messages}
//           lastResponse={lastResponse}
//         />

//         <div className="mt-4 flex gap-2 rounded-lg border border-slate-200 bg-white p-2 shadow-sm">
//           <input
//             value={query}
//             onChange={(e) => setQuery(e.target.value)}
//             onKeyDown={(e) => {
//               if (e.key === "Enter" && !e.shiftKey) handleSend();
//             }}
//             placeholder="Ask something..."
//             className="min-w-0 flex-1 rounded-md border border-transparent px-3 py-2 outline-none focus:border-slate-300"
//           />

//           <button
//             onClick={handleSend}
//             disabled={sending || credits <= 0}
//             className="rounded-md bg-slate-950 px-5 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:bg-slate-300"
//           >
//             {sending ? "Thinking..." : "Send"}
//           </button>
//         </div>
//       </div>
//     </div>
//   );
// }
