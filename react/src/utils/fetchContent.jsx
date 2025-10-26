export async function fetchContent(url, options = {}) {
  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),          // merge any additional headers
      },
      credentials: "include", // always include cookies
    });

    const data = await res.json().catch(() => null);

    if (!res.ok) {
      console.error("Request failed:", res.status, data);
      return { success: false, message: data?.message || "Server error" };
    }

    return data;

  } catch (err) {
    console.error("Fetch error:", err);
    return { success: false, message: "Network error" };
  }
}