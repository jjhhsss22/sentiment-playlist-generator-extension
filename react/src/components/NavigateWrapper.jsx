import { useNavigate } from "react-router-dom";
import { useEffect } from "react";
import { setNavigate } from "../utils/navigate";

export default function AppWrapper({ children }) {
  const navigate = useNavigate();
  setNavigate(navigate); // store navigate globally once

  useEffect(() => {
    if (window.location.pathname.startsWith("/api")) {
      navigate("/unknown");
    }
  }, [navigate]);

  return children;
}