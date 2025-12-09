import api from "./axios.jsx";
import { showMessage } from "./showMessage.jsx"

export async function handleLogout(onSuccess, onError) {
  try {
    const res = await api.post("/logout");

    if (res.status === 200) {
      onSuccess();
    }

  } catch (err) {
    onError("Logout failed. Please try again.");
  }
}