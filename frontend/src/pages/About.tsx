import React from "react";
export default function About() {
  return (
    <div style={{maxWidth: 720, margin: '40px auto'}}>
      <h2>About</h2>
      <p>This app is a demonstration of a humanitarian document-to-knowledge pipeline:</p>
      <ul>
        <li><b>Scraping:</b> Pull documents from external sources</li>
        <li><b>Ingestion:</b> Parse documents into semantic triplets & graphs</li>
        <li><b>Wiki:</b> Generate knowledge pages, cards, and intelligence</li>
        <li><b>Curation:</b> Human curators refine cards for actionable use</li>
      </ul>
      <p>Demo mode: All data is simulated. Explore the workflow from the Wiki entry point!</p>
    </div>
  );
}
