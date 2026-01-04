import { useEffect, useState } from "react";
import { socket } from "./socketio.jsx";

export function getPlaylistTask(requestId) {
  const [status, setStatus] = useState("idle");
  const [result, setResult] = useState(null);

  useEffect(() => {
    if (!requestId) return;

    setStatus("processing");

    const handleUpdate = (payload) => {
      if (payload.request_id !== requestId) return;

      setStatus(payload.status);

      if (payload.status === "done") {
        setResult(payload.result);
      }
    };

    socket.on("playlist_update", handleUpdate);

    return () => {
      socket.off("playlist_update", handleUpdate);
    };
  }, [requestId]);

  return { status, result };
}
