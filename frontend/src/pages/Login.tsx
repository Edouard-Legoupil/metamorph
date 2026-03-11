import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const [apiKey, setApiKey] = useState("");
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    // Call login endpoint
    const resp = await fetch("/api/v1/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ api_key: apiKey }),
    });
    if (resp.ok) {
      localStorage.setItem("API_KEY", apiKey);
      navigate("/curation");
    } else {
      setError("Invalid API key");
    }
  };
  return (
    <div style={{ maxWidth: 340, margin: "auto", marginTop: 120 }}>
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <input
          autoFocus
          type="text"
          placeholder="Enter API Key"
          value={apiKey}
          onChange={e => setApiKey(e.target.value)}
          style={{ width: "100%", padding: 8, marginBottom: 12 }}
        />
        <button type="submit" style={{ width: "100%" }}>Login</button>
        {error && <div style={{ color: "red", marginTop: 8 }}>{error}</div>}
      </form>
    </div>
  );
}
