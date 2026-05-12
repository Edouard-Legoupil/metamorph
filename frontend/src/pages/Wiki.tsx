import React, { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { BlockActions } from "../components/Wiki/BlockActions";
import { ProvenanceModal } from "../components/Wiki/ProvenanceModal";

const UNHCR_BLUE = "#0072bc";

// Card template definitions
const CARD_TEMPLATES: Record<string, {title: string; description: string; sections: {name: string; word_limit: number; live?: boolean}[]}> = {
  "KC-1": {
    title: "Donor Intelligence Card",
    description: "Comprehensive profile of donor, funding, alignment, and contacts.",
    sections: [
      { name: "Donor Overview", word_limit: 80 },
      { name: "Organisational Structure", word_limit: 60 },
      { name: "Funding History", word_limit: 75 },
      { name: "Strategic Alignment", word_limit: 65 },
      { name: "Active Pledges", word_limit: 20 },
      { name: "Contact Details", word_limit: 30, live: true },
      { name: "Key Contacts List", word_limit: 20, live: true },
    ]
  },
  "KC-2": {
    title: "Field Context Card",
    description: "Contextual operational and protection profile by field location.",
    sections: [
      { name: "Protection Landscape", word_limit: 100 },
      { name: "Population Profile", word_limit: 80 },
      { name: "Socio-Economic", word_limit: 75 },
      { name: "Stakeholder Landscape", word_limit: 65 },
      { name: "Population Figures", word_limit: 20, live: true },
      { name: "Registration Count", word_limit: 10, live: true },
    ]
  },
  "KC-3": {
    title: "Outcome Evidence Card",
    description: "Evidence, KOI/KRI metrics, and evaluation findings for interventions.",
    sections: [
      { name: "Evidence PICO Table", word_limit: 110 },
      { name: "Indicator KOI", word_limit: 40 },
      { name: "Indicator KRI", word_limit: 40 },
    ]
  },
  "KC-4": {
    title: "Partner Capacity Card",
    description: "Evaluation of partner capacity, compliance, and projects.",
    sections: [
      { name: "Capacity Ratings", word_limit: 35 },
      { name: "Compliance & Risk", word_limit: 35 },
      { name: "Active Project Count", word_limit: 20, live: true },
      { name: "Total Beneficiaries Reached", word_limit: 20, live: true },
    ]
  },
  "KC-5": {
    title: "Track Record Card",
    description: "Historical performance and applied lessons for donor/partner.",
    sections: [
      { name: "Past Performance", word_limit: 45 },
      { name: "Lessons Applied", word_limit: 70 },
    ]
  },
  "KC-6": {
    title: "Crisis Political Economy Card",
    description: "Complex emergency/crisis scenario analysis and planning.",
    sections: [
      { name: "Crisis Overview", word_limit: 60 },
      { name: "Scenario Planning", word_limit: 100 },
    ]
  },
};

// Tab types
type TabType = 'article' | 'curation' | 'discussion' | 'history';

export default function Wiki() {
  const { topicId } = useParams<{ topicId: string }>();
  const navigate = useNavigate();
  
  // Load topics from localStorage
  const [topics, setTopics] = useState<{id: string; title: string; cardTemplateId: string; enabled: boolean}[]>([]);
  const [activeTab, setActiveTab] = useState<TabType>('article');
  const [blocks, setBlocks] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [modalBlock, setModalBlock] = useState<any>(null);
  const [editingBlock, setEditingBlock] = useState<any>(null);
  const [editContent, setEditContent] = useState('');

  // Load topics
  useEffect(() => {
    const savedTopics = localStorage.getItem("metamorph_topics");
    if (savedTopics) {
      setTopics(JSON.parse(savedTopics).filter((t: any) => t.enabled));
    }
  }, []);

  // Determine current topic and card template
  const currentTopic = topics.find(t => t.id === topicId);
  const currentCardTemplate = currentTopic ? CARD_TEMPLATES[currentTopic.cardTemplateId] : null;

  // If no topic selected and topics exist, select the first one
  useEffect(() => {
    if (topics.length > 0 && !topicId) {
      navigate(`/wiki/${topics[0].id}`);
    }
  }, [topics, topicId, navigate]);

  // Fetch blocks for the current topic (using cardId as topic proxy for now)
  const cardId = currentTopic?.cardTemplateId || "KC-1";
  useEffect(() => {
    if (cardId) {
      setIsLoading(true);
      setError(null);
      fetch(`/api/v1/blocks/card/${cardId}`)
        .then(r => {
          if (!r.ok) throw new Error('Failed to load blocks');
          return r.json();
        })
        .then(data => {
          setBlocks(data);
          setIsLoading(false);
        })
        .catch(err => {
          setError(err.message);
          setIsLoading(false);
        });
    }
  }, [cardId]);

  // Handle topic selection
  const selectTopic = (topic: {id: string; title: string; cardTemplateId: string; enabled: boolean}) => {
    navigate(`/wiki/${topic.id}`);
  };

  // Handle block edit
  const startEditing = (block: any) => {
    setEditingBlock(block);
    setEditContent(block.template || '');
  };

  const saveEdit = () => {
    if (!editingBlock) return;
    // Update block in state (in real app, this would call API)
    setBlocks(blocks.map(b => b.block_id === editingBlock.block_id ? { ...b, template: editContent } : b));
    setEditingBlock(null);
    setEditContent('');
  };

  const cancelEdit = () => {
    setEditingBlock(null);
    setEditContent('');
  };

  // Get template sections for the current card
  const templateSections = currentCardTemplate?.sections || [];

  return (
    <div style={{ minHeight: '100vh', background: '#f9fbfd', fontFamily: 'Open Sans, Arial, sans-serif', display: 'flex', margin: 0 }}>
      {/* Sidebar - Topic Navigation */}
      <aside style={{ width: 280, background: '#eff6fa', padding: '32px 16px 24px 24px', minHeight: '100vh', boxShadow: '2px 0 8px #e6e6e9', borderRight: `2px solid ${UNHCR_BLUE}`, display: 'flex', flexDirection: 'column' }}>
        <div style={{ marginBottom: 32 }}>
          <img src="https://www.unhcr.org/etc/designs/unhcr/logo.svg" alt="UNHCR" style={{ height: 38 }} />
        </div>
        
        <div style={{ fontWeight: 'bold', fontSize: 17, marginBottom: 16, color: UNHCR_BLUE }}>Knowledge Topics</div>
        
        <div style={{ marginBottom: 16, fontSize: 12, color: '#666' }}>
          <Link to="/settings" style={{ color: UNHCR_BLUE, textDecoration: 'none' }}>
            ⚙️ Configure Topics
          </Link>
        </div>

        {topics.length === 0 ? (
          <div style={{ padding: 16, background: '#fff3cd', borderRadius: 4, marginBottom: 16, fontSize: 13 }}>
            No topics configured. Please go to <Link to="/settings" style={{ color: UNHCR_BLUE }}>Settings</Link> to add topics.
          </div>
        ) : (
          topics.map(topic => {
            const template = CARD_TEMPLATES[topic.cardTemplateId];
            const isActive = topic.id === topicId;
            return (
              <div 
                key={topic.id} 
                onClick={() => selectTopic(topic)} 
                style={{
                  cursor: 'pointer', 
                  padding: '12px 12px', 
                  color: isActive ? UNHCR_BLUE : '#222', 
                  fontWeight: isActive ? 'bold' : 'normal', 
                  borderLeft: isActive ? `4px solid ${UNHCR_BLUE}` : 'none', 
                  background: isActive ? '#e3f0fa' : 'transparent', 
                  borderRadius: 5, 
                  marginBottom: 4,
                  transition: 'all 0.2s',
                  ':hover': { background: '#e3f0fa' }
                }}
              >
                <div style={{ fontSize: 14, fontWeight: 600 }}>{topic.title}</div>
                <div style={{ fontSize: 11, color: '#666', marginTop: 2 }}>
                  {topic.cardTemplateId} - {template?.title}
                </div>
              </div>
            );
          })
        )}

        <div style={{ marginTop: 'auto', paddingTop: 24, borderTop: '1px solid #e6e6e9' }}>
          <div style={{ fontSize: 12, color: '#666', marginBottom: 8 }}>Active Template:</div>
          {currentCardTemplate ? (
            <div style={{ fontSize: 13, fontWeight: 600 }}>
              {currentCardTemplate.title}
              <div style={{ fontSize: 11, color: '#666', marginTop: 2 }}>
                {currentCardTemplate.description}
              </div>
            </div>
          ) : (
            <div style={{ fontSize: 13, color: '#999' }}>No template selected</div>
          )}
        </div>
      </aside>

      {/* Main Content Area */}
      <main style={{ flex: 1, padding: 40, background: '#fff', margin: '36px', boxShadow: '0 2px 24px #e5e7ea', borderRadius: 12, minHeight: 'calc(100vh - 80px)' }}>
        {/* Page Header */}
        <div style={{ marginBottom: 32 }}>
          <h1 style={{ color: UNHCR_BLUE, fontSize: 28, marginBottom: 8 }}>
            {currentTopic?.title || 'Knowledge Topic'}
          </h1>
          {currentCardTemplate && (
            <div style={{ fontSize: 14, color: '#666' }}>
              Template: <strong>{currentCardTemplate.title}</strong> | {currentCardTemplate.description}
            </div>
          )}
        </div>

        {/* Tabs */}
        <div style={{ display: 'flex', gap: 8, marginBottom: 24, borderBottom: '2px solid #eee' }}>
          {[
            { id: 'article', label: 'Article', icon: '📄' },
            { id: 'curation', label: 'Curation', icon: '✏️' },
            { id: 'discussion', label: 'Discussion', icon: '💬' },
            { id: 'history', label: 'History', icon: '📜' },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as TabType)}
              style={{
                padding: '12px 24px',
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                fontSize: 16,
                fontWeight: activeTab === tab.id ? 'bold' : 'normal',
                color: activeTab === tab.id ? UNHCR_BLUE : '#666',
                borderBottom: activeTab === tab.id ? `3px solid ${UNHCR_BLUE}` : 'none',
                marginBottom: -2,
              }}
            >
              <span style={{ marginRight: 8 }}>{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div style={{ padding: 16 }}>
          {error && (
            <div style={{ padding: 16, background: '#ffebee', borderRadius: 8, marginBottom: 24, color: '#c62828' }}>
              Error: {error}
            </div>
          )}

          {isLoading && !blocks.length ? (
            <div style={{ padding: 40, textAlign: 'center', color: '#666' }}>
              Loading blocks...
            </div>
          ) : (
            <>
              {/* ARTICLE TAB - View the curated content */}
              {activeTab === 'article' && (
                <div>
                  <h2 style={{ color: UNHCR_BLUE, fontSize: 20, marginBottom: 16 }}>Article Content</h2>
                  <p style={{ color: '#666', marginBottom: 24 }}>
                    This is the curated view of the knowledge topic. Only accepted, sourced, and current information is displayed.
                  </p>
                  
                  {templateSections.length > 0 && (
                    <div style={{ marginBottom: 24 }}>
                      <strong>Template Sections:</strong>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 8 }}>
                        {templateSections.map(section => (
                          <span key={section.name} style={{ 
                            background: '#e3f2fd', 
                            padding: '4px 12px', 
                            borderRadius: 12, 
                            fontSize: 12,
                            color: UNHCR_BLUE
                          }}>
                            {section.name} ({section.word_limit}w)
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {blocks.length > 0 ? (
                    blocks.map(block => (
                      <div key={block.block_id} style={{ 
                        marginBottom: 32, 
                        padding: 24, 
                        background: '#f7f9fb', 
                        borderRadius: 8, 
                        boxShadow: '0 1px 8px #e6e6f0',
                        position: 'relative'
                      }}>
                        <div style={{ fontWeight: 'bold', fontSize: 18, marginBottom: 6 }}>
                          {block.section_name} 
                          <span style={{ fontSize: 12, color: '#2196f3', marginLeft: 8 }}>{block.block_type}</span>
                        </div>
                        
                        {block.verification_status === "PENDING" && (
                          <div style={{ 
                            position: 'absolute', 
                            top: 24, 
                            right: 24,
                            color: '#d97706', 
                            fontWeight: 'bold', 
                            marginBottom: 4,
                            fontSize: 12,
                            padding: '4px 8px',
                            background: '#fff3e0',
                            borderRadius: 4
                          }}>
                            ⚠️ Pending review
                          </div>
                        )}
                        
                        {block.verification_status === "CONFLICT" && (
                          <div style={{ 
                            position: 'absolute', 
                            top: 24, 
                            right: 24,
                            color: '#c0392b', 
                            fontWeight: 'bold', 
                            marginBottom: 4,
                            fontSize: 12,
                            padding: '4px 8px',
                            background: '#ffebee',
                            borderRadius: 4
                          }}>
                            ⚠️ Conflict detected
                          </div>
                        )}

                        <div style={{ fontSize: 16, color: '#444', marginBottom: 10, lineHeight: 1.6 }}>
                          {block.template}
                        </div>
                        <div style={{ marginBottom: 8, fontSize: 13, color: '#00695c' }}>
                          Provenance: <span>{block.page_id}</span> &nbsp;|&nbsp; Word limit: {block.word_limit}
                          <button 
                            style={{ 
                              marginLeft: 16, 
                              background: '#2196f3', 
                              color: 'white', 
                              border: 'none', 
                              borderRadius: 4, 
                              padding: '3px 11px',
                              cursor: 'pointer'
                            }} 
                            onClick={() => setModalBlock(block)}
                          >
                            View
                          </button>
                        </div>
                        <BlockActions 
                          blockId={block.block_id} 
                          userId="stub-user" 
                          verificationStatus={block.verification_status} 
                          communityTrustScore={35} 
                        />
                      </div>
                    ))
                  ) : (
                    <div style={{ padding: 40, textAlign: 'center', color: '#999' }}>
                      No blocks found for this topic. Blocks will be generated based on the {currentCardTemplate?.title || 'selected template'}.
                    </div>
                  )}
                </div>
              )}

              {/* CURATION TAB - Edit and manage blocks */}
              {activeTab === 'curation' && (
                <div>
                  <h2 style={{ color: UNHCR_BLUE, fontSize: 20, marginBottom: 16 }}>Curation Workspace</h2>
                  <p style={{ color: '#666', marginBottom: 24 }}>
                    Edit, verify, and manage knowledge blocks. This tab allows you to work with the structured content based on the {currentCardTemplate?.title || 'selected template'}.
                  </p>

                  {/* Template-based section structure */}
                  {templateSections.length > 0 && (
                    <div style={{ marginBottom: 24 }}>
                      <div style={{ display: 'grid', gap: 16 }}>
                        {templateSections.map(section => {
                          const sectionBlocks = blocks.filter(b => b.section_name === section.name);
                          return (
                            <div key={section.name} style={{ 
                              background: '#f5f5f5', 
                              padding: 16, 
                              borderRadius: 8,
                              border: '1px solid #e0e0e0'
                            }}>
                              <div style={{ 
                                display: 'flex', 
                                justifyContent: 'space-between', 
                                alignItems: 'center', 
                                marginBottom: 12
                              }}>
                                <h3 style={{ margin: 0, color: UNHCR_BLUE }}>
                                  {section.name}
                                </h3>
                                <div style={{ 
                                  fontSize: 12, 
                                  color: '#666', 
                                  padding: '4px 8px', 
                                  background: '#fff',
                                  borderRadius: 4
                                }}>
                                  Word limit: {section.word_limit}
                                  {section.live && <span style={{ marginLeft: 8, color: '#4caf50' }}>🔄 Live</span>}
                                </div>
                              </div>
                              
                              {sectionBlocks.length > 0 ? (
                                sectionBlocks.map(block => (
                                  <div key={block.block_id} style={{ 
                                    marginBottom: 12, 
                                    padding: 12, 
                                    background: '#fff',
                                    borderRadius: 4,
                                    border: '1px solid #e0e0e0',
                                    position: 'relative'
                                  }}>
                                    <div style={{ 
                                      display: 'flex', 
                                      justifyContent: 'space-between', 
                                      alignItems: 'start',
                                      marginBottom: 8
                                    }}>
                                      <div style={{ flex: 1 }}>
                                        <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 4 }}>
                                          Block: {block.block_id}
                                        </div>
                                        <div style={{ 
                                          fontSize: 14, 
                                          color: '#444', 
                                          background: '#fafafa', 
                                          padding: 8, 
                                          borderRadius: 4,
                                          minHeight: 60,
                                          lineHeight: 1.5
                                        }}>
                                          {block.template || <span style={{ color: '#999' }}>Empty block - click to edit</span>}
                                        </div>
                                      </div>
                                      
                                      <div style={{ marginLeft: 16, display: 'flex', flexDirection: 'column', gap: 4 }}>
                                        <button 
                                          style={{ 
                                            padding: '4px 12px', 
                                            background: UNHCR_BLUE, 
                                            color: 'white', 
                                            border: 'none', 
                                            borderRadius: 4, 
                                            cursor: 'pointer',
                                            fontSize: 12
                                          }}
                                          onClick={() => startEditing(block)}
                                        >
                                          Edit
                                        </button>
                                        <div style={{ 
                                          fontSize: 10, 
                                          color: block.verification_status === 'PENDING' ? '#d97706' : block.verification_status === 'CONFLICT' ? '#c0392b' : '#4caf50',
                                          padding: '2px 6px',
                                          background: block.verification_status === 'PENDING' ? '#fff3e0' : block.verification_status === 'CONFLICT' ? '#ffebee' : '#e8f5e8',
                                          borderRadius: 3,
                                          textAlign: 'center'
                                        }}>
                                          {block.verification_status || 'Accepted'}
                                        </div>
                                      </div>
                                    </div>
                                    
                                    <BlockActions 
                                      blockId={block.block_id} 
                                      userId="stub-user" 
                                      verificationStatus={block.verification_status} 
                                      communityTrustScore={35}
                                    />
                                  </div>
                                ))
                              ) : (
                                <div style={{ 
                                  padding: 16, 
                                  textAlign: 'center', 
                                  color: '#999',
                                  fontSize: 13,
                                  background: '#fff',
                                  borderRadius: 4,
                                  border: '2px dashed #ccc'
                                }}>
                                  No blocks for this section yet
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}

                  {/* Edit Modal */}
                  {editingBlock && (
                    <div style={{ 
                      position: 'fixed', 
                      top: 0, 
                      left: 0, 
                      right: 0, 
                      bottom: 0, 
                      background: 'rgba(0,0,0,0.5)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      zIndex: 1000
                    }}>
                      <div style={{ 
                        background: 'white', 
                        padding: 24, 
                        borderRadius: 8, 
                        maxWidth: 600, 
                        width: '90%',
                        maxHeight: '80vh',
                        overflow: 'auto'
                      }}>
                        <h3 style={{ margin: 0, color: UNHCR_BLUE, marginBottom: 16 }}>
                          Edit Block: {editingBlock.section_name}
                        </h3>
                        <div style={{ marginBottom: 16 }}>
                          <label style={{ display: 'block', marginBottom: 4, fontWeight: 600 }}>
                            Content
                          </label>
                          <textarea
                            value={editContent}
                            onChange={(e) => setEditContent(e.target.value)}
                            style={{ 
                              width: '100%', 
                              minHeight: 150, 
                              padding: 12, 
                              border: '1px solid #ddd', 
                              borderRadius: 4, 
                              fontSize: 14,
                              fontFamily: 'inherit'
                            }}
                            placeholder="Enter block content..."
                          />
                          <div style={{ fontSize: 12, color: '#666', marginTop: 4 }}>
                            Word limit: {editingBlock.word_limit} words
                          </div>
                        </div>
                        <div style={{ display: 'flex', gap: 12, justifyContent: 'flex-end' }}>
                          <button 
                            onClick={cancelEdit}
                            style={{ padding: '8px 20px', border: 'none', background: '#ccc', cursor: 'pointer', borderRadius: 4 }}
                          >
                            Cancel
                          </button>
                          <button 
                            onClick={saveEdit}
                            style={{ padding: '8px 20px', border: 'none', background: UNHCR_BLUE, color: 'white', cursor: 'pointer', borderRadius: 4 }}
                          >
                            Save Changes
                          </button>
                        </div>
                      </div>
                    </div>
                  )}

                  {blocks.length === 0 && templateSections.length === 0 && (
                    <div style={{ padding: 40, textAlign: 'center', color: '#999' }}>
                      No template sections or blocks found. Please select a topic with a valid card template.
                    </div>
                  )}
                </div>
              )}

              {/* DISCUSSION TAB */}
              {activeTab === 'discussion' && (
                <div>
                  <h2 style={{ color: UNHCR_BLUE, fontSize: 20, marginBottom: 16 }}>Discussion</h2>
                  <p style={{ color: '#666', marginBottom: 24 }}>
                    This is where contested, uncertain, or proposed information is evaluated. 
                    Discussion threads are linked to specific blocks, claims, or conflicts.
                  </p>
                  <div style={{ padding: 40, textAlign: 'center', color: '#999' }}>
                    Discussion feature coming soon. This will show threads linked to blocks in the {currentCardTemplate?.title || 'current template'}.
                  </div>
                </div>
              )}

              {/* HISTORY TAB */}
              {activeTab === 'history' && (
                <div>
                  <h2 style={{ color: UNHCR_BLUE, fontSize: 20, marginBottom: 16 }}>Revision History</h2>
                  <p style={{ color: '#666', marginBottom: 24 }}>
                    Immutable record of all changes to this topic's knowledge blocks.
                  </p>
                  <div style={{ padding: 40, textAlign: 'center', color: '#999' }}>
                    History feature coming soon. This will show the complete audit trail for all blocks in the {currentCardTemplate?.title || 'current template'}.
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        <ProvenanceModal block={modalBlock} onClose={() => setModalBlock(null)} />
      </main>
    </div>
  );
}
