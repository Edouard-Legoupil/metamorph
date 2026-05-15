import React from 'react';
import { IngestionProgress } from '../components/Ingestion';

export const IngestionProgressPage: React.FC = () => {
  return (
    <div className="ingestion-progress-container">
      <IngestionProgress />
    </div>
  );
};

// Add minimal CSS
const style = document.createElement('style');
style.textContent = `
.ingestion-progress-container {
  min-height: 100vh;
  background: #f5f5f5;
}
`;
document.head.appendChild(style);