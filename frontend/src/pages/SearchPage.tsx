import React, { useState } from "react";

export default function SearchPage() {
  const [q, setQ] = useState("");
  const [mode, setMode] = useState("lexical");
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const search = () => {
    setLoading(true);
    fetch(`/api/v1/search?type=${mode}&q=${encodeURIComponent(q)}`)
      .then(r => r.json())
      .then(setResults)
      .finally(() => setLoading(false));
  };

  return (
    <div style={{ maxWidth: 850, margin: '30px auto', fontFamily: 'Open Sans, Arial, sans-serif' }}>
      <h2>Hybrid Knowledge Search</h2>
      <div style={{ display: 'flex', gap: 10, marginBottom: 16 }}>
        <input value={q} onChange={e => setQ(e.target.value)} placeholder="Search..." style={{ fontSize: 18, padding: 5, flex: 1 }} />
        <select value={mode} onChange={e => setMode(e.target.value)}>
          <option value="lexical">Lexical</option>
          <option value="vector">Vector</option>
          <option value="graph">Graph</option>
          <option value="wiki">Wiki</option>
        </select>
        <button onClick={search} disabled={loading}>Search</button>
      </div>
      {loading && <div>Loading...</div>}
      <div>
        {results.map(r => (
          <div key={r.id || r.block_id || r.claim_id} style={{ background: '#f3f6fb', borderRadius: 7, padding: 15, marginBottom: 13 }}>
            <div style={{ fontWeight: 'bold', fontSize: 18 }}>{r.title || r.section_name || r.canonical_name || r.id}</div>
            <div style={{ fontSize: 14, color: '#555', margin: "5px 0" }}>{r.snippet || r.content_text || r.value || r.desc}</div>
            <div style={{ fontSize: 13, color: '#0072bc' }}>{r.type || r.entity_type || r.block_type}</div>
            <a href={r.wiki_url || `/wiki?card=${r.card_id || r.id}`}>View in Wiki/Card</a>
            {r.context_pack_id && (
              <a href={`/context?pk=${r.context_pack_id}`} style={{ marginLeft: 14 }}>View Agent Context</a>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}