import React, { useState } from "react";
import {fetchContent} from "../utils/fetchContent.jsx";

export default function Home() {
  const [formData, setFormData] = useState({
    text: "",
    emotion: "",
  });

  const [predictions, setPredictions] = useState([]);
  const [predictedEmotions, setPredictedEmotions] = useState([]);
  const [predictedOthers, setPredictedOthers] = useState();
  const [desiredEmotion, setDesiredEmotion] = useState("");
  const [songs, setSongs] = useState([]);

  const [errors, setErrors] = useState({});
  const [general, setGeneral] = useState("");
  const [success, setSuccess] = useState("");
  const [isVisible, setIsVisible] = useState(false);

  const showMessage = (setter, message, duration = 3000, fadeDuration = 500) => {
    setter(message);
    setIsVisible(true);

    setTimeout(() => setIsVisible(false), duration);

    setTimeout(() => setter(""), duration + fadeDuration);
  };

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

    const newErrors = {};

    if (!formData.text) newErrors.text = "you need to type something in";
    if (!formData.emotion) newErrors.emotion = "you need to select an emotion";

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    const data = await fetchContent("/api/home", {
      method: "POST",
      headers: { "X-Requested-With": "ReactApp" },
      body: JSON.stringify(formData),
    });

    if (data.success) {
      setPredictions(data.predictions_list || []);
      setPredictedEmotions(data.predicted_emotions || []);
      setPredictedOthers(data.others_prediction || 0)
      setDesiredEmotion(data.desired_emotion || "");
      setSongs(data.songs_playlist || []);
      showMessage(setSuccess, "Playlist generated successfully!");
    } else {
      console.error("Home API error:", data.message);
      showMessage(setGeneral, data.message || "Something went wrong.");
    }
  };

  const emotions = {
    Positive: ["Happiness", "Enthusiasm", "Love", "Relief", "Fun"],
    Neutral: ["Neutral", "Boredom", "Empty", "Surprise"],
    Negative: ["Anger", "Hate", "Sadness", "Worry"],
  };

  return (
    <div className="relative min-h-screen overflow-hidden">
      <video
        autoPlay
        loop
        muted
        playsInline
        className="absolute inset-0 w-full h-full object-cover"
      >
        <source src="/static/assets/gradient.mp4" type="video/mp4" />
      </video>

      {/* Navbar */}
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

      {/* Alerts */}
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

      {/* Main Section */}
      <div className="relative z-10 flex items-center justify-center min-h-screen px-6">
        <div className="w-full max-w-2xl mt-4 bg-base-200/80 backdrop-blur-xl border border-neutral rounded-2xl shadow-2xl p-8">

          {/* Input Form */}
          {!predictions.length && (
            <>
              <h1 className="text-3xl font-extrabold text-center mb-8 text-primary">
                How are you feeling today?
              </h1>

              <form onSubmit={handleSubmit} className="space-y-8">
                {/* Text Area */}
                <div>
                  <textarea
                    name="text"
                    value={formData.text}
                    onChange={handleChange}
                    placeholder="Write a few sentences about your day..."
                    className="textarea textarea-bordered w-full h-28 rounded-xl bg-base-100 text-base-content focus:ring-1 focus:ring-primary resize-none"
                  />
                  {errors.text && (
                    <span className="text-red-500 text-sm">{errors.text}</span>
                  )}
                </div>

                {/* Emotion Options */}
                <div>
                  <h2 className="text-xl font-semibold mb-4 text-primary">
                    How do you want to feel?
                  </h2>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {/* Positive */}
                    <div className="p-4 rounded-xl bg-success/10 border border-success/30 shadow-sm">
                      <h3 className="text-success font-semibold mb-2">Positive</h3>
                      {emotions.Positive.map((emo) => (
                        <label key={emo} className="flex items-center justify-between py-1">
                          <span>{emo}</span>
                          <input
                            type="radio"
                            name="emotion"
                            value={emo}
                            checked={formData.emotion === emo}
                            onChange={handleEmotionChange}
                            className="radio checked:bg-success"
                          />
                        </label>
                      ))}
                    </div>

                    {/* Neutral */}
                    <div className="p-4 rounded-xl bg-neutral/40 border border-neutral/90 shadow-sm">
                      <h3 className="text-neutral-content font-semibold mb-2">Neutral</h3>
                      {emotions.Neutral.map((emo) => (
                        <label key={emo} className="flex items-center justify-between py-1">
                          <span>{emo}</span>
                          <input
                            type="radio"
                            name="emotion"
                            value={emo}
                            checked={formData.emotion === emo}
                            onChange={handleEmotionChange}
                            className="radio checked:bg-neutral"
                          />
                        </label>
                      ))}
                    </div>

                    {/* Negative */}
                    <div className="p-4 rounded-xl bg-error/10 border border-error/30 shadow-sm">
                      <h3 className="text-error font-semibold mb-2">Negative</h3>
                      {emotions.Negative.map((emo) => (
                        <label key={emo} className="flex items-center justify-between py-1">
                          <span>{emo}</span>
                          <input
                            type="radio"
                            name="emotion"
                            value={emo}
                            checked={formData.emotion === emo}
                            onChange={handleEmotionChange}
                            className="radio checked:bg-error"
                          />
                        </label>
                      ))}
                    </div>
                  </div>
                  {errors.emotion && (
                    <span className="text-red-500 text-sm">{errors.emotion}</span>
                  )}
                </div>

                {/* Submit */}
                <button
                  type="submit"
                  className="btn btn-primary w-full mt-4 text-lg rounded-xl py-3 transition-transform transform hover:scale-[1.03]"
                >
                  Generate Playlist
                </button>
              </form>
            </>
          )}

          {/* Results */}
          {predictions.length > 0 && predictedEmotions.length > 0 && (
            <div className="mt-6">
              <h1 className="text-3xl font-extrabold text-center mb-8 text-primary">
                Your Emotional Breakdown
              </h1>

              <textarea
                name="textAfterSubmit"
                value={formData.text}
                className="textarea textarea-bordered w-full h-24 mb-6 rounded-xl bg-base-100 text-base-content"
                readOnly
              />

              <h3 className="text-lg font-semibold mb-3 text-primary">You are feeling:</h3>

              <div className="space-y-3">
                {predictions.map((p, idx) => (
                  <div
                    key={idx}
                    className="flex justify-between items-center space-x-4"
                  >
                    <span className="w-1/3 font-medium">{predictedEmotions[idx]}</span>
                    <progress
                      className={`progress w-2/3 ${
                        predictedEmotions[idx] === "Happy" || predictedEmotions[idx] === "Enthusiasm" || predictedEmotions[idx] === "Fun"
                          ? "progress-success"
                          : predictedEmotions[idx] === "Anger" || predictedEmotions[idx] === "Hate"
                          ? "progress-error"
                          : predictedEmotions[idx] === "Boredom" || predictedEmotions[idx] === "Empty"
                          ? "progress-progress"
                          : predictedEmotions[idx] === "Neutral"
                          ? "progress-primary"
                          : predictedEmotions[idx] === "Love"
                          ? "progress-accent"
                          : predictedEmotions[idx] === "Relief"
                          ? "progress-info"
                          : predictedEmotions[idx] === "Surprise"
                          ? "progress-warning"
                          : predictedEmotions[idx] === "Sadness"
                          ? "progress-secondary"
                          : predictedEmotions[idx] === "Worry"
                          ? "progress-neutral"
                          : "progress-primary"

                      }`}
                      value={p * 100}
                      max="100"
                    ></progress>
                    <span>{(p * 100).toFixed(1)}%</span>
                  </div>
                ))}

                {predictedOthers !== 0 && (
                  <div className="flex justify-between items-center bg-base-100 rounded-lg px-4 py-2 border border-base-300">
                    <span className="w-1/3 font-medium">{predictedOthers}</span>
                    <progress
                      className="progress progress-primary w-2/3"
                      value={predictedOthers * 100}
                      max="100"
                    ></progress>
                    <span>{(predictedOthers * 100).toFixed(1)}%</span>
                  </div>
                )}
              </div>

              <h4 className="text-lg font-semibold mt-6 text-primary">
                You want to feel: <span className="text-primary">{desiredEmotion}</span>
              </h4>

              <h2 className="text-2xl font-bold mt-6 mb-3 text-primary">Your Playlist</h2>
              <ul className="list-disc list-inside space-y-2">
                {songs.map((song, idx) => (
                  <li key={idx} className="border-b border-base-300 pb-2">
                    {song}
                  </li>
                ))}
              </ul>

              <div className="text-right mt-6">
                <a class="text-blue-600 after:content-['_↗'] hover:underline" href="/home">
                  🎧 Make another playlist
                </a>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}