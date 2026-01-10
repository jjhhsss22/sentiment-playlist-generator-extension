import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Signup from "./pages/Signup.jsx";
import Login from "./pages/Login.jsx"
import Home from "./pages/Home.jsx"
import Profile from "./pages/Profile.jsx"
import Unknown from "./pages/Unknown.jsx"

import ProtectedRoute from "./components/ProtectedRoute.jsx"
import NavigateWrapper from "./components/NavigateWrapper.jsx"
import WebSocketWrapper from "./components/WebSocketWrapper.jsx"

import "./styles/index.css";


const root = createRoot(document.getElementById("root"));

root.render(
  <StrictMode>
    <Router>
      <NavigateWrapper>  // move wrapper to wrap whole app if multiple pages need a socket connection
        <Routes>
          <Route path="/" element={<Login />} />

          <Route path="/home" element={
            <ProtectedRoute>
              <WebSocketWrapper>
                <Home />
              </WebSocketWrapper>
            </ProtectedRoute>
          } />

          <Route path="/profile" element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          } />

          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/unknown" element={<Unknown />} />

          {/* catch-all */}
          <Route path="*" element={<Unknown />} />
        </Routes>
      </NavigateWrapper>
    </Router>
  </StrictMode>
);