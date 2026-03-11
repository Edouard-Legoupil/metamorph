import React from "react";
export const CardEditor: React.FC<{cardId?: string, initialCard?: any}> = ({ cardId }) => (
  <div>
    <h2>Card Editor</h2>
    <p>Editing or creating card: {cardId}</p>
    <p className="block">(Implementation pending)</p>
  </div>
);
export default CardEditor;
