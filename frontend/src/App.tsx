import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from "react-router-dom";
import CuratorWorkspace from "./pages/CuratorWorkspace";
import Login from "./pages/Login";

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
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/curation" element={
          <RequireAuth>
            <CuratorWorkspace />
          </RequireAuth>
        } />
        <Route path="/curation/card/:cardId" element={
          <RequireAuth>
            <CuratorWorkspace />
          </RequireAuth>
        } />
        <Route path="*" element={<Navigate to="/curation" />} />
      </Routes>
    </Router>
  );
}
