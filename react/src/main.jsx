import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import Signup from "./pages/Signup.jsx";
import Login from "./pages/Login.jsx"
import Home from "./pages/Home.jsx"
import Profile from "./pages/Profile.jsx"
import Unknown from "./pages/Unknown.jsx"
import "./styles/index.css";

const signupRoot = document.getElementById("signup-root");
const loginRoot = document.getElementById("login-root")
const homeRoot = document.getElementById("home-root")
const profileRoot = document.getElementById("profile-root")
const unknownRoot = document.getElementById("unknown-root")

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

if (homeRoot) {
    createRoot(homeRoot).render(
        <StrictMode>
            <Home />
        </StrictMode>
    );
}

if (profileRoot) {
    createRoot(profileRoot).render(
        <StrictMode>
            <Profile />
        </StrictMode>
    );
}

if (unknownRoot) {
    createRoot(unknownRoot).render(
        <StrictMode>
            <Unknown />
        </StrictMode>
    );
}

//if (logoutRoot) {
//    createRoot(loginRoot).render(
//        <StrictMode>
//            <Logout />
//        </StrictMode>
//    );
//}



