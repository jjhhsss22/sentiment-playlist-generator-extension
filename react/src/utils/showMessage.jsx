let messageTimeout;

export const showMessage = (setter, message, persist = false, duration = 3000) => {
  if (persist) {
    sessionStorage.setItem("flashType", setter);
    sessionStorage.setItem("flashMessage", message);
    return;
  }

  if (messageTimeout) clearTimeout(messageTimeout);  // Clear any pending timeout before setting a new one

  setter(message);
  messageTimeout = setTimeout(() => setter(""), duration);
};