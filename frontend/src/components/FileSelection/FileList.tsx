import React, { useState, useEffect } from 'react';
import { getDiscoveredFiles, selectFiles, deselectFiles, getFilePreview } from '../../utils/api';
import { FileFilter } from './FileFilter';
import { FilePreview } from './FilePreview';

interface FileItem {
  id: number;
  file_name: string;
  file_type: string;
  file_size: number;
  url: string;
  is_selected: boolean;
  status: string;
  last_modified: string;
}

export const FileList: React.FC<{ websiteId: number }> = ({ websiteId }) => {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<number[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [previewFile, setPreviewFile] = useState<FileItem | null>(null);
  const [showPreview, setShowPreview] = useState(false);
  const [groupBy, setGroupBy] = useState<'none' | 'type' | 'size' | 'date'>('none');
  const pageSize = 20;

  const fetchFiles = async (page: number = 1) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await getDiscoveredFiles(websiteId, page, pageSize);
      
      if (response.files && Array.isArray(response.files)) {
        setFiles(response.files);
        setTotalPages(Math.ceil(response.total_count / pageSize));
        
        // Update selected files state based on is_selected flag
        const initiallySelected = response.files
          .filter((file: FileItem) => file.is_selected)
          .map((file: FileItem) => file.id);
        setSelectedFiles(initiallySelected);
      } else {
        setFiles([]);
        setTotalPages(1);
      }
    } catch (err) {
      setError('Failed to fetch files. Please try again.');
      console.error('Error fetching files:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFiles(currentPage);
  }, [websiteId, currentPage]);

  const handleSelectFile = async (fileId: number, selected: boolean) => {
    try {
      if (selected) {
        await selectFiles(websiteId, [fileId]);
        setSelectedFiles([...selectedFiles, fileId]);
      } else {
        await deselectFiles(websiteId, [fileId]);
        setSelectedFiles(selectedFiles.filter(id => id !== fileId));
      }
      
      // Refresh files to get updated selection status
      fetchFiles(currentPage);
    } catch (err) {
      setError('Failed to update file selection.');
      console.error('Error updating selection:', err);
    }
  };

  const handleSelectAll = async () => {
    try {
      const allFileIds = files.map(file => file.id);
      await selectFiles(websiteId, allFileIds);
      setSelectedFiles(allFileIds);
      fetchFiles(currentPage);
    } catch (err) {
      setError('Failed to select all files.');
      console.error('Error selecting all files:', err);
    }
  };

  const handleDeselectAll = async () => {
    try {
      await deselectFiles(websiteId, selectedFiles);
      setSelectedFiles([]);
      fetchFiles(currentPage);
    } catch (err) {
      setError('Failed to deselect all files.');
      console.error('Error deselecting all files:', err);
    }
  };

  const handlePreview = async (file: FileItem) => {
    try {
      const preview = await getFilePreview(file.id);
      setPreviewFile({ ...file, preview: preview.preview });
      setShowPreview(true);
    } catch (err) {
      setError('Failed to load preview.');
      console.error('Error loading preview:', err);
    }
  };

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    // In a real implementation, you would call the search API here
    // For now, we'll just filter locally
    if (query.trim() === '') {
      fetchFiles(currentPage);
    } else {
      // Local filtering as a temporary solution
      const filtered = files.filter(file =>
        file.file_name.toLowerCase().includes(query.toLowerCase()) ||
        file.url.toLowerCase().includes(query.toLowerCase())
      );
      setFiles(filtered);
    }
  };

  const handleGroupChange = (groupBy: 'none' | 'type' | 'size' | 'date') => {
    setGroupBy(groupBy);
  };

  const groupedFiles = () => {
    if (groupBy === 'none') {
      return { 'All Files': files };
    }
    
    if (groupBy === 'type') {
      return files.reduce((groups, file) => {
        const type = file.file_type || 'Unknown';
        if (!groups[type]) {
          groups[type] = [];
        }
        groups[type].push(file);
        return groups;
      }, {} as Record<string, FileItem[]>);
    }
    
    if (groupBy === 'size') {
      return files.reduce((groups, file) => {
        const sizeCategory = file.file_size < 1024 * 1024 ? 'Small (<1MB)' : 
                           file.file_size < 10 * 1024 * 1024 ? 'Medium (1-10MB)' : 'Large (>10MB)';
        if (!groups[sizeCategory]) {
          groups[sizeCategory] = [];
        }
        groups[sizeCategory].push(file);
        return groups;
      }, {} as Record<string, FileItem[]>);
    }
    
    // Group by date (today, this week, older)
    return files.reduce((groups, file) => {
      const fileDate = new Date(file.last_modified || Date.now());
      const today = new Date();
      const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
      
      let dateCategory = 'Older';
      if (fileDate >= today.setHours(0, 0, 0, 0)) {
        dateCategory = 'Today';
      } else if (fileDate >= weekAgo) {
        dateCategory = 'This Week';
      }
      
      if (!groups[dateCategory]) {
        groups[dateCategory] = [];
      }
      groups[dateCategory].push(file);
      return groups;
    }, {} as Record<string, FileItem[]>);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
    return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB';
  };

  const getFileIcon = (fileType: string) => {
    const type = fileType.toLowerCase();
    if (type.includes('pdf')) return '📄';
    if (type.includes('word') || type.includes('doc')) return '📝';
    if (type.includes('excel') || type.includes('xls')) return '📊';
    if (type.includes('powerpoint') || type.includes('ppt')) return '📈';
    if (type.includes('text') || type.includes('txt')) return '📋';
    if (type.includes('html') || type.includes('htm')) return '🌐';
    if (type.includes('json')) return '📦';
    if (type.includes('xml')) return '🔗';
    return '📁';
  };

  if (loading && files.length === 0) {
    return (
      <div className="loading-spinner">
        <div className="spinner"></div>
        <p>Loading files...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-message">
        <p>{error}</p>
        <button onClick={() => fetchFiles(currentPage)}>Retry</button>
      </div>
    );
  }

  const fileGroups = groupedFiles();

  return (
    <div className="file-list-container">
      <h2>Discovered Files</h2>
      
      <FileFilter
        onSearch={handleSearch}
        onGroupChange={handleGroupChange}
        searchQuery={searchQuery}
        groupBy={groupBy}
      />

      <div className="file-list-actions">
        <div className="selection-info">
          <span>{selectedFiles.length} of {files.length} files selected</span>
        </div>
        <div className="bulk-actions">
          <button onClick={handleSelectAll} disabled={selectedFiles.length === files.length}>
            Select All
          </button>
          <button onClick={handleDeselectAll} disabled={selectedFiles.length === 0}>
            Deselect All
          </button>
        </div>
      </div>

      <div className="file-groups">
        {Object.entries(fileGroups).map(([groupName, groupFiles]) => (
          <div key={groupName} className="file-group">
            <h3>{groupName} ({groupFiles.length})</h3>
            <div className="file-items">
              {groupFiles.map((file) => (
                <div key={file.id} className={`file-item ${file.is_selected ? 'selected' : ''}`}>
                  <div className="file-info">
                    <div className="file-icon">{getFileIcon(file.file_type)}</div>
                    <div className="file-details">
                      <div className="file-name">{file.file_name}</div>
                      <div className="file-meta">
                        <span className="file-type">{file.file_type}</span>
                        <span className="file-size">{formatFileSize(file.file_size)}</span>
                        <span className="file-status">{file.status}</span>
                      </div>
                    </div>
                  </div>
                  <div className="file-actions">
                    <input
                      type="checkbox"
                      checked={file.is_selected}
                      onChange={(e) => handleSelectFile(file.id, e.target.checked)}
                      className="file-checkbox"
                    />
                    <button
                      onClick={() => handlePreview(file)}
                      className="preview-button"
                      title="Preview"
                    >
                      👁️
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="pagination">
        <button
          onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
          disabled={currentPage === 1}
        >
          Previous
        </button>
        <span>Page {currentPage} of {totalPages}</span>
        <button
          onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
          disabled={currentPage === totalPages}
        >
          Next
        </button>
      </div>

      {showPreview && previewFile && (
        <FilePreview
          file={previewFile}
          onClose={() => setShowPreview(false)}
        />
      )}
    </div>
  );
};

// Add some basic CSS styles
const style = document.createElement('style');
style.textContent = `
.file-list-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.file-list-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 20px 0;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 5px;
}

.bulk-actions button {
  margin-left: 10px;
  padding: 8px 16px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.bulk-actions button:disabled {
  background: #cccccc;
  cursor: not-allowed;
}

.file-groups {
  margin-top: 20px;
}

.file-group {
  margin-bottom: 30px;
  border: 1px solid #ddd;
  border-radius: 5px;
  padding: 15px;
}

.file-group h3 {
  margin-top: 0;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.file-items {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.file-item {
  border: 1px solid #ddd;
  padding: 15px;
  border-radius: 5px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.2s;
}

.file-item:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.file-item.selected {
  border-color: #4CAF50;
  background: #f0fff0;
}

.file-info {
  display: flex;
  align-items: center;
  flex: 1;
}

.file-icon {
  font-size: 24px;
  margin-right: 15px;
}

.file-details {
  flex: 1;
}

.file-name {
  font-weight: bold;
  margin-bottom: 5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
}

.file-meta {
  font-size: 12px;
  color: #666;
}

.file-meta span {
  margin-right: 10px;
}

.file-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.file-checkbox {
  width: 18px;
  height: 18px;
}

.preview-button {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  padding: 5px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 30px;
}

.pagination button {
  padding: 8px 16px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.pagination button:disabled {
  background: #cccccc;
  cursor: not-allowed;
}

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 50px;
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top: 4px solid #4CAF50;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  color: #d32f2f;
  background: #ffebee;
  padding: 15px;
  border-radius: 5px;
  margin: 20px 0;
}
`;
document.head.appendChild(style);