export const connectChatSocket = (sessionId, onMessage, onError) => {
  const WS_BASE =
    process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws/chat";

  const socket = new WebSocket(`${WS_BASE}/${sessionId}`);

  socket.onopen = () => {
    console.log("WebSocket connected");
  };

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      if (onMessage) onMessage(data);
    } catch (err) {
      console.log("Invalid WS message", event.data);
    }
  };

  socket.onerror = (err) => {
    console.log("WebSocket error", err);
    if (onError) onError(err);
  };

  socket.onclose = () => {
    console.log("WebSocket closed");
  };

  return socket;
};