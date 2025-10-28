import React, { useEffect, useState } from "react";
import {fetchContent} from "../utils/fetchContent.jsx";

export default function Profile() {
  const [general, setGeneral] = useState("");
  const [success, setSuccess] = useState("");
  const [isVisible, setIsVisible] = useState(false);

  const [loading, setLoading] = useState(true);
  const [playlists, setPlaylists] = useState([]);

  const showMessage = (setter, message, duration = 3000) => {
    setter(message);
    setIsVisible(true);

    setTimeout(() => setIsVisible(false), duration);

    setTimeout(() => setter(""), duration);
  };

  useEffect(() => {
    const fetchData = async () => {
      const data = await fetchContent("/api/profile", {
        headers: { "X-Requested-With": "ReactApp" },
      });

      setLoading(false);

      if (data.success) {
        setPlaylists(data);
        showMessage(setSuccess, "Playlists fetched successfully");
      } else {
        console.error("Profile API error:", data.message);
        showMessage(setGeneral, data.message || "Failed to fetch profile");
      }
    };

    fetchData();
  }, []);  // empty array = run once on mount

  return (
    <div className="min-h-screen bg-base-200">
      <nav className="navbar bg-base-200 px-6 py-4 shadow-md">
        <div className="flex-1">
          <a href="/home" className="text-2xl font-bold text-primary">
            Home
          </a>
        </div>
        <div className="flex-none space-x-4">
          <a href="/profile" className="hover:text-primary font-medium">Profile</a>
          <a href="/logout" className="hover:text-primary font-medium">Logout</a>
        </div>
      </nav>

      <div className="max-w-2xl mx-auto mt-6 px-4">
        {general && (
          <div className="alert alert-error shadow-lg">
            {general}
          </div>
        )}
        {success && (
          <div className="alert alert-success shadow-lg">
            {success}
          </div>
        )}
      </div>

      <h3 className="custom">Playlists from the past</h3>
      <br />

      <div className="card-container">
        {playlists.map((playlist, index) => (
          <div key={index} className="card mb-3">
            <div className="card-body">
              <h4 className="card-title">Playlist {index + 1}</h4>
              <h6 className="card-subtitle mb-2 text-muted">
                {playlist.start_emotion} → {playlist.target_emotion}
              </h6>
              <p className="card-text">{playlist.prompt}</p>

              <ul className="list-group list-group-flush">
                {playlist.playlist.map((song, i) => (
                  <li key={i} className="list-group-item">
                    {song}
                  </li>
                ))}
              </ul>

              <div className="card-footer text-muted">
                {playlist.creation_date}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}