import React, { useEffect, useState } from "react";

export default function Logout() {
  const [general, setGeneral] = useState("");

  useEffect(() => {
    const handleLogout = async () => {
      try {
        const res = await fetch("/logout", { method: "POST" });
        const data = await res.json();

        if (data.success) {
          setGeneral(data.message || "You have been logged out.");
          setTimeout(() => {
            window.location.href = "/login";
          }, 1500);
        } else {
          setGeneral("Server error. Please try again later.");
        }
      } catch (err) {
        setGeneral("Server error. Please try again later.");
      }
    };

    handleLogout();
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center bg-base-200">
      <div className="alert alert-info text-center shadow-lg p-6 rounded">
        {message || "Logging you out..."}
      </div>
    </div>
  );
}