import React, { useState, useEffect } from "react";
import { apiFetch } from "../utils/api";

// Demo data
const MOCK_JOBS = [
  { id: "job-001", source: "UNGM", status: "Completed", doc: "2026-field-assessment.pdf" },
  { id: "job-002", source: "IATI", status: "In Progress", doc: "2026-unhcr-overview.pdf" },
  { id: "job-003", source: "Local Upload", status: "Failed", doc: "bad-data.xls" },
];

export default function Scraping() {
  const [jobs, setJobs] = useState([]);
  useEffect(() => {
    // TODO: Replace with apiFetch("/api/v1/scraping/jobs") when backend is live
    setJobs(MOCK_JOBS);
  }, []);
  return (
    <div style={{maxWidth: 720, margin: '32px auto'}}>
      <h2>Scraping</h2>
      <p>Scraping collects documents from external sources. Current jobs:</p>
      <table style={{width: '100%', marginBottom: 24}}>
        <thead>
          <tr>
            <th>Source</th>
            <th>Document</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {jobs.map(job => (
            <tr key={job.id} style={{background: job.status === "Completed" ? '#edffee' : job.status === "Failed" ? '#fff0f0' : undefined}}>
              <td>{job.source}</td>
              <td>{job.doc}</td>
              <td>{job.status}</td>
              <td>{job.status === "Completed" ? <button>Ingest</button> : "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <button style={{marginTop:8}}>Launch New Scrape (Demo)</button>
    </div>
  );
}
