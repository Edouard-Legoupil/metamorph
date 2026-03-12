import React, { useState, useEffect } from "react";
import PipelineStepper from "../components/PipelineStepper";
import { apiFetch } from "../utils/api";

export default function Dashboard() {
  // Demo stats/state
  const [stats, setStats] = useState({ scraping: 3, ingestion: 2, wiki: 3, curation: 2 });
  const [stage, setStage] = useState("scraping");

  useEffect(() => {
    // TODO: Replace with actual fetches from backend when available
    // Example:
    // apiFetch("/api/v1/scraping/jobs").then(resp => ...)
    // apiFetch("/api/v1/ingestion/list").then(resp => ...)
  }, []);

  return (
    <div style={{maxWidth: 760, margin: '32px auto'}}>
      <h1>Knowledge Pipeline Dashboard</h1>
      <PipelineStepper stage={stage} stats={stats} />

      <div style={{marginBottom: 24, border: '1px solid #eee', borderRadius: 8, padding: 24}}>
        <strong>Workflow Overview:</strong>
        <ul style={{marginTop: 8}}>
          <li><b>Scraping:</b> Collects documents from external sources (UNGM, IATI, etc.)</li>
          <li><b>Ingestion:</b> Parses documents, extracts semantic triplets, and stores them in the graph database</li>
          <li><b>Wiki Pages:</b> Generates wiki-style pages and Knowledge Cards from extracted and reconciled facts</li>
          <li><b>Curation Workspace:</b> Human curators review, edit, and approve Knowledge Cards for use in proposals</li>
        </ul>
        <p style={{marginTop: 12}}>
          Click any stage above to explore, upload, or curate. Your changes are traceable—every claim links back to the document it came from.
        </p>
      </div>
    </div>
  );
}
