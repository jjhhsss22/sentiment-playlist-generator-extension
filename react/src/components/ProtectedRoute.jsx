import { Navigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { fetchContent } from "../utils/fetchContent";
import { showMessage } from "../utils/showMessage.jsx";

export default function ProtectedRoute({ children }) {
  const [valid, setValid] = useState(null);

  useEffect(() => {
    async function check() {
      const data = await fetchContent("/validate");
      if (data?.user_id) setValid(true);
      else setValid(false);
    }
    check();
  }, []);

  if (valid === null) return <div>Loading...</div>;

  if (valid === false) return <Navigate to="/login" replace />;

  return children;
}