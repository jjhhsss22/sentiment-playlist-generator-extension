let globalNavigate = null;

export function setNavigate(navigateFn) {
  globalNavigate = navigateFn;
}

export function navTo(path) {
  if (globalNavigate) globalNavigate(path);
  else window.location.href = path;
}