import { navTo } from "./navigate";
import { showMessage } from "./showMessage.jsx"

export async function handleLogout() {
  await fetch("/api/logout", {
    method: "POST",
    credentials: "include"
  });

  showMessage("success", "You have been successfully logged out.", true);

  navTo("/login");
}