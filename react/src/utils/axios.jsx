import axios from "axios";
import { navTo } from "./navigate";
import { showMessage } from "./showMessage";

const api = axios.create({
  baseURL: "/api",     // Every call becomes /api/...
  withCredentials: true,
  headers: { "Content-Type": "application/json",
             "X-Requested-With": "ReactApp"},
});

// Automatically attach CSRF token from cookie for state-changing requests
//CSRF tokens prevent attackers from forcing authenticated users to make a request to a trusted site
api.interceptors.request.use((config) => {
  if (["post", "put", "patch", "delete"].includes(config.method)) {
    const csrfToken = document.cookie
      .split("; ")
      .find(row => row.startsWith("csrf_access_token="))
      ?.split("=")[1];

    if (csrfToken) {
      config.headers["X-CSRF-TOKEN"] = csrfToken;
    }
  }
  return config;
});

// global response interceptor
api.interceptors.response.use(
  (response) => response,

  (error) => {
    const res = error.response;

    if (!res) {
      return Promise.reject(error);
    }

    if (res.status === 401 && res.data?.jwt === "invalid") {
      showMessage("general", res.data.message || "Session expired", true);

      const redirect = res.data.location || "/login";
      navTo(redirect);
      return Promise.reject(error);
    }

    return Promise.reject(error);
  }
);

export default api;