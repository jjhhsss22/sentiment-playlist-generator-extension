import api from "./axios";

export async function fetchContent(endpoint, options = {}) {
  try {
    const method = options.method || "get";
    const body = options.body || null;

    const config = { ...options };

    let response;
    if (method.toLowerCase() === "get") {
      response = await api.get(endpoint, config);
    } else {
      response = await api[method](endpoint, body, config);  // For POST, PUT, PATCH → send JSON data
    }

    return response.data;

  } catch (err) {
    return null;
  }
}