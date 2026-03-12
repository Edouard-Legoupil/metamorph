import React, { useEffect, useState } from "react";
import { BlockActions } from "./components/Wiki/BlockActions";

const UNHCR_BLUE = "#0072bc";

export default function Wiki() {
  const [blocks, setBlocks] = useState([]);
  const [cardId, setCardId] = useState("KC-1"); // Demo: default Donor Intelligence

  useEffect(() => {
    fetch(`/api/v1/blocks/card/${cardId}`)
      .then(r => r.json())
      .then(setBlocks);
  }, [cardId]);

import { ProvenanceModal } from "../components/Wiki/ProvenanceModal";
  const [modalBlock, setModalBlock] = useState(null);
  return (
    <div style={{ minHeight: '100vh', background: '#f9fbfd', fontFamily: 'Open Sans, Arial, sans-serif', margin: 0 }}>
      <aside style={{ width: 240, background: '#eff6fa', padding: '32px 16px 24px 24px', minHeight: '100vh', boxShadow: '2px 0 8px #e6e6e9', borderRight: `2px solid ${UNHCR_BLUE}` }}>
        <div style={{ marginBottom: 32 }}>
          <img src="https://www.unhcr.org/etc/designs/unhcr/logo.svg" alt="UNHCR" style={{ height: 38 }} />
        </div>
        <div style={{ fontWeight: 'bold', fontSize: 17, marginBottom: 16, color: UNHCR_BLUE }}>Cards</div>
        {["KC-1", "KC-2", "KC-3", "KC-4", "KC-5", "KC-6"].map(cid => (
          <div key={cid} onClick={() => setCardId(cid)} style={{ cursor: 'pointer', padding: '10px 0', color: cardId === cid ? UNHCR_BLUE : '#222', fontWeight: cardId === cid ? 'bold' : 'normal', borderLeft: cardId === cid ? `4px solid ${UNHCR_BLUE}` : 'none', background: cardId === cid ? '#e3f0fa' : 'transparent', borderRadius: 5, marginBottom: 1 }}>
            <span style={{ fontSize: 18, minWidth: 27 }}>{cid}</span>
            <span style={{ marginLeft: 12 }}>{cid}</span>
          </div>
        ))}
      </aside>
      <section style={{ flex: 1, padding: 40, background: '#fff', margin: '36px', boxShadow: '0 2px 24px #e5e7ea', borderRadius: 12, minHeight: 'calc(100vh - 80px)', maxWidth: 820, marginRight: 'auto', marginLeft: 30 }}>
        <h2 style={{ color: UNHCR_BLUE, fontSize: 24 }}>Card: {cardId}</h2>
        {blocks.map(block => (
          <div key={block.block_id} style={{ marginBottom: 32, padding: 24, background: '#f7f9fb', borderRadius: 8, boxShadow: '0 1px 8px #e6e6f0' }}>
            <div style={{ fontWeight: 'bold', fontSize: 18, marginBottom: 6 }}>{block.section_name} <span style={{ fontSize: 12, color: '#2196f3' }}>{block.block_type}</span></div>
            {block.verification_status === "PENDING" && (<div style={{ color: '#d97706', fontWeight: 'bold', marginBottom: 4 }}>
              ⚠️ Pending review
            </div>)}
            {block.verification_status === "CONFLICT" && (<div style={{ color: '#c0392b', fontWeight: 'bold', marginBottom: 4 }}>
              ⚠️ Conflict detected
            </div>)}
            <div style={{ fontSize: 16, color: '#444', marginBottom: 10 }}>{block.template}</div>
            <div style={{ marginBottom: 8, fontSize: 13, color: '#00695c' }}>
              Provenance: <span>{block.page_id}</span> &nbsp;|&nbsp; Word limit: {block.word_limit}
              <button style={{ marginLeft: 16, background: '#2196f3', color: 'white', border: 'none', borderRadius: 4, padding: '3px 11px' }} onClick={() => setModalBlock(block)}>View</button>
            </div>
            <BlockActions blockId={block.block_id} userId="stub-user" verificationStatus={block.verification_status} communityTrustScore={35} />
          </div>
        ))}
        <ProvenanceModal block={modalBlock} onClose={() => setModalBlock(null)} />
      </section>
    </div>
  );
}
