import React, { useState, useEffect } from "react";
import { apiFetch } from "../utils/api";

const MOCK_DOCS = [
  { id: "doc-001", name: "2026-field-assessment.pdf", parsed: true, triplets: 15, cards: 2 },
  { id: "doc-002", name: "2026-unhcr-overview.pdf", parsed: false, triplets: 0, cards: 0 },
  { id: "doc-003", name: "local-upload.docx", parsed: true, triplets: 22, cards: 3 },
];

export default function Ingestion() {
  const [docs, setDocs] = useState([]);
  useEffect(() => {
    // TODO: Replace with apiFetch("/api/v1/ingestion/list") when backend is live
    setDocs(MOCK_DOCS);
  }, []);
  return (
    <div style={{maxWidth: 720, margin: '32px auto'}}>
      <h2>Ingestion Pipeline</h2>
      <p>Documents processed via ingestion:</p>
      <table style={{width: '100%', marginBottom: 24}}>
        <thead>
          <tr>
            <th>Document</th>
            <th>Parsed?</th>
            <th>Triplets</th>
            <th>Knowledge Cards</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {docs.map(doc => (
            <tr key={doc.id} style={{background: doc.parsed ? '#f8fff8' : '#fffaf0'}}>
              <td>{doc.name}</td>
              <td>{doc.parsed ? "✔" : "⏳"}</td>
              <td>{doc.triplets}</td>
              <td>{doc.cards}</td>
              <td>{doc.parsed ? <button>View Wiki</button> : <button disabled>Parse</button>}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <button style={{marginTop:8}}>Upload Document (Demo)</button>
    </div>
  );
}
