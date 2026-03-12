import React, { useState } from "react";
export default function AgentContextView({ contextPackId }) {
  const [contextPack, setContextPack] = useState<any>(null);
  React.useEffect(() => {
    fetch(`/mcp/get_context_pack?context_pack_id=${contextPackId || ''}`)
      .then(r => r.json()).then(setContextPack);
  }, [contextPackId]);

  if (!contextPack) return <div>Loading agentic context pack...</div>;
  return (
    <div style={{ maxWidth: 820, margin: '30px auto', fontFamily: 'Open Sans, Arial, sans-serif' }}>
      <h3>Agent Context Pack</h3>
      <pre style={{ background: '#f5f9fb', borderRadius: 7, padding: 16 }}>{JSON.stringify(contextPack, null, 2)}</pre>
      <div>Origin: <a href={contextPack.origin_wiki_url} target="_blank" rel="noopener noreferrer">View wiki/card</a></div>
    </div>
  );
}
