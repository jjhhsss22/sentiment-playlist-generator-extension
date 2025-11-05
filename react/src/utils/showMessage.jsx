export const showMessage = (setter, message, duration = 3000) => {

  setter(message);
  setTimeout(() => setter(""), duration);

};