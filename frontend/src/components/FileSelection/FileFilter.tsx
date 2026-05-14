import React from 'react';

interface FileFilterProps {
  onSearch: (query: string) => void;
  onGroupChange: (groupBy: 'none' | 'type' | 'size' | 'date') => void;
  searchQuery: string;
  groupBy: 'none' | 'type' | 'size' | 'date';
}

export const FileFilter: React.FC<FileFilterProps> = ({ 
  onSearch, 
  onGroupChange, 
  searchQuery, 
  groupBy 
}) => {
  const [localQuery, setLocalQuery] = React.useState(searchQuery);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setLocalQuery(e.target.value);
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(localQuery);
  };

  const handleGroupChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onGroupChange(e.target.value as 'none' | 'type' | 'size' | 'date');
  };

  const handleClearSearch = () => {
    setLocalQuery('');
    onSearch('');
  };

  return (
    <div className="file-filter">
      <form onSubmit={handleSearchSubmit} className="search-form">
        <input
          type="text"
          placeholder="Search files by name or URL..."
          value={localQuery}
          onChange={handleSearchChange}
          className="search-input"
        />
        <button type="submit" className="search-button">Search</button>
        {localQuery && (
          <button 
            type="button" 
            onClick={handleClearSearch} 
            className="clear-button"
          >
            ×
          </button>
        )}
      </form>

      <div className="group-controls">
        <label htmlFor="group-by">Group by:</label>
        <select 
          id="group-by" 
          value={groupBy} 
          onChange={handleGroupChange} 
          className="group-select"
        >
          <option value="none">No grouping</option>
          <option value="type">File Type</option>
          <option value="size">File Size</option>
          <option value="date">Date Modified</option>
        </select>
      </div>
    </div>
  );
};

// Add CSS styles
const style = document.createElement('style');
style.textContent = `
.file-filter {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 20px;
}

.search-form {
  display: flex;
  align-items: center;
  flex: 1;
  max-width: 600px;
}

.search-input {
  flex: 1;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px 0 0 4px;
  font-size: 16px;
}

.search-button {
  padding: 10px 20px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
  font-size: 16px;
}

.search-button:hover {
  background: #45a049;
}

.clear-button {
  padding: 10px 15px;
  background: #f44336;
  color: white;
  border: none;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
  font-size: 16px;
  margin-left: 5px;
}

.clear-button:hover {
  background: #d32f2f;
}

.group-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.group-select {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  background: white;
  cursor: pointer;
}
`;
document.head.appendChild(style);