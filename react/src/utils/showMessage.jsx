export const showMessage = (setter, message, persist = false, duration = 3000) => {
  if (persist) {
    sessionStorage.setItem("flashType", setter);
    sessionStorage.setItem("flashMessage", message);
    return;
  }

  setter(message);
  setTimeout(() => setter(""), duration);
};