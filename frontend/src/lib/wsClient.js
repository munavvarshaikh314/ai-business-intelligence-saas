export const connectChatSocket = (datasetId, sessionId, onMessage, onError) => {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
  const wsUrl = apiUrl
    .replace(/^http/, "ws")
    .replace(/\/api\/v1\/?$/, `/ws/chat/${datasetId}/${sessionId}`);

  const socket = new WebSocket(wsUrl);

  socket.onmessage = (event) => {
    try {
      onMessage(JSON.parse(event.data));
    } catch {
      onMessage({ type: "token", data: event.data });
    }
  };

  socket.onerror = onError;
  return socket;
};
