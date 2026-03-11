import React from "react";
export const SectionNav: React.FC<{ sections: Array<any>, current: number, onSelect: (i:number)=>void }> = ({ sections, current, onSelect }) => (
  <nav style={{padding: '1em', borderRight: '1px solid #eee', height: '100%'}}> 
    <h4>Sections</h4>
    <ul style={{listStyle: 'none', paddingLeft: 0}}>
      {sections.map((s, i) => (
        <li key={i} style={{marginBottom:'.5em'}}> 
          <button onClick={()=>onSelect(i)} style={{fontWeight: i===current?'bold':'normal'}}> {s.name || `Section ${i+1}`} </button> 
        </li>
      ))}
    </ul>
  </nav>
);
export default SectionNav;
