import React from "react";
export const GraphDataExplorer: React.FC<{section: any}> = ({ section }) => (
  <div style={{padding: '1em'}}>
    <h4>Graph Data Explorer</h4>
    <p>Section: {section.name}</p>
    <div style={{background: '#f5faff', padding: '.5em', borderRadius: '4px', border: '1px solid #e4ebf3'}}>Coming soon: Live Cypher/graph results for {section.name}</div>
  </div>
);
export default GraphDataExplorer;
