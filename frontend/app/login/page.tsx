
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  function handleLogin(e: React.FormEvent) {
    e.preventDefault();

    if (!email || !password) {
      setError("Please enter email and password");
      return;
    }

    localStorage.setItem("recoup_logged_in", "true");
    router.push("/");
  }

  return (
    <main
      style={{
        minHeight: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        background: "#f4f7fb",
        padding: "20px",
      }}
    >
      <form
        onSubmit={handleLogin}
        style={{
          width: "100%",
          maxWidth: "400px",
          background: "white",
          padding: "35px",
          borderRadius: "16px",
          boxShadow: "0 8px 30px rgba(0,0,0,0.1)",
        }}
      >
        <h1 style={{ textAlign: "center", color: "#2563eb" }}>
          RECOUP
        </h1>

        <p style={{ textAlign: "center", color: "#666" }}>
          AI Medical Bill Advocate
        </p>

        <h2>Login</h2>

        <label>Email</label>
        <input
          type="email"
          placeholder="Enter your email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={{
            width: "100%",
            padding: "12px",
            margin: "8px 0 18px",
            border: "1px solid #ccc",
            borderRadius: "8px",
          }}
        />

        <label>Password</label>
        <input
          type="password"
          placeholder="Enter your password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={{
            width: "100%",
            padding: "12px",
            margin: "8px 0 18px",
            border: "1px solid #ccc",
            borderRadius: "8px",
          }}
        />

        {error && (
          <p style={{ color: "red" }}>{error}</p>
        )}

        <button
          type="submit"
          style={{
            width: "100%",
            padding: "13px",
            background: "#2563eb",
            color: "white",
            border: "none",
            borderRadius: "8px",
            cursor: "pointer",
            fontSize: "16px",
          }}
        >
          Login
        </button>

        <p
          style={{
            textAlign: "center",
            color: "#888",
            fontSize: "12px",
            marginTop: "20px",
          }}
        >
          Demo login for Recoup
        </p>
      </form>
    </main>
  );
}