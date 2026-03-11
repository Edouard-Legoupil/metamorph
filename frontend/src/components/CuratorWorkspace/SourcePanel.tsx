import React from "react";
export const SourcePanel: React.FC<{section: any}> = ({ section }) => (
  <footer style={{background: 'var(--unhcr-light-blue)', padding: '10px', borderTop: '1px solid #e4ebf3', fontSize: '0.95em'}}>
    <b>Source documents for: {section.name}</b>
    <div>(stub panel — traceability, extracted triplets, and document links will appear here)</div>
  </footer>
);
export default SourcePanel;
