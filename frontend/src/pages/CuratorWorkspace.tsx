import React, { useState, useEffect } from "react";
export default function CurationWorkspace() {
  const [cards, setCards] = useState([]);
  useEffect(() => {
    fetch('/api/v1/cards').then(r => r.json()).then(setCards);
  }, []);
  return (
    <div style={{maxWidth: 720, margin: '32px auto'}}>
      <h2>Curation Workspace</h2>
      <p>Review and curate Knowledge Cards:</p>
      <table style={{width: '100%', marginBottom: 24}}>
        <thead>
          <tr><th>Title</th><th>Status</th><th>Last Update</th><th>Action</th></tr>
        </thead>
        <tbody>
          {cards.map(card => (
            <tr key={card.id} style={{background: card.status === "Curated" ? '#def6de' : card.status === "Draft" ? '#fffef3' : '#f0f0f0'}}>
              <td>{card.title}</td>
              <td>{card.status}</td>
              <td>{card.updated}</td>
               <td><a href={`/wiki?card=${card.id}`} target="_blank" rel="noopener noreferrer"><button>Review Blocks</button></a></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
