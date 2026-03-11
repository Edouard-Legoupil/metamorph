import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import CuratorWorkspace from "./pages/CuratorWorkspace";
// ... other imports

export default function App() {
  return (
    <Router>
      <Routes>
        {/* ... other routes ... */}
        <Route path="/curation" element={<CuratorWorkspace />} />
        <Route path="/curation/card/:cardId" element={<CuratorWorkspace />} />
      </Routes>
    </Router>
  );
}
