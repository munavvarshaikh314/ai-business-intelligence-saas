import api from "@/lib/api";

export const createChatSession = async (datasetId) => {
  const res = await api.post(`/chatbot/session/${datasetId}`, {
    session_name: "New Chat",
  });
  return res.data;
};

export const sendChatMessage = async (datasetId, payload) => {
  const res = await api.post(`/chatbot/ask/${datasetId}`, payload, {
    timeout: 120000,
  });
  return res.data;
}; 

export const fetchChatHistory = async (sessionId) => {
  const res = await api.get(`/chatbot/messages/${sessionId}`);
  return res.data;
};

export const fetchChatSessions = async (datasetId) => {
  const res = await api.get(`/chatbot/sessions/${datasetId}`);
  return res.data;
};
