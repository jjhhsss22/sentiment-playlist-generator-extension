import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import Signup from "./Signup.jsx";
import Login from "./Login.jsx"
import "./index.css";

const signupRoot = document.getElementById("signup-root");
const loginRoot = document.getElementById("login-root")

if (signupRoot) {
    createRoot(signupRoot).render(
        <StrictMode>
            <Signup />
        </StrictMode>
    );
}

if (loginRoot) {
    createRoot(loginRoot).render(
        <StrictMode>
            <Login />
        </StrictMode>
    );
}


