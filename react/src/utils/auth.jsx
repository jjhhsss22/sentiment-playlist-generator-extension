import { navTo } from "./navigate";
import { showMessage } from "./showMessage.jsx"

export async function handleLogout() {

  const res = await fetch("/api/logout", {
    method: "POST",
    credentials: "include"
  });

  if (res.status === 200) {
    showMessage("success", "You have been successfully logged out.", true);
    navTo("/login");
  }
}