"""Unit tests for Ingestion Manager"""
import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime

from app.services.ingestion_manager import IngestionManager
from app.models.sql.website import IngestionJob, IngestionJobStatus


def test_ingestion_manager_initialization():
    """Test IngestionManager initialization"""
    manager = IngestionManager()
    assert manager.job_timeout == 3600  # 1 hour
    assert manager.max_retries == 3
    assert manager.max_file_size == 50 * 1024 * 1024  # 50MB


@pytest.mark.asyncio
async def test_create_ingestion_job():
    """Test creating an ingestion job"""
    manager = IngestionManager()
    
    # Mock database session
    mock_db = MagicMock()
    
    # Mock job creation
    mock_job = IngestionJob(
        id=1,
        website_id=1,
        url="http://example.com/test.pdf",
        file_type="pdf",
        status=IngestionJobStatus.PENDING,
        created_at=datetime.utcnow()
    )
    
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None
    
    with patch.object(manager, '_get_next_job_id', return_value=1):
        with patch('app.services.ingestion_manager.IngestionJob', return_value=mock_job):
            job = await manager.create_ingestion_job(
                mock_db, 
                website_id=1, 
                url="http://example.com/test.pdf",
                file_type="pdf"
            )
            
            assert job is not None
            assert job.website_id == 1
            assert job.url == "http://example.com/test.pdf"
            assert job.status == IngestionJobStatus.PENDING


@pytest.mark.asyncio
async def test_validate_file_url():
    """Test file URL validation"""
    manager = IngestionManager()
    
    # Test valid URL
    valid_url = "http://example.com/test.pdf"
    assert manager._validate_file_url(valid_url) == valid_url
    
    # Test invalid URL
    invalid_url = "not-a-url"
    with pytest.raises(ValueError):
        manager._validate_file_url(invalid_url)


@pytest.mark.asyncio
async def test_download_file():
    """Test file download functionality"""
    manager = IngestionManager()
    
    # Create a temporary file to simulate download
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Test content for download")
        temp_file = f.name
    
    try:
        # Mock httpx download
        mock_response = MagicMock()
        mock_response.iter_bytes.return_value = [b"Test content for download"]
        
        with patch('app.services.ingestion_manager.httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            download_path = await manager._download_file("http://example.com/test.txt")
            
            assert download_path.exists()
            assert download_path.read_text() == "Test content for download"
            download_path.unlink()
            
    finally:
        os.unlink(temp_file)


@pytest.mark.asyncio
async def test_file_too_large():
    """Test file size limit enforcement"""
    manager = IngestionManager()
    
    # Mock large file download
    mock_response = MagicMock()
    mock_response.iter_bytes.return_value = [b"x" * (51 * 1024 * 1024)]  # 51MB
    
    with patch('app.services.ingestion_manager.httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        
        with pytest.raises(ValueError) as exc_info:
            await manager._download_file("http://example.com/large.txt")
        
        assert "File too large" in str(exc_info.value)


@pytest.mark.asyncio
async def test_select_parser():
    """Test parser selection"""
    manager = IngestionManager()
    
    # Test PDF parser selection
    parser = manager._select_parser("test.pdf")
    assert parser is not None
    
    # Test unsupported format
    with pytest.raises(ValueError):
        manager._select_parser("test.xyz")


@pytest.mark.asyncio
async def test_extract_metadata():
    """Test metadata extraction"""
    manager = IngestionManager()
    
    # Create a temporary PDF file
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        # Write minimal PDF content
        f.write(b"%PDF-1.4\n%%Title: Test Document\n%%Author: Test Author\n1 0 obj<</Type/Catalog>>endobj xref 0 1 0000000000 65535 f trailer<</Size 1/Root 1 0 R>> startxref 67 %%EOF")
        temp_file = f.name
    
    try:
        metadata = manager._extract_metadata(temp_file)
        assert metadata is not None
        # PDF metadata extraction might not work with minimal content
        
    finally:
        os.unlink(temp_file)


@pytest.mark.asyncio
async def test_update_job_status():
    """Test job status updates"""
    manager = IngestionManager()
    
    # Mock database session
    mock_db = MagicMock()
    
    # Create a mock job
    mock_job = IngestionJob(
        id=1,
        website_id=1,
        url="http://example.com/test.pdf",
        file_type="pdf",
        status=IngestionJobStatus.PENDING
    )
    
    # Test status update
    updated_job = manager._update_job_status(mock_job, IngestionJobStatus.PROCESSING)
    assert updated_job.status == IngestionJobStatus.PROCESSING


@pytest.mark.asyncio
async def test_job_retry_logic():
    """Test job retry logic"""
    manager = IngestionManager()
    
    # Create a job with retries
    job = IngestionJob(
        id=1,
        website_id=1,
        url="http://example.com/test.pdf",
        file_type="pdf",
        status=IngestionJobStatus.PENDING,
        retry_count=1
    )
    
    # Test should retry
    assert manager._should_retry(job)
    
    # Test should not retry (max retries reached)
    job.retry_count = manager.max_retries
    assert not manager._should_retry(job)


@pytest.mark.asyncio
async def test_get_job_statistics():
    """Test job statistics calculation"""
    manager = IngestionManager()
    
    # Mock database session with query results
    mock_db = MagicMock()
    
    # Mock query results
    mock_query = MagicMock()
    mock_query.filter.return_value.count.return_value = 5
    mock_query.filter.return_value.all.return_value = [
        IngestionJob(status=IngestionJobStatus.COMPLETED),
        IngestionJob(status=IngestionJobStatus.COMPLETED),
        IngestionJob(status=IngestionJobStatus.FAILED),
    ]
    
    mock_db.query.return_value = mock_query
    
    stats = manager.get_job_statistics(mock_db)
    assert stats.total_jobs == 5
    assert stats.completed_jobs == 2
    assert stats.failed_jobs == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
