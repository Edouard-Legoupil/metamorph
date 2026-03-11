import React from "react";

export const MarkdownEditor: React.FC<{section: any, value?: string, onChange: (v:string)=>void}> = ({ section, value = '', onChange }) => (
  <div>
    <h4>Edit: {section.name}</h4>
    <textarea
      value={value}
      onChange={e => onChange(e.target.value)}
      rows={10}
      style={{width: '100%', minHeight: '13em', fontFamily: 'monospace'}}
      placeholder={`Write markdown for ${section.name}`}
    />
    <small>Word limit: {section.word_limit||'n/a'}</small>
  </div>
);
export default MarkdownEditor;
