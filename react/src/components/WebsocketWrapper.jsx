import { useEffect } from "react";
import { socket } from "../socket/socketio.jsx";

export default function WebSocketWrapper({ children }) {
  useEffect(() => {
    socket.connect();

    return () => {
      socket.disconnect();
    };
  }, []);

  return children;
}