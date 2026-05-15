import React from 'react';

interface FilePreviewProps {
  file: {
    id: number;
    file_name: string;
    file_type: string;
    url: string;
    preview?: string;
  };
  onClose: () => void;
}

export const FilePreview: React.FC<FilePreviewProps> = ({ file, onClose }) => {
  return (
    <div className="file-preview-overlay">
      <div className="file-preview-modal">
        <div className="preview-header">
          <h3>File Preview: {file.file_name}</h3>
          <button onClick={onClose} className="close-button">×</button>
        </div>

        <div className="preview-content">
          {file.preview ? (
            <div className="preview-text">
              <pre>{file.preview}</pre>
            </div>
          ) : (
            <div className="preview-loading">
              <p>Loading preview...</p>
            </div>
          )}
        </div>

        <div className="preview-footer">
          <div className="file-info">
            <span><strong>Type:</strong> {file.file_type}</span>
            <span><strong>URL:</strong> <a href={file.url} target="_blank" rel="noopener noreferrer">Open original</a></span>
          </div>
          <button onClick={onClose} className="close-preview-button">Close Preview</button>
        </div>
      </div>
    </div>
  );
};

// Add CSS styles
const style = document.createElement('style');
style.textContent = `
.file-preview-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.file-preview-modal {
  background: white;
  border-radius: 8px;
  max-width: 800px;
  width: 90%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.preview-header {
  padding: 15px 20px;
  background: #f5f5f5;
  border-bottom: 1px solid #ddd;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preview-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.close-button {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  padding: 5px;
}

.close-button:hover {
  color: #333;
}

.preview-content {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
  min-height: 300px;
}

.preview-text {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.5;
  max-height: 500px;
  overflow-y: auto;
}

.preview-text pre {
  margin: 0;
  padding: 0;
}

.preview-loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}

.preview-footer {
  padding: 15px 20px;
  background: #f5f5f5;
  border-top: 1px solid #ddd;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.file-info {
  display: flex;
  gap: 20px;
  font-size: 14px;
  color: #666;
}

.file-info a {
  color: #4CAF50;
  text-decoration: none;
}

.file-info a:hover {
  text-decoration: underline;
}

.close-preview-button {
  padding: 8px 16px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.close-preview-button:hover {
  background: #45a049;
}
`;
document.head.appendChild(style);