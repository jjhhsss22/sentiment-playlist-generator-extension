import { useNavigate } from "react-router-dom";
import { showMessage } from "./showMessage.jsx"

export async function handleLogout() {
  await fetch("/logout", {
    method: "POST",
    credentials: "include"
  });
  showMessage("success", "You have been successfully logged out.", true);

  navigate("/login");
}