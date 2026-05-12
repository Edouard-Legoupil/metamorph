import React, { useState, useEffect } from "react";

const UNHCR_BLUE = "#0072bc";

// Card template options from backend
const CARD_TEMPLATES = [
  { id: "KC-1", title: "Donor Intelligence Card", description: "Comprehensive profile of donor, funding, alignment, and contacts." },
  { id: "KC-2", title: "Field Context Card", description: "Contextual operational and protection profile by field location." },
  { id: "KC-3", title: "Outcome Evidence Card", description: "Evidence, KOI/KRI metrics, and evaluation findings for interventions." },
  { id: "KC-4", title: "Partner Capacity Card", description: "Evaluation of partner capacity, compliance, and projects." },
  { id: "KC-5", title: "Track Record Card", description: "Historical performance and applied lessons for donor/partner." },
  { id: "KC-6", title: "Crisis Political Economy Card", description: "Complex emergency/crisis scenario analysis and planning." },
];

export default function Settings() {
  const [topics, setTopics] = useState<{id: string; title: string; cardTemplateId: string; enabled: boolean}[]>([]);
  const [newTopicTitle, setNewTopicTitle] = useState("");
  const [newTopicCardTemplate, setNewTopicCardTemplate] = useState("KC-1");

  // Load saved topics from localStorage
  useEffect(() => {
    const savedTopics = localStorage.getItem("metamorph_topics");
    if (savedTopics) {
      setTopics(JSON.parse(savedTopics));
    } else {
      // Default topics linked to card templates
      const defaultTopics = [
        { id: "donor-unhcr", title: "UNHCR Donor Profile", cardTemplateId: "KC-1", enabled: true },
        { id: "field-syria", title: "Syria Field Context", cardTemplateId: "KC-2", enabled: true },
        { id: "outcome-education", title: "Education Outcomes", cardTemplateId: "KC-3", enabled: true },
        { id: "partner-msf", title: "MSF Partner Capacity", cardTemplateId: "KC-4", enabled: true },
        { id: "track-record-2024", title: "2024 Operations Track Record", cardTemplateId: "KC-5", enabled: true },
        { id: "crisis-sudan", title: "Sudan Crisis Analysis", cardTemplateId: "KC-6", enabled: true },
      ];
      setTopics(defaultTopics);
      localStorage.setItem("metamorph_topics", JSON.stringify(defaultTopics));
    }
  }, []);

  // Save topics to localStorage
  useEffect(() => {
    localStorage.setItem("metamorph_topics", JSON.stringify(topics));
  }, [topics]);

  const addTopic = () => {
    if (!newTopicTitle.trim()) return;
    const newTopic = {
      id: `topic-${Date.now()}`,
      title: newTopicTitle,
      cardTemplateId: newTopicCardTemplate,
      enabled: true,
    };
    setTopics([...topics, newTopic]);
    setNewTopicTitle("");
    setNewTopicCardTemplate("KC-1");
  };

  const updateTopic = (id: string, updates: Partial<{title: string; cardTemplateId: string; enabled: boolean}>) => {
    setTopics(topics.map(t => t.id === id ? { ...t, ...updates } : t));
  };

  const deleteTopic = (id: string) => {
    setTopics(topics.filter(t => t.id !== id));
  };

  const getTemplateTitle = (templateId: string) => {
    const template = CARD_TEMPLATES.find(t => t.id === templateId);
    return template ? template.title : templateId;
  };

  return (
    <div style={{ maxWidth: 900, margin: '32px auto', padding: '0 20px' }}>
      <h1 style={{ color: UNHCR_BLUE, marginBottom: 24 }}>Settings - Topics Configuration</h1>
      
      <div style={{ background: '#fff', padding: 24, borderRadius: 8, boxShadow: '0 2px 4px rgba(0,0,0,0.1)', marginBottom: 32 }}>
        <h2 style={{ color: UNHCR_BLUE, marginBottom: 16 }}>Configure Knowledge Topics</h2>
        <p style={{ color: '#666', marginBottom: 20 }}>
          Each topic is linked to a Knowledge Card template that drives the article format and structure.
        </p>
        
        {/* Add New Topic */}
        <div style={{ display: 'flex', gap: 12, marginBottom: 24, flexWrap: 'wrap' }}>
          <input
            type="text"
            value={newTopicTitle}
            onChange={(e) => setNewTopicTitle(e.target.value)}
            placeholder="New topic title"
            style={{ flex: 1, minWidth: 250, padding: '8px 12px', border: '1px solid #ddd', borderRadius: 4, fontSize: 14 }}
          />
          <select
            value={newTopicCardTemplate}
            onChange={(e) => setNewTopicCardTemplate(e.target.value)}
            style={{ padding: '8px 12px', border: '1px solid #ddd', borderRadius: 4, fontSize: 14 }}
          >
            {CARD_TEMPLATES.map(template => (
              <option key={template.id} value={template.id}>{template.id}: {template.title}</option>
            ))}
          </select>
          <button
            onClick={addTopic}
            style={{ padding: '8px 20px', background: UNHCR_BLUE, color: 'white', border: 'none', borderRadius: 4, cursor: 'pointer', fontSize: 14 }}
          >
            Add Topic
          </button>
        </div>

        {/* Topics Table */}
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: '#f6f8fa' }}>
                <th style={{ padding: 12, textAlign: 'left', borderBottom: '2px solid #ddd' }}>Enabled</th>
                <th style={{ padding: 12, textAlign: 'left', borderBottom: '2px solid #ddd' }}>Topic Title</th>
                <th style={{ padding: 12, textAlign: 'left', borderBottom: '2px solid #ddd' }}>Card Template</th>
                <th style={{ padding: 12, textAlign: 'left', borderBottom: '2px solid #ddd' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {topics.map(topic => (
                <tr key={topic.id} style={{ borderBottom: '1px solid #eee' }}>
                  <td style={{ padding: 12 }}>
                    <input
                      type="checkbox"
                      checked={topic.enabled}
                      onChange={(e) => updateTopic(topic.id, { enabled: e.target.checked })}
                    />
                  </td>
                  <td style={{ padding: 12 }}>
                    <input
                      type="text"
                      value={topic.title}
                      onChange={(e) => updateTopic(topic.id, { title: e.target.value })}
                      style={{ width: '100%', padding: 8, border: '1px solid #ddd', borderRadius: 4, fontSize: 14 }}
                    />
                  </td>
                  <td style={{ padding: 12 }}>
                    <select
                      value={topic.cardTemplateId}
                      onChange={(e) => updateTopic(topic.id, { cardTemplateId: e.target.value })}
                      style={{ padding: 8, border: '1px solid #ddd', borderRadius: 4, fontSize: 14, width: '100%' }}
                    >
                      {CARD_TEMPLATES.map(template => (
                        <option key={template.id} value={template.id}>{template.id}</option>
                      ))}
                    </select>
                  </td>
                  <td style={{ padding: 12 }}>
                    <button
                      onClick={() => deleteTopic(topic.id)}
                      style={{ padding: '6px 12px', background: '#c0392b', color: 'white', border: 'none', borderRadius: 4, cursor: 'pointer', fontSize: 12 }}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div style={{ marginTop: 16, color: '#666', fontSize: 13 }}>
          {topics.filter(t => t.enabled).length} topics enabled
        </div>
      </div>

      {/* Card Templates Reference */}
      <div style={{ background: '#fff', padding: 24, borderRadius: 8, boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <h2 style={{ color: UNHCR_BLUE, marginBottom: 16 }}>Knowledge Card Templates Reference</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 16 }}>
          {CARD_TEMPLATES.map(template => (
            <div key={template.id} style={{ padding: 16, background: '#f9f9f9', borderRadius: 8, border: '1px solid #eee' }}>
              <div style={{ fontWeight: 'bold', color: UNHCR_BLUE, marginBottom: 4 }}>{template.id}</div>
              <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 4 }}>{template.title}</div>
              <div style={{ fontSize: 13, color: '#666' }}>{template.description}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
