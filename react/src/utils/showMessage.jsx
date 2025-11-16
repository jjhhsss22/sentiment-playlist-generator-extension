export const showMessage = (setter, message, persist = false, duration = 3000) => {
  if (persist) {
    sessionStorage.setItem("setter", setter);
    sessionStorage.setItem("flashMessage", message);
    return;
  }

  setter(message);
  setTimeout(() => setter(""), duration);

};