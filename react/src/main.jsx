import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import Signup from "./Signup.jsx";
import Login from "./Login.jsx"
import Home from "./Home.jsx"
import "./index.css";

const signupRoot = document.getElementById("signup-root");
const loginRoot = document.getElementById("login-root")
const homeRoot = document.getElementById("home-root")

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

//if (logoutRoot) {
//    createRoot(loginRoot).render(
//        <StrictMode>
//            <Logout />
//        </StrictMode>
//    );
//}



