import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const [apiKey, setApiKey] = useState("");
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    // DEMO MODE: Accept any API key. No backend call.
    localStorage.setItem("API_KEY", apiKey || "demo");
    navigate("/dashboard");
  };

  return (
    <div style={{ maxWidth: 340, margin: "auto", marginTop: 120 }}>
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <input
          autoFocus
          type="text"
          placeholder="Enter API Key (demo mode)"
          value={apiKey}
          onChange={e => setApiKey(e.target.value)}
          style={{ width: "100%", padding: 8, marginBottom: 12 }}
        />
        <button type="submit" style={{ width: "100%" }}>Login</button>
        {error && <div style={{ color: "red", marginTop: 8 }}>{error}</div>}
      </form>
      <div style={{ color: '#888', marginTop: 16 }}>
        Demo mode: No backend required. Use any key.
      </div>
    </div>
  );
}
