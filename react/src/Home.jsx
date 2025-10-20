import React, { useState } from "react";

export default function Home() {
  const [formData, setFormData] = useState({
    text: "",
    emotion: "",
  });

  const [predictions, setPredictions] = useState([]);
  const [desiredEmotion, setDesiredEmotion] = useState("");
  const [songs, setSongs] = useState([]);
  const [general, setGeneral] = useState("");
  const [success, setSuccess] = useState("");

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleEmotionChange = (e) => {
    setFormData({ ...formData, emotion: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setGeneral("");
    setSuccess("");
    setPredictions([]);
    setSongs([]);

    try {
      const res = await fetch('/', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      const data = await res.json();

      if (data.success) {
        setPredictions(data.predictions);
        setDesiredEmotion(data.desired_emotion);
        setSongs(data.songs_playlist);
        setSuccess("Playlist generated successfully!");
      } else {
        setGeneral(data.message || "Something went wrong.");
      }
    } catch (err) {
      setGeneral("Server error. Please try again later.");
    }
  };

  const emotions = {
    Positive: ["Happiness", "Enthusiasm", "Love", "Relief", "Fun"],
    Neutral: ["Neutral", "Boredom", "Empty", "Surprise"],
    Negative: ["Anger", "Hate", "Sadness", "Worry"],
  };

  return (
    <div className="min-h-screen bg-base-200">
      {/* Navbar */}
      <nav className="navbar bg-base-100 px-4 shadow">
        <div className="flex-1">
          <a href="/" className="btn btn-ghost normal-case text-xl">
            Home
          </a>
        </div>
        <div className="flex-none">
          <ul className="menu menu-horizontal p-0">
            <li>
              <a href="/profile">Profile</a>
            </li>
            <li>
              <a href="/logout">Logout</a>
            </li>
          </ul>
        </div>
      </nav>

      {general && (
        <div className="alert alert-error text-sm p-2 mb-4 rounded">{general}</div>
      )}
      {success && (
        <div className="alert alert-success text-sm p-2 mb-4 rounded">{success}</div>
      )}

      {/* Main Form */}
      <div className="flex items-center justify-center p-4">
          <h1 className="text-2xl font-bold text-center mb-6">
            How are you feeling today?
          </h1>

          <form onSubmit={handleSubmit}>
            <textarea
              name="text"
              value={formData.text}
              onChange={handleChange}
              placeholder="How are you feeling today..."
              className="textarea textarea-bordered w-full h-24"
              required
            />

    //            {/* Emotions */}  Uncaught TypeError: Cannot read properties of undefined (reading 'length')
            {!predictions.length && (
              <>
                <h2 className="text-xl font-semibold mt-6 mb-4">
                  How do you want to feel?
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <h3 className="text-green-600 font-semibold mb-2">
                      Positive Emotions
                    </h3>
                    {emotions.Positive.map((emo) => (
                      <label key={emo} className="label cursor-pointer">
                        <span className="label-text">{emo}</span>
                        <input
                          type="radio"
                          name="emotion"
                          value={emo}
                          checked={formData.emotion === emo}
                          onChange={handleEmotionChange}
                          className="radio checked:bg-green-500"
                        />
                      </label>
                    ))}
                  </div>

                  <div>
                    <h3 className="text-gray-600 font-semibold mb-2">
                      Neutral Emotions
                    </h3>
                    {emotions.Neutral.map((emo) => (
                      <label key={emo} className="label cursor-pointer">
                        <span className="label-text">{emo}</span>
                        <input
                          type="radio"
                          name="emotion"
                          value={emo}
                          checked={formData.emotion === emo}
                          onChange={handleEmotionChange}
                          className="radio checked:bg-gray-500"
                        />
                      </label>
                    ))}
                  </div>

                  <div>
                    <h3 className="text-red-600 font-semibold mb-2">
                      Negative Emotions
                    </h3>
                    {emotions.Negative.map((emo) => (
                      <label key={emo} className="label cursor-pointer">
                        <span className="label-text">{emo}</span>
                        <input
                          type="radio"
                          name="emotion"
                          value={emo}
                          checked={formData.emotion === emo}
                          onChange={handleEmotionChange}
                          className="radio checked:bg-red-500"
                        />
                      </label>
                    ))}
                  </div>
                </div>

                <button type="submit" className="btn btn-primary w-full mt-6">
                  Submit
                </button>
              </>
            )}
          </form>

          {/* Results */}
          {predictions.length > 0 && (
            <div className="mt-8">
              <h3 className="text-lg font-semibold mb-4">You are feeling:</h3>

              <div className="space-y-3">
                {predictions.map((p, idx) => (
                  <div
                    key={idx}
                    className="flex justify-between items-center space-x-4"
                  >
                    <span className="w-1/3 font-medium">{p.emotion}</span>
                    <progress
                      className="progress progress-info w-2/3"
                      value={p.probability * 100}
                      max="100"
                    ></progress>
                    <span>{(p.probability * 100).toFixed(1)}%</span>
                  </div>
                ))}
              </div>

              <h4 className="text-lg font-semibold mt-6">
                You want to feel: {desiredEmotion}
              </h4>

              <h2 className="text-2xl font-bold mt-6 mb-3">Playlist</h2>
              <ul className="list-disc list-inside">
                {songs.map((song, idx) => (
                  <li key={idx} className="border-b py-2">
                    {song}
                  </li>
                ))}
              </ul>

              <div className="text-right mt-4">
                <a href="/" className="text-blue-500 hover:underline">
                  Make another playlist?
                </a>
              </div>
            </div>
          )}
      </div>
    </div>
  );
}