import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FileList } from '../components/FileSelection';
import { getWebsiteDetail, triggerIngestion } from '../utils/api';

interface WebsiteDetail {
  id: number;
  url: string;
  title: string;
  description: string;
  status: string;
}

export const FileSelectionPage: React.FC = () => {
  const { websiteId } = useParams<{ websiteId: string }>();
  const [website, setWebsite] = useState<WebsiteDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [ingestionInProgress, setIngestionInProgress] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchWebsiteDetail = async () => {
      try {
        if (!websiteId) {
          setError('No website ID provided');
          return;
        }

        setLoading(true);
        const data = await getWebsiteDetail(parseInt(websiteId));
        setWebsite(data);
      } catch (err) {
        setError('Failed to load website details');
        console.error('Error fetching website:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchWebsiteDetail();
  }, [websiteId]);

  const handleStartIngestion = async () => {
    try {
      if (!websiteId || !website) return;

      setIngestionInProgress(true);
      const response = await triggerIngestion(parseInt(websiteId));
      
      // Show success message
      alert(`Ingestion started! ${response.jobs_created} jobs created.`);
      
      // Navigate to ingestion progress page
      if (response.job_ids && response.job_ids.length > 0) {
        navigate(`/ingestion/progress/${response.job_ids[0]}`);
      }
    } catch (err) {
      setError('Failed to start ingestion');
      console.error('Error starting ingestion:', err);
    } finally {
      setIngestionInProgress(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-page">
        <div className="spinner"></div>
        <p>Loading website details...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-page">
        <h2>Error</h2>
        <p>{error}</p>
        <button onClick={() => navigate('/websites')}>Back to Websites</button>
      </div>
    );
  }

  if (!website) {
    return (
      <div className="not-found-page">
        <h2>Website Not Found</h2>
        <button onClick={() => navigate('/websites')}>Back to Websites</button>
      </div>
    );
  }

  return (
    <div className="file-selection-page">
      <div className="page-header">
        <div className="website-info">
          <h1>{website.title || 'Untitled Website'}</h1>
          <p className="website-url">{website.url}</p>
          <p className="website-status">Status: {website.status}</p>
        </div>
        <div className="page-actions">
          <button 
            onClick={handleStartIngestion} 
            disabled={ingestionInProgress}
            className="ingestion-button"
          >
            {ingestionInProgress ? 'Starting Ingestion...' : 'Start Ingestion'}
          </button>
          <button 
            onClick={() => navigate('/websites')} 
            className="back-button"
          >
            Back to Websites
          </button>
        </div>
      </div>

      <div className="file-selection-content">
        <FileList websiteId={parseInt(websiteId)} />
      </div>
    </div>
  );
};

// Add CSS styles
const style = document.createElement('style');
style.textContent = `
.file-selection-page {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.website-info h1 {
  margin: 0;
  font-size: 24px;
  color: #333;
}

.website-url {
  color: #4CAF50;
  margin: 5px 0;
  word-break: break-all;
}

.website-status {
  color: #666;
  font-size: 14px;
}

.page-actions {
  display: flex;
  gap: 10px;
}

.ingestion-button {
  padding: 12px 24px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.ingestion-button:hover {
  background: #45a049;
}

.ingestion-button:disabled {
  background: #cccccc;
  cursor: not-allowed;
}

.back-button {
  padding: 12px 24px;
  background: #f5f5f5;
  color: #333;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.back-button:hover {
  background: #eeeeee;
}

.file-selection-content {
  margin-top: 20px;
}

.loading-page, .error-page, .not-found-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 50px;
  text-align: center;
}

.loading-page .spinner {
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

.error-page, .not-found-page {
  color: #d32f2f;
}

.error-page button, .not-found-page button {
  margin-top: 20px;
  padding: 10px 20px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
`;
document.head.appendChild(style);