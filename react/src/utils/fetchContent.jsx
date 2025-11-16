import { useNavigate } from "react-router-dom";
import { showMessage } from "./showMessage.jsx";

export async function fetchContent(url, options = {}) {
  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),          // merge any additional headers
      },
      credentials: "include", // always include cookies
    });

    const data = await res.json().catch(() => null);  // Try parsing JSON, fallback to null if invalid

    if (res.status === 401) {
      console.warn("JWT Error:", data);

      showMessage("general", data?.message || "Failed to authenticate user. Please try again", true);

      if (data.location) {
        navigate(data.location);
      } else {
        navigate("/login");
      }

      return null;
    }

    if (!res.ok) throw new Error(data?.message || "server error");

    return data
  } catch (err) {
    console.error("Fetch error:", err);
    return { success: false, message: err };
  }
}