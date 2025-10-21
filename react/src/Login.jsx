import React, { useState } from "react";
import "./auth.css"

export default function Login() {
  const [formData, setFormData] = useState({
    email: "",
    username: "",
    password: "",
  });

  const newErrors = {};

  const [errors, setErrors] = useState({});
  const [general, setGeneral] = useState("");
  const [success, setSuccess] = useState("");

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setErrors({});
    setGeneral("");
    setSuccess("");

    if (!formData.email) newErrors.email = "Email is required";
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email))
        newErrors.email = "Invalid email format";
    if (!formData.username) newErrors.username = "Username is required";
    if (!formData.password) newErrors.password = "Password is required";

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    try {
    fetch("/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.success) {
          setSuccess(data.message || "Account Logged in successfully!");
          setGeneral("");
          setTimeout(() => (window.location.href = "/"), 1000);
        } else {
          setGeneral(data.message || "Something went wrong");
        }
      })
    } catch(err) {
        setGeneral("Server error. Please try again later.");
    }
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

      {/* Login form */}
      <div className="flex items-center justify-center p-4">
        <div className="auth-form card w-full max-w-md shadow-lg bg-base-100 p-6 mt-6">
          <h1 className="text-2xl font-bold text-center mb-4">Login Page</h1>
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
            </div>

            <button type="submit" className="btn btn-primary w-full mt-2">
              Submit
            </button>
          </form>

          <p className="text-center mt-4">
            Don’t have an account?{" "}
            <a href="/signup" className="text-blue-500 hover:underline">
              Sign up
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}