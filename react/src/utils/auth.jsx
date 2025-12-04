import api from "./axios.jsx";
import { navTo } from "./navigate";
import { showMessage } from "./showMessage.jsx"

export async function handleLogout() {

  const res = await api.post("/logout");

  if (res.status === 200) {
    showMessage("success", "You have been successfully logged out.", true);
    navTo("/login");
  }
}