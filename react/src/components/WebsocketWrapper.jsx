import { useEffect } from "react";
import { socket } from "../socket/socketio.jsx";

export default function WebSocketWrapper({ children }) {
  useEffect(() => {
    if (!socket.connected) {
      socket.connect();
    }

    socket.on("connect", () => {
      console.debug("[socket] connected", socket.id);
    });

    socket.on("disconnect", (reason) => {
      console.debug("[socket] disconnected:", reason);
    });

    socket.on("connect_error", (err) => {
      console.error("[socket] connection error:", err.message);
    });

    return () => {
      socket.off("connect");
      socket.off("disconnect");
      socket.off("connect_error");
    };
  }, []);

  return children;
}