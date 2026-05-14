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
      { name: "Active Pledges", word_limit: 20, live: true },
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
  const [showEditToolbar, setShowEditToolbar] = useState(false);
  const [selectedText, setSelectedText] = useState('');

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

  // Handle text selection for curation toolbar
  const handleTextSelection = () => {
    const selection = window.getSelection();
    if (selection && selection.toString().trim().length > 0) {
      const rect = selection.getRangeAt(0).getBoundingClientRect();
      setSelectedText(selection.toString());
      setShowEditToolbar(true);
    } else {
      setShowEditToolbar(false);
    }
  };

  useEffect(() => {
    document.addEventListener('mouseup', handleTextSelection);
    return () => document.removeEventListener('mouseup', handleTextSelection);
  }, []);

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

      {/* Main Content Area - Wikipedia-style */}
      <main style={{ flex: 1, background: '#fff', margin: '36px', boxShadow: '0 2px 24px #e5e7ea', borderRadius: 12, minHeight: 'calc(100vh - 80px)', position: 'relative' }}>
        {/* Wikipedia-style Header */}
        <div style={{ borderBottom: '1px solid #a2a9b1', padding: '24px 40px', background: '#f8f9fa' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h1 style={{ color: '#202122', fontSize: 32, margin: 0, fontWeight: 'bold' }}>
                {currentTopic?.title || 'Knowledge Topic'}
              </h1>
              {currentCardTemplate && (
                <div style={{ fontSize: 16, color: '#54595d', marginTop: 4 }}>
                  {currentCardTemplate.title}
                </div>
              )}
            </div>
            <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
              {/* Wikipedia-style search */}
              <div style={{ position: 'relative' }}>
                <input 
                  type="text"
                  placeholder="Search this topic"
                  style={{
                    padding: '8px 16px',
                    border: '1px solid #a2a9b1',
                    borderRadius: '2px',
                    fontSize: 14,
                    width: 200
                  }}
                />
                <button style={{
                  position: 'absolute',
                  right: 2,
                  top: 2,
                  background: '#36c',
                  color: 'white',
                  border: 'none',
                  padding: '6px 12px',
                  borderRadius: '2px',
                  cursor: 'pointer'
                }}>Go</button>
              </div>
            </div>
          </div>
        </div>

        {/* Wikipedia-style Tabs */}
        <div style={{ display: 'flex', gap: 0, borderBottom: '1px solid #a2a9b1', background: '#f8f9fa', padding: '0 40px' }}>
          {[{ id: 'article', label: 'Article', icon: '📄' },
            { id: 'discussion', label: 'Discussion', icon: '💬' },
            { id: 'curation', label: 'Curation', icon: '✏️' },
            { id: 'history', label: 'View history', icon: '📜' },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as TabType)}
              style={{
                padding: '12px 20px',
                background: 'none',
                border: 'none',
                borderRight: '1px solid #a2a9b1',
                cursor: 'pointer',
                fontSize: 14,
                fontWeight: 'normal',
                color: activeTab === tab.id ? '#202122' : '#0645ad',
                backgroundColor: activeTab === tab.id ? 'white' : 'transparent',
                borderBottom: activeTab === tab.id ? 'none' : '1px solid #a2a9b1',
                marginBottom: -1,
                ':hover': { backgroundColor: '#f8f9fa' }
              }}
            >
              <span style={{ marginRight: 8 }}>{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div style={{ padding: '32px 40px' }}>
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
              {/* ARTICLE TAB - Wikipedia-style article view */}
              {activeTab === 'article' && (
                <div style={{ maxWidth: '800px', margin: '0 auto' }}>
                  {/* Wikipedia-style article header */}
                  <div style={{ 
                    background: '#f8f9fa', 
                    border: '1px solid #a2a9b1', 
                    borderRadius: '4px', 
                    padding: '16px', 
                    marginBottom: '24px',
                    fontSize: '14px',
                    lineHeight: '1.6'
                  }}>
                    <strong>Knowledge Card Type:</strong> {currentCardTemplate?.title || 'Unknown'}<br />
                    <strong>Template:</strong> {currentTopic?.cardTemplateId || 'None'}<br />
                    <strong>Last Updated:</strong> {new Date().toLocaleDateString()}<br />
                    <strong>Status:</strong> <span style={{ color: '#006600' }}>✓ Curated</span>
                  </div>

                  {/* Wikipedia-style article content */}
                  <div style={{ 
                    fontSize: '16px', 
                    lineHeight: '1.6', 
                    color: '#202122'
                  }}>
                    {templateSections.length > 0 && (
                      <div style={{ marginBottom: '24px' }}>
                        <strong>Template Sections:</strong>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '8px' }}>
                          {templateSections.map(section => (
                            <span key={section.name} style={{ 
                              background: '#e3f2fd', 
                              padding: '4px 12px', 
                              borderRadius: '12px', 
                              fontSize: '12px',
                              color: UNHCR_BLUE
                            }}>
                              {section.name} ({section.word_limit}w)
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Wikipedia-style article sections */}
                    {blocks.length > 0 ? (
                      blocks.map((block, index) => (
                        <div key={block.block_id} style={{ marginBottom: '32px' }}>
                          {/* Wikipedia-style section header */}
                          <h2 style={{ 
                            fontSize: '22px', 
                            fontWeight: 'bold', 
                            color: '#202122', 
                            borderBottom: '1px solid #a2a9b1', 
                            paddingBottom: '8px', 
                            marginBottom: '16px'
                          }}>
                            <span id={block.section_name.replace(/\s+/g, '_')}>{block.section_name}</span>
                            {block.verification_status === "PENDING" && (
                              <span style={{ 
                                marginLeft: '12px', 
                                fontSize: '14px', 
                                color: '#d97706', 
                                fontWeight: 'normal'
                              }}>
                                [Pending review]
                              </span>
                            )}
                            {block.verification_status === "CONFLICT" && (
                              <span style={{ 
                                marginLeft: '12px', 
                                fontSize: '14px', 
                                color: '#c0392b', 
                                fontWeight: 'normal'
                              }}>
                                [Conflict detected]
                              </span>
                            )}
                            <span style={{ float: 'right', fontSize: '14px', color: '#666' }}>
                              <a href="#cite_note-1" style={{ color: '#0645ad' }}>[edit]</a>
                            </span>
                          </h2>

                          {/* Wikipedia-style content */}
                          <div style={{ 
                            fontSize: '16px', 
                            lineHeight: '1.6', 
                            color: '#202122', 
                            marginBottom: '16px'
                          }}>
                            {block.template}
                          </div>

                          {/* Wikipedia-style provenance and actions */}
                          <div style={{ 
                            fontSize: '14px', 
                            color: '#54595d', 
                            marginTop: '16px', 
                            paddingTop: '16px', 
                            borderTop: '1px solid #e5e5e5'
                          }}>
                            <strong>Provenance:</strong> {block.page_id} &nbsp;|&nbsp; 
                            <strong>Word limit:</strong> {block.word_limit} words &nbsp;|&nbsp; 
                            <button 
                              style={{ 
                                background: '#2196f3', 
                                color: 'white', 
                                border: 'none', 
                                borderRadius: '4px', 
                                padding: '3px 11px',
                                cursor: 'pointer',
                                fontSize: '12px'
                              }} 
                              onClick={() => setModalBlock(block)}
                            >
                              View provenance
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
                      <div style={{ 
                        padding: '40px', 
                        textAlign: 'center', 
                        color: '#999', 
                        fontStyle: 'italic'
                      }}>
                        No content available for this topic. Content will be generated based on the {currentCardTemplate?.title || 'selected template'}.
                      </div>
                    )}
                  </div>

                  {/* Wikipedia-style footer */}
                  <div style={{ 
                    marginTop: '40px', 
                    paddingTop: '24px', 
                    borderTop: '1px solid #a2a9b1',
                    fontSize: '12px', 
                    color: '#54595d', 
                    lineHeight: '1.6'
                  }}>
                    <strong>Retrieved from</strong> "https://metamorph.unhcr.org/wiki/{topicId}"<br />
                    <strong>This page was last edited on</strong> {new Date().toLocaleDateString()} <strong>at</strong> {new Date().toLocaleTimeString()}.<br />
                    <strong>Text is available under the</strong> <a href="#" style={{ color: '#0645ad' }}>Creative Commons Attribution-ShareAlike License</a>; <strong>additional terms may apply.</strong>
                  </div>
                </div>
              )}

              {/* DISCUSSION TAB - Wikipedia-style talk page */}
              {activeTab === 'discussion' && (
                <div style={{ maxWidth: '800px', margin: '0 auto' }}>
                  <h2 style={{ fontSize: '24px', fontWeight: 'bold', color: '#202122', marginBottom: '24px' }}>
                    Discussion about "{currentTopic?.title || 'this topic'}"
                  </h2>
                  
                  {/* Wikipedia-style discussion notice */}
                  <div style={{ 
                    background: '#f8f9fa', 
                    border: '1px solid #a2a9b1', 
                    borderRadius: '4px', 
                    padding: '16px', 
                    marginBottom: '24px',
                    fontSize: '14px',
                    lineHeight: '1.6'
                  }}>
                    <strong>This is the discussion page</strong> for improving the article "{currentTopic?.title || 'this topic'}".
                    <br /><br />
                    Here you can:
                    <ul style={{ margin: '8px 0', paddingLeft: '24px' }}>
                      <li>Discuss changes to article content</li>
                      <li>Propose new content or edits</li>
                      <li>Resolve conflicts and disagreements</li>
                      <li>Ask questions about the topic</li>
                    </ul>
                    <strong>Please sign your posts</strong> with <code>~~~~</code>.
                  </div>

                  {/* Discussion threads would go here */}
                  <div style={{ padding: '40px', textAlign: 'center', color: '#999' }}>
                    Discussion feature coming soon. This will show threads linked to blocks in the {currentCardTemplate?.title || 'current template'}.
                  </div>

                  {/* Wikipedia-style add topic section */}
                  <div style={{ 
                    marginTop: '32px', 
                    padding: '16px', 
                    background: '#f8f9fa', 
                    border: '1px solid #a2a9b1', 
                    borderRadius: '4px'
                  }}>
                    <h3 style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '12px' }}>Add topic</h3>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <input 
                        type="text"
                        placeholder="Enter a title for your discussion"
                        style={{ 
                          flex: 1, 
                          padding: '8px', 
                          border: '1px solid #a2a9b1', 
                          borderRadius: '2px'
                        }}
                      />
                      <button style={{ 
                        padding: '8px 16px', 
                        background: '#36c', 
                        color: 'white', 
                        border: 'none', 
                        borderRadius: '2px', 
                        cursor: 'pointer'
                      }}>
                        Start discussion
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* CURATION TAB - Integrated into article view */}
              {activeTab === 'curation' && (
                <div style={{ maxWidth: '800px', margin: '0 auto' }}>
                  <h2 style={{ fontSize: '24px', fontWeight: 'bold', color: '#202122', marginBottom: '16px' }}>
                    Curation Workspace
                  </h2>
                  <p style={{ color: '#54595d', marginBottom: '24px', lineHeight: '1.6' }}>
                    Edit, verify, and manage knowledge blocks. This workspace allows you to work with the structured content 
                    based on the {currentCardTemplate?.title || 'selected template'}.
                  </p>

                  {/* Template-based section structure */}
                  {templateSections.length > 0 && (
                    <div style={{ marginBottom: '24px' }}>
                      <div style={{ display: 'grid', gap: '24px' }}>
                        {templateSections.map(section => {
                          const sectionBlocks = blocks.filter(b => b.section_name === section.name);
                          return (
                            <div key={section.name} style={{ 
                              background: '#f8f9fa', 
                              padding: '20px', 
                              borderRadius: '8px',
                              border: '1px solid #e0e0e0'
                            }}>
                              <div style={{ 
                                display: 'flex', 
                                justifyContent: 'space-between', 
                                alignItems: 'center', 
                                marginBottom: '16px'
                              }}>
                                <h3 style={{ margin: 0, color: UNHCR_BLUE, fontSize: '18px' }}>
                                  {section.name}
                                </h3>
                                <div style={{ 
                                  fontSize: '12px', 
                                  color: '#666', 
                                  padding: '4px 8px', 
                                  background: '#fff',
                                  borderRadius: '4px'
                                }}>
                                  Word limit: {section.word_limit}
                                  {section.live && <span style={{ marginLeft: '8px', color: '#4caf50' }}>🔄 Live</span>}
                                </div>
                              </div>
                              
                              {sectionBlocks.length > 0 ? (
                                sectionBlocks.map(block => (
                                  <div key={block.block_id} style={{ 
                                    marginBottom: '16px', 
                                    padding: '16px', 
                                    background: '#fff', 
                                    borderRadius: '4px', 
                                    border: '1px solid #e0e0e0',
                                    position: 'relative'
                                  }}>
                                    <div style={{ 
                                      display: 'flex', 
                                      justifyContent: 'space-between', 
                                      alignItems: 'start',
                                      marginBottom: '12px'
                                    }}>
                                      <div style={{ flex: 1 }}>
                                        <div style={{ fontSize: '14px', fontWeight: '600', marginBottom: '8px' }}>
                                          Block: {block.block_id}
                                        </div>
                                        <div style={{ 
                                          fontSize: '14px', 
                                          color: '#444', 
                                          background: '#fafafa', 
                                          padding: '12px', 
                                          borderRadius: '4px', 
                                          minHeight: '80px', 
                                          lineHeight: '1.5',
                                          border: '1px solid #eee'
                                        }}>
                                          {block.template || <span style={{ color: '#999' }}>Empty block - click to edit</span>}
                                        </div>
                                      </div>
                                      
                                      <div style={{ marginLeft: '16px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                        <button 
                                          style={{ 
                                            padding: '6px 14px', 
                                            background: UNHCR_BLUE, 
                                            color: 'white', 
                                            border: 'none', 
                                            borderRadius: '4px', 
                                            cursor: 'pointer',
                                            fontSize: '12px',
                                            fontWeight: '600'
                                          }} 
                                          onClick={() => startEditing(block)}
                                        >
                                          Edit
                                        </button>
                                        <div style={{ 
                                          fontSize: '11px', 
                                          color: block.verification_status === 'PENDING' ? '#d97706' : block.verification_status === 'CONFLICT' ? '#c0392b' : '#4caf50', 
                                          padding: '4px 8px', 
                                          background: block.verification_status === 'PENDING' ? '#fff3e0' : block.verification_status === 'CONFLICT' ? '#ffebee' : '#e8f5e8', 
                                          borderRadius: '4px', 
                                          textAlign: 'center',
                                          fontWeight: '600'
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
                                  padding: '20px', 
                                  textAlign: 'center', 
                                  color: '#999', 
                                  fontSize: '13px', 
                                  background: '#fff', 
                                  borderRadius: '4px', 
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

                  {blocks.length === 0 && templateSections.length === 0 && (
                    <div style={{ padding: '40px', textAlign: 'center', color: '#999' }}>
                      No template sections or blocks found. Please select a topic with a valid card template.
                    </div>
                  )}
                </div>
              )}

              {/* HISTORY TAB - Wikipedia-style history */}
              {activeTab === 'history' && (
                <div style={{ maxWidth: '800px', margin: '0 auto' }}>
                  <h2 style={{ fontSize: '24px', fontWeight: 'bold', color: '#202122', marginBottom: '16px' }}>
                    Revision History
                  </h2>
                  <p style={{ color: '#54595d', marginBottom: '24px', lineHeight: '1.6' }}>
                    Immutable record of all changes to this topic's knowledge blocks.
                  </p>

                  {/* Wikipedia-style history notice */}
                  <div style={{ 
                    background: '#f8f9fa', 
                    border: '1px solid #a2a9b1', 
                    borderRadius: '4px', 
                    padding: '16px', 
                    marginBottom: '24px',
                    fontSize: '14px',
                    lineHeight: '1.6'
                  }}>
                    <strong>View history</strong> for "{currentTopic?.title || 'this topic'}"
                    <br /><br />
                    This page provides access to every revision of this article. 
                    Select any date to view the article as it appeared on that date. 
                    You may also view the <a href="#" style={{ color: '#0645ad' }}>differences between revisions</a>.
                  </div>

                  <div style={{ padding: '40px', textAlign: 'center', color: '#999' }}>
                    History feature coming soon. This will show the complete audit trail for all blocks in the {currentCardTemplate?.title || 'current template'}.
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        <ProvenanceModal block={modalBlock} onClose={() => setModalBlock(null)} />
        
        {/* Wikipedia-style edit toolbar (appears on text selection) */}
        {showEditToolbar && (
          <div style={{ 
            position: 'absolute', 
            background: 'white', 
            border: '1px solid #a2a9b1', 
            borderRadius: '4px', 
            padding: '8px', 
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)', 
            display: 'flex', 
            gap: '8px', 
            zIndex: 1000
          }}>
            <button style={{ 
              padding: '4px 12px', 
              background: '#36c', 
              color: 'white', 
              border: 'none', 
              borderRadius: '4px', 
              cursor: 'pointer', 
              fontSize: '12px'
            }}>
              Edit
            </button>
            <button style={{ 
              padding: '4px 12px', 
              background: '#6c6', 
              color: 'white', 
              border: 'none', 
              borderRadius: '4px', 
              cursor: 'pointer', 
              fontSize: '12px'
            }}>
              Flag
            </button>
            <button style={{ 
              padding: '4px 12px', 
              background: '#c60', 
              color: 'white', 
              border: 'none', 
              borderRadius: '4px', 
              cursor: 'pointer', 
              fontSize: '12px'
            }}>
              Discuss
            </button>
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
              padding: '24px', 
              borderRadius: '8px', 
              maxWidth: '600px', 
              width: '90%', 
              maxHeight: '80vh', 
              overflow: 'auto',
              boxShadow: '0 4px 24px rgba(0,0,0,0.3)'
            }}>
              <h3 style={{ margin: 0, color: UNHCR_BLUE, marginBottom: '16px', fontSize: '18px' }}>
                Edit Block: {editingBlock.section_name}
              </h3>
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', marginBottom: '4px', fontWeight: '600', fontSize: '14px' }}>
                  Content
                </label>
                <textarea
                  value={editContent}
                  onChange={(e) => setEditContent(e.target.value)}
                  style={{ 
                    width: '100%', 
                    minHeight: '150px', 
                    padding: '12px', 
                    border: '1px solid #ddd', 
                    borderRadius: '4px', 
                    fontSize: '14px', 
                    fontFamily: 'inherit',
                    resize: 'vertical'
                  }}
                  placeholder="Enter block content..."
                />
                <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
                  Word limit: {editingBlock.word_limit} words
                </div>
              </div>
              <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
                <button 
                  onClick={cancelEdit}
                  style={{ 
                    padding: '8px 20px', 
                    border: 'none', 
                    background: '#ccc', 
                    cursor: 'pointer', 
                    borderRadius: '4px', 
                    fontSize: '14px'
                  }}
                >
                  Cancel
                </button>
                <button 
                  onClick={saveEdit}
                  style={{ 
                    padding: '8px 20px', 
                    border: 'none', 
                    background: UNHCR_BLUE, 
                    color: 'white', 
                    cursor: 'pointer', 
                    borderRadius: '4px', 
                    fontSize: '14px'
                  }}
                >
                  Save Changes
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}