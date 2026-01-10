import { useEffect, useState } from "react";
import { socket } from "./socketio.jsx";

export function getPlaylistProgress(requestId) {
  const [steps, setSteps] = useState([]);

  useEffect(() => {
    if (!requestId) return;

    const handleUpdate = (payload) => {
      if (payload.request_id !== requestId) return;

      setSteps(prev => [...prev, payload.step]);
    };

    socket.on("playlist_progress", handleUpdate);

    return () => {
      socket.off("playlist_progress");
    };
  }, [requestId]);

  return steps;
}
