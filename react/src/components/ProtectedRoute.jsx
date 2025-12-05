import { Navigate } from "react-router-dom";
import { useEffect, useState } from "react";
import api from "../utils/axios.jsx";

export default function ProtectedRoute({ children }) {
  const [valid, setValid] = useState(null);

  useEffect(() => {
    async function check() {
      try {
        const { data } = await api.get("/verify"); // GET request to verify JWT
        if (data?.user_id) {
          setValid(true);
        } else {
          setValid(false);
        }
      } catch (err) {
        console.error("JWT validation failed:", err);
        setValid(false); // Axios interceptor already handles 401 redirect
      }
    }

    check();
  }, []);

  if (valid === null) return <div>Loading...</div>;

  if (valid === false) return <Navigate to="/login" replace />;

  return children;
}