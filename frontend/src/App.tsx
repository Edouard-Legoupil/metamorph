import React from "react";
import NavBar from "./components/NavBar";
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from "react-router-dom";
import Scraping from "./pages/Scraping";
import Ingestion from "./pages/Ingestion";
import Wiki from "./pages/Wiki";
import CurationWorkspace from "./pages/CuratorWorkspace";
import Login from "./pages/Login";
import About from "./pages/About";

function RequireAuth({ children }: { children: React.ReactNode }) {
  const apiKey = typeof window !== 'undefined' ? localStorage.getItem("API_KEY") : null;
  const location = useLocation();
  if (!apiKey) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  return <>{children}</>;
}

export default function App() {
  return (
    <Router>
      <NavBar />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<Navigate to="/wiki" />} />
        <Route path="/wiki" element={<RequireAuth><Wiki /></RequireAuth>} />
        <Route path="/scraping" element={<RequireAuth><Scraping /></RequireAuth>} />
        <Route path="/ingestion" element={<RequireAuth><Ingestion /></RequireAuth>} />
        <Route path="/curation" element={<RequireAuth><CurationWorkspace /></RequireAuth>} />
        <Route path="/about" element={<RequireAuth><About /></RequireAuth>} />
        <Route path="*" element={<Navigate to="/wiki" />} />
      </Routes>
    </Router>
  );
}
