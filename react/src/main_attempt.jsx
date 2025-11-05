import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Signup from "./pages/Signup.jsx";
import Login from "./pages/Login.jsx"
import Home from "./pages/Home.jsx"
import Profile from "./pages/Profile.jsx"
import Unknown from "./pages/Unknown.jsx"
import "./styles/index.css";


const root = createRoot(document.getElementById("root"));

root.render(
  <StrictMode>
    <Router>
      <Routes>
      <Route path="/" element={<Login />} />
        <Route path="/home" element={<Home />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/login" element={<Login />} />
        <Route path="/Signup" element={<Signup />} />
        {/* Catch-all route */}
        <Route path="*" element={<Unknown />} />
      </Routes>
    </Router>
  </StrictMode>
);



