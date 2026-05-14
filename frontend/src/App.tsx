import React from "react";
import NavBar from "./components/NavBar";
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from "react-router-dom";
import Scraping from "./pages/Scraping";
import Ingestion from "./pages/Ingestion";
import Wiki from "./pages/Wiki";
import Settings from "./pages/Settings";
import Login from "./pages/Login";
import About from "./pages/About";
import WebsiteManagement from "./pages/WebsiteManagement";
import UserManagement from "./pages/UserManagement";
import TeamManagement from "./pages/TeamManagement";
import TopicManagement from "./pages/TopicManagement";
import FileSelectionPage from "./pages/FileSelectionPage";
import IngestionProgressPage from "./pages/IngestionProgressPage";

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
        <Route path="/wiki/:topicId" element={<RequireAuth><Wiki /></RequireAuth>} />
        <Route path="/scraping" element={<RequireAuth><Scraping /></RequireAuth>} />
        <Route path="/ingestion" element={<RequireAuth><Ingestion /></RequireAuth>} />
        <Route path="/websites" element={<RequireAuth><WebsiteManagement /></RequireAuth>} />
        <Route path="/websites/:websiteId/files" element={<RequireAuth><FileSelectionPage /></RequireAuth>} />
        <Route path="/ingestion/progress/:jobId" element={<RequireAuth><IngestionProgressPage /></RequireAuth>} />
        <Route path="/users" element={<RequireAuth><UserManagement /></RequireAuth>} />
        <Route path="/teams" element={<RequireAuth><TeamManagement /></RequireAuth>} />
        <Route path="/topics" element={<RequireAuth><TopicManagement /></RequireAuth>} />
        <Route path="/settings" element={<RequireAuth><Settings /></RequireAuth>} />
        <Route path="/about" element={<RequireAuth><About /></RequireAuth>} />
        <Route path="*" element={<Navigate to="/wiki" />} />
      </Routes>
    </Router>
  );
}
