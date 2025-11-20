import React, { useState, useEffect } from "react";
import api from "../utils/axios.jsx";
import { showMessage } from "../utils/showMessage.jsx";
import { handleLogout } from "../utils/auth";
import { navTo } from "../utils/navigate";

import "../styles/auth.css"


export default function Signup() {
  useEffect(() => {
    const handlePageShow = (event) => {
      if (event.persisted) {
        setFormData({
          email: "",
          username: "",
          password: "",
          confirmPassword: "",
        });
      }
    };

    window.addEventListener("pageshow", handlePageShow);
    return () => window.removeEventListener("pageshow", handlePageShow);
  }, []);

  useEffect(() => {
    const flashMessage = sessionStorage.getItem("flashMessage");
    const flashType = sessionStorage.getItem("flashType");
    if (flashMessage) {
      if (flashType === "success") {
        showMessage(setSuccess, flashMessage);
      } else {
        showMessage(setGeneral, flashMessage);
      }

      sessionStorage.removeItem("flashMessage");
      sessionStorage.removeItem("flashType")
    }
  }, []);

  const [formData, setFormData] = useState({
    email: "",
    username: "",
    password: "",
    confirmPassword: "",
  });

  const [errors, setErrors] = useState({});
  const [general, setGeneral] = useState("");
  const [success, setSuccess] = useState("");

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async(e) => {
    e.preventDefault();
    setErrors({});
    setGeneral("");
    setSuccess("");  // clear old field errors

    const newErrors = {};  // client-side validation before being sent to backend

    if (!formData.email) newErrors.email = "Email is required";
    if (!formData.username) newErrors.username = "Username is required";
    if (!formData.password) newErrors.password = "Password is required";
    else {
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email))
        newErrors.email = "Invalid email format";
      if (formData.password.length < 8)
        newErrors.password = "Password must be at least 8 characters";
      if (!/[A-Z]/.test(formData.password))
        newErrors.password = "Password must have at least one uppercase letter";
      if (!/[0-9]/.test(formData.password))
        newErrors.password = "Password must have at least one number";
      if (/\s/.test(formData.username))
        newErrors.username = "Username cannot contain spaces";
    }
    if (formData.password !== formData.confirmPassword) newErrors.confirmPassword = "Passwords do not match";

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;  // stop if frontend validation failed
    }

    try {
      const { data } = await api.post("/signup", formData);

      showMessage(setSuccess, data.message || "Logged in successfully!");
      setTimeout(() => navTo("/home"), 1000);

    } catch (err) {
      console.error("Signup request error:", err);
      showMessage(setGeneral, err?.response?.data?.message || "Something went wrong.");
    }
  };


  return (
    <div className="min-h-screen bg-base-200">
      <nav className="navbar bg-base-100 px-4 shadow">
        <div className="flex-1">
          <a href="/home" className="text-2xl font-bold text-primary">
            Home
          </a>
        </div>
        <div className="flex-none space-x-4">
          <a href="/profile" className="hover:text-primary font-medium">Profile</a>
          <a href="#" className="hover:text-primary font-medium"
          onClick={(e) => { e.preventDefault(); handleLogout(); }}
          >Logout</a>
        </div>
      </nav>

      {/* Error / Success flash messages */}
      {general && (
        <div className="alert alert-error text-sm p-2 mb-4 rounded">{general}</div>
      )}
      {success && (
        <div className="alert alert-success text-sm p-2 mb-4 rounded">{success}</div>
      )}

      {/* Signup form */}
      <div className="flex items-center justify-center p-4">
        <div className="auth-form card w-full max-w-md shadow-lg bg-base-100 p-6 mt-6">
          <h1 className="text-2xl font-bold text-center mb-4">Signup Page</h1>
          <form className="space-y-4" onSubmit={handleSubmit}>

            {/* Email */}
            <div className="form-control w-full">
              <label className="label">
                <span className="label-text">Email</span>
              </label>
              <input
                type="text"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="Enter email"
                className="input input-bordered w-full"
              />
              {errors.email && (
                <span className="text-red-500 text-sm">{errors.email}</span>
              )}
            </div>

            {/* Username */}
            <div className="form-control w-full">
              <label className="label">
                <span className="label-text">Username</span>
              </label>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                placeholder="Enter username"
                className="input input-bordered w-full"
              />
              {errors.username && (
                <span className="text-red-500 text-sm">{errors.username}</span>
              )}
            </div>

            {/* Password */}
            <div className="form-control w-full">
              <label className="label">
                <span className="label-text">Password</span>
              </label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Enter password"
                className="input input-bordered w-full"
              />
              {errors.password && (
                <span className="text-red-500 text-sm">{errors.password}</span>
              )}
              <ul className="text-xs mt-2 list-none space-y-1">
                <li
                  className={`flex items-center ${
                    formData.password.length >= 8 ? "text-green-600" : "text-gray-500"
                  }`}
                >
                  {formData.password.length >= 8 ? "✅" : "❌"} More than 8 characters
                </li>
                <li
                  className={`flex items-center ${
                    /[A-Z]/.test(formData.password) ? "text-green-600" : "text-gray-500"
                  }`}
                >
                  {/[A-Z]/.test(formData.password) ? "✅" : "❌"} At least one UPPERCASE letter
                </li>
                <li
                  className={`flex items-center ${
                    /[0-9]/.test(formData.password) ? "text-green-600" : "text-gray-500"
                  }`}
                >
                  {/[0-9]/.test(formData.password) ? "✅" : "❌"} At least one number
                </li>
              </ul>
            </div>

            {/* Confirm Password */}
            <div className="form-control w-full">
              <label className="label">
                <span className="label-text">Confirm Password</span>
              </label>
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                placeholder="Confirm password"
                className="input input-bordered w-full"
              />
              {errors.confirmPassword && (
                <span className="text-red-500 text-sm">{errors.confirmPassword}</span>
              )}
            </div>

            <button type="submit" className="btn btn-primary w-full mt-2">
              Submit
            </button>
          </form>

          <p className="text-center mt-4">
            Already have an account?{" "}
            <a href="/login" className="text-blue-500 hover:underline">
              Log in
            </a>
          </p>
        </div>
      </div>
    </div>
  )
};
