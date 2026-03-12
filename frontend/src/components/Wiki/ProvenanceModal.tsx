import React, { useState } from "react";

export function ProvenanceModal({ block, onClose }) {
  if (!block) return null;
  return (
    <div style={{ position: "fixed", top: 0, left: 0, right: 0, bottom: 0, background: "rgba(0,0,0,0.35)", zIndex: 8888, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ background: "white", borderRadius: 10, padding: 32, minWidth: 340, maxWidth: 540, boxShadow: "0 2px 32px #aaa" }}>
        <h3 style={{ color: "#0072bc" }}>Provenance & Evidence</h3>
        <div style={{ fontWeight: 'bold', marginTop: 12 }}>Section Path:</div>
        <div>{block.section_name}</div>
        <div style={{ fontWeight: 'bold', marginTop: 12 }}>Page/Entity:</div>
        <div>{block.page_id}</div>
        <div style={{ fontWeight: 'bold', marginTop: 12 }}>Template/Raw:</div>
        <div style={{ fontSize: 13, color: '#555' }}>{block.template}</div>
        <div style={{ fontWeight: 'bold', marginTop: 12 }}>Claim/Evidence Spans:</div>
        <div style={{ whiteSpace: 'pre-wrap', fontSize: 13 }}>{block.evidence_text || '(no span extracted yet)'}</div>
        <div style={{ fontWeight: 'bold', marginTop: 12 }}>Verification:</div>
        <div>Status: {block.verification_status}</div>
        <div>Word Limit: {block.word_limit}</div>
        <div style={{ fontWeight: 'bold', marginTop: 12 }}>Graph Query:</div>
        <pre style={{ background: '#e3e7ea', borderRadius: 4, padding: 8, fontSize: 12 }}>{JSON.stringify(block.graph_query, null, 2)}</pre>
        <button style={{ marginTop: 18, background: '#0072bc', color: 'white', border: 'none', padding: '8px 20px', borderRadius: 5 }} onClick={onClose}>Close</button>
      </div>
    </div>
  );
}
