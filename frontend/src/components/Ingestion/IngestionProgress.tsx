import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getIngestionJobStatus } from '../../utils/api';

interface IngestionJobStatus {
  job_id: number;
  file_id: number;
  status: string;
  job_type: string;
  priority: number;
  retry_count: number;
  max_retries: number;
  error_message: string | null;
  parser_used: string | null;
  entities_extracted: number;
  relationships_extracted: number;
  queued_at: string | null;
  started_at: string | null;
  completed_at: string | null;
  duration_seconds: number | null;
}

export const IngestionProgress: React.FC = () => {
  const { jobId } = useParams<{ jobId: string }>();
  const [jobStatus, setJobStatus] = useState<IngestionJobStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState('Initializing...');
  const navigate = useNavigate();

  const statusSteps = [
    { status: 'PENDING', label: 'Waiting in queue', progress: 10 },
    { status: 'PROCESSING', label: 'Processing file', progress: 40 },
    { status: 'COMPLETED', label: 'Ingestion completed', progress: 100 },
    { status: 'FAILED', label: 'Ingestion failed', progress: 0 }
  ];

  const fetchJobStatus = async () => {
    try {
      if (!jobId) {
        setError('No job ID provided');
        return;
      }

      const response = await getIngestionJobStatus(parseInt(jobId));
      setJobStatus(response);
      
      // Update progress based on status
      const step = statusSteps.find(s => s.status === response.status) || statusSteps[0];
      setCurrentStep(step.label);
      setProgress(step.progress);
      
    } catch (err) {
      setError('Failed to fetch job status');
      console.error('Error fetching job status:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobStatus();
    
    // Poll for status updates every 3 seconds
    const interval = setInterval(fetchJobStatus, 3000);
    
    return () => clearInterval(interval);
  }, [jobId]);

  const getStatusColor = () => {
    if (!jobStatus) return '#999';
    switch (jobStatus.status) {
      case 'COMPLETED': return '#4CAF50';
      case 'FAILED': return '#f44336';
      case 'PROCESSING': return '#2196F3';
      default: return '#FF9800';
    }
  };

  const formatDuration = (seconds: number | null) => {
    if (!seconds) return 'N/A';
    if (seconds < 60) return `${seconds}s`;
    return `${(seconds / 60).toFixed(2)}min`;
  };

  const formatTimestamp = (timestamp: string | null) => {
    if (!timestamp) return 'N/A';
    return new Date(timestamp).toLocaleString();
  };

  if (loading && !jobStatus) {
    return (
      <div className="loading-page">
        <div className="spinner"></div>
        <p>Loading ingestion progress...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-page">
        <h2>Error</h2>
        <p>{error}</p>
        <button onClick={() => fetchJobStatus()}>Retry</button>
        <button onClick={() => navigate('/websites')} style={{ marginLeft: '10px' }}>
          Back to Websites
        </button>
      </div>
    );
  }

  if (!jobStatus) {
    return (
      <div className="not-found-page">
        <h2>Job Not Found</h2>
        <button onClick={() => navigate('/websites')}>Back to Websites</button>
      </div>
    );
  }

  return (
    <div className="ingestion-progress-page">
      <div className="progress-header">
        <h1>Ingestion Progress</h1>
        <p>Job ID: {jobStatus.job_id}</p>
        <div className="status-badge" style={{ backgroundColor: getStatusColor() }}>
          {jobStatus.status}
        </div>
      </div>

      <div className="progress-bar-container">
        <div className="progress-bar" style={{ width: `${progress}%` }}></div>
        <span className="progress-text">{progress}%</span>
      </div>

      <div className="current-step">
        <h3>Current Step</h3>
        <p>{currentStep}</p>
      </div>

      <div className="job-details">
        <h3>Job Details</h3>
        <div className="details-grid">
          <div className="detail-item">
            <span className="detail-label">Job Type:</span>
            <span className="detail-value">{jobStatus.job_type}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">File ID:</span>
            <span className="detail-value">{jobStatus.file_id}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Parser:</span>
            <span className="detail-value">{jobStatus.parser_used || 'Not started'}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Priority:</span>
            <span className="detail-value">{jobStatus.priority}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Retries:</span>
            <span className="detail-value">{jobStatus.retry_count} of {jobStatus.max_retries}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Entities Extracted:</span>
            <span className="detail-value">{jobStatus.entities_extracted}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Relationships Extracted:</span>
            <span className="detail-value">{jobStatus.relationships_extracted}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Duration:</span>
            <span className="detail-value">{formatDuration(jobStatus.duration_seconds)}</span>
          </div>
        </div>
      </div>

      <div className="timeline">
        <h3>Timeline</h3>
        <div className="timeline-steps">
          <div className={`timeline-step ${jobStatus.queued_at ? 'completed' : ''}`}>
            <div className="step-icon">⏳</div>
            <div className="step-info">
              <div className="step-name">Queued</div>
              <div className="step-time">{formatTimestamp(jobStatus.queued_at)}</div>
            </div>
          </div>
          
          <div className={`timeline-step ${jobStatus.started_at ? 'completed' : ''}`}>
            <div className="step-icon">▶️</div>
            <div className="step-info">
              <div className="step-name">Started</div>
              <div className="step-time">{formatTimestamp(jobStatus.started_at)}</div>
            </div>
          </div>
          
          <div className={`timeline-step ${jobStatus.completed_at ? 'completed' : ''}`}>
            <div className="step-icon">{jobStatus.status === 'COMPLETED' ? '✅' : jobStatus.status === 'FAILED' ? '❌' : '⏳'}</div>
            <div className="step-info">
              <div className="step-name">{jobStatus.status === 'COMPLETED' ? 'Completed' : jobStatus.status === 'FAILED' ? 'Failed' : 'Pending'}</div>
              <div className="step-time">{formatTimestamp(jobStatus.completed_at)}</div>
            </div>
          </div>
        </div>
      </div>

      {jobStatus.error_message && (
        <div className="error-section">
          <h3>Error Details</h3>
          <div className="error-message">
            <pre>{jobStatus.error_message}</pre>
          </div>
        </div>
      )}

      <div className="progress-actions">
        <button onClick={() => fetchJobStatus()} disabled={loading}>
          {loading ? 'Refreshing...' : 'Refresh Status'}
        </button>
        <button onClick={() => navigate('/websites')}>
          Back to Websites
        </button>
        {jobStatus.status === 'COMPLETED' && (
          <button onClick={() => navigate(`/websites/${jobStatus.file_id}/files`)}>
            View Files
          </button>
        )}
      </div>
    </div>
  );
};

// Add CSS styles
const style = document.createElement('style');
style.textContent = `
.ingestion-progress-page {
  padding: 20px;
  max-width: 1000px;
  margin: 0 auto;
}

.progress-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.progress-header h1 {
  margin: 0;
  font-size: 24px;
  color: #333;
}

.status-badge {
  padding: 8px 16px;
  border-radius: 20px;
  color: white;
  font-weight: bold;
  font-size: 14px;
}

.progress-bar-container {
  height: 30px;
  background: #f5f5f5;
  border-radius: 15px;
  margin: 30px 0;
  overflow: hidden;
  position: relative;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #4CAF50, #45a049);
  transition: width 0.3s ease;
  border-radius: 15px;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-weight: bold;
  font-size: 14px;
}

.current-step {
  background: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
  margin: 20px 0;
  border: 1px solid #eee;
}

.current-step h3 {
  margin-top: 0;
  color: #666;
  font-size: 16px;
}

.job-details {
  margin: 30px 0;
}

.job-details h3 {
  margin-top: 0;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.detail-item {
  background: #f9f9f9;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #eee;
}

.detail-label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
}

.detail-value {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.timeline {
  margin: 30px 0;
}

.timeline h3 {
  margin-top: 0;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.timeline-steps {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
  position: relative;
}

.timeline-steps::before {
  content: '';
  position: absolute;
  top: 20px;
  left: 0;
  right: 0;
  height: 2px;
  background: #ddd;
  z-index: 1;
}

.timeline-step {
  position: relative;
  z-index: 2;
  text-align: center;
  flex: 1;
}

.timeline-step.completed .step-icon {
  background: #4CAF50;
  color: white;
}

.timeline-step:not(.completed) .step-icon {
  background: #ddd;
  color: #999;
}

.step-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  font-size: 20px;
  background: #ddd;
}

.step-info {
  margin-top: 10px;
  font-size: 12px;
}

.step-name {
  font-weight: bold;
  color: #333;
}

.step-time {
  color: #666;
  font-size: 11px;
}

.error-section {
  background: #ffebee;
  border: 1px solid #f44336;
  border-radius: 8px;
  padding: 15px;
  margin: 20px 0;
}

.error-section h3 {
  margin-top: 0;
  color: #d32f2f;
}

.error-message {
  background: white;
  border: 1px solid #ffcdd2;
  border-radius: 4px;
  padding: 10px;
  margin-top: 10px;
  overflow-x: auto;
  max-height: 200px;
  overflow-y: auto;
}

.error-message pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-size: 13px;
  color: #d32f2f;
}

.progress-actions {
  display: flex;
  gap: 10px;
  margin-top: 30px;
}

.progress-actions button {
  padding: 12px 24px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.progress-actions button:hover {
  background: #45a049;
}

.progress-actions button:disabled {
  background: #cccccc;
  cursor: not-allowed;
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