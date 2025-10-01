import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import Signup from "./Signup.jsx";
import "./index.css";

const signupRoot = document.getElementById("signup-root");

if (signupRoot) {
  createRoot(signupRoot).render(
    <StrictMode>
      <Signup />
    </StrictMode>
  );
}


