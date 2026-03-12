import React from "react";
import { Link } from "react-router-dom";

const STEPS = [
  { key: "scraping", label: "Scraping" },
  { key: "ingestion", label: "Ingestion" },
  { key: "wiki", label: "Wiki Pages" },
  { key: "curation", label: "Curation Workspace" },
];

export default function PipelineStepper({ stage = "scraping", stats = {} }) {
  const currentIdx = STEPS.findIndex(s => s.key === stage);
  return (
    <div style={{ display: "flex", justifyContent: "space-between", gap: 16, margin: "32px 0" }}>
      {STEPS.map((step, idx) => (
        <Link to={`/${step.key}`} key={step.key} style={{ textDecoration: "none" }}>
          <div style={{
            minWidth: 120,
            padding: 16,
            borderRadius: 8,
            background: idx < currentIdx ? "#def6de" : idx === currentIdx ? "#f0f8ff" : "#f2f2f2",
            border: idx === currentIdx ? "2px solid #259" : "1px solid #bbb",
            textAlign: "center"
          }}>
            <div style={{ fontWeight: idx === currentIdx ? "bold" : "normal" }}>{step.label}</div>
            <div style={{ fontSize: 13, marginTop: 4, color: "#888" }}>{stats[step.key] ? `${stats[step.key]} items` : ""}</div>
            {idx < STEPS.length - 1 && <div style={{ marginTop: 6, fontSize: 18 }}>&rarr;</div>}
          </div>
        </Link>
      ))}
    </div>
  );
}
