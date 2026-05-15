"""Integration tests for Ingestion API endpoints"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime

from app.main import app
from app.models.sql.website import IngestionJob, IngestionJobStatus


client = TestClient(app)


def test_create_ingestion_job_endpoint():
    """Test creating an ingestion job via API"""
    # Mock the ingestion manager
    with patch('app.api.v1.endpoints.websites.ingestion_manager') as mock_manager:
        mock_job = IngestionJob(
            id=1,
            website_id=1,
            url="http://example.com/test.pdf",
            file_type="pdf",
            status=IngestionJobStatus.PENDING,
            created_at=datetime.utcnow()
        )
        mock_manager.create_ingestion_job.return_value = mock_job
        
        # Make API request
        response = client.post(
            "/api/v1/websites/1/ingestion",
            json={
                "url": "http://example.com/test.pdf",
                "file_type": "pdf"
            }
        )
        
        assert response.status_code == 201
        assert response.json()["id"] == 1
        assert response.json()["website_id"] == 1
        assert response.json()["status"] == "PENDING"


def test_get_ingestion_job_status():
    """Test getting ingestion job status"""
    # Mock the ingestion manager
    with patch('app.api.v1.endpoints.websites.ingestion_manager') as mock_manager:
        mock_job = IngestionJob(
            id=1,
            website_id=1,
            url="http://example.com/test.pdf",
            file_type="pdf",
            status=IngestionJobStatus.PROCESSING,
            created_at=datetime.utcnow()
        )
        mock_manager.get_ingestion_job.return_value = mock_job
        
        # Make API request
        response = client.get("/api/v1/websites/ingestion/1")
        
        assert response.status_code == 200
        assert response.json()["id"] == 1
        assert response.json()["status"] == "PROCESSING"


def test_list_ingestion_jobs():
    """Test listing ingestion jobs"""
    # Mock the ingestion manager
    with patch('app.api.v1.endpoints.websites.ingestion_manager') as mock_manager:
        mock_jobs = [
            IngestionJob(
                id=1,
                website_id=1,
                url="http://example.com/test1.pdf",
                file_type="pdf",
                status=IngestionJobStatus.COMPLETED
            ),
            IngestionJob(
                id=2,
                website_id=1,
                url="http://example.com/test2.pdf",
                file_type="pdf",
                status=IngestionJobStatus.PENDING
            )
        ]
        mock_manager.list_ingestion_jobs.return_value = mock_jobs
        
        # Make API request
        response = client.get("/api/v1/websites/1/ingestion")
        
        assert response.status_code == 200
        assert len(response.json()) == 2
        assert response.json()[0]["id"] == 1
        assert response.json()[1]["id"] == 2


def test_get_ingestion_statistics():
    """Test getting ingestion statistics"""
    # Mock the ingestion manager
    with patch('app.api.v1.endpoints.websites.ingestion_manager') as mock_manager:
        mock_stats = MagicMock()
        mock_stats.total_jobs = 10
        mock_stats.completed_jobs = 7
        mock_stats.failed_jobs = 2
        mock_stats.pending_jobs = 1
        mock_stats.avg_processing_time = 120.5
        
        mock_manager.get_job_statistics.return_value = mock_stats
        
        # Make API request
        response = client.get("/api/v1/websites/ingestion/stats")
        
        assert response.status_code == 200
        assert response.json()["total_jobs"] == 10
        assert response.json()["completed_jobs"] == 7
        assert response.json()["failed_jobs"] == 2


def test_file_preview_endpoint():
    """Test file preview endpoint"""
    # Mock the preview service
    with patch('app.api.v1.endpoints.websites.preview_service') as mock_service:
        mock_service.get_file_preview.return_value = "This is a preview of the file content..."
        
        # Make API request
        response = client.get("/api/v1/websites/preview?url=http://example.com/test.pdf")
        
        assert response.status_code == 200
        assert "preview of the file content" in response.json()["preview"]


def test_file_download_endpoint():
    """Test file download endpoint"""
    # Mock the preview service
    with patch('app.api.v1.endpoints.websites.preview_service') as mock_service:
        mock_service.download_file.return_value = ("/tmp/test.pdf", "test.pdf")
        
        # Make API request
        response = client.get("/api/v1/websites/download?url=http://example.com/test.pdf")
        
        assert response.status_code == 200
        assert response.json()["file_path"] == "/tmp/test.pdf"
        assert response.json()["filename"] == "test.pdf"


def test_schedule_management_endpoints():
    """Test schedule management endpoints"""
    # Mock the scheduling service
    with patch('app.api.v1.endpoints.websites.scheduling_service') as mock_service:
        # Test adding a schedule
        mock_service.add_website_schedule.return_value = "schedule_123"
        
        response = client.post(
            "/api/v1/websites/1/schedule",
            json={
                "frequency": "daily",
                "start_time": "09:00"
            }
        )
        
        assert response.status_code == 201
        assert response.json()["schedule_id"] == "schedule_123"
        
        # Test getting schedules
        mock_service.get_website_schedules.return_value = [
            {"schedule_id": "schedule_123", "frequency": "daily", "start_time": "09:00"}
        ]
        
        response = client.get("/api/v1/websites/1/schedule")
        
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["frequency"] == "daily"


def test_schedule_statistics_endpoint():
    """Test schedule statistics endpoint"""
    # Mock the scheduling service
    with patch('app.api.v1.endpoints.websites.scheduling_service') as mock_service:
        mock_stats = MagicMock()
        mock_stats.total_schedules = 5
        mock_stats.websites_with_schedules = 3
        mock_stats.next_scheduled_runs = [
            {"schedule_id": "schedule_1", "next_run": "2024-01-01T09:00:00"}
        ]
        
        mock_service.get_schedule_statistics.return_value = mock_stats
        
        # Make API request
        response = client.get("/api/v1/websites/schedule/stats")
        
        assert response.status_code == 200
        assert response.json()["total_schedules"] == 5
        assert response.json()["websites_with_schedules"] == 3


def test_ingestion_job_error_handling():
    """Test error handling for ingestion job endpoints"""
    # Test invalid website ID
    response = client.post(
        "/api/v1/websites/999/ingestion",
        json={
            "url": "http://example.com/test.pdf",
            "file_type": "pdf"
        }
    )
    
    assert response.status_code == 404
    
    # Test invalid job ID
    response = client.get("/api/v1/websites/ingestion/999")
    
    assert response.status_code == 404


def test_file_preview_error_handling():
    """Test error handling for file preview endpoint"""
    # Mock the preview service to raise an exception
    with patch('app.api.v1.endpoints.websites.preview_service') as mock_service:
        mock_service.get_file_preview.side_effect = Exception("File not found")
        
        # Make API request
        response = client.get("/api/v1/websites/preview?url=http://example.com/nonexistent.pdf")
        
        assert response.status_code == 404
        assert "File not found" in response.json()["detail"]


def test_schedule_error_handling():
    """Test error handling for schedule endpoints"""
    # Mock the scheduling service to raise an exception
    with patch('app.api.v1.endpoints.websites.scheduling_service') as mock_service:
        mock_service.add_website_schedule.side_effect = ValueError("Invalid frequency")
        
        # Make API request
        response = client.post(
            "/api/v1/websites/1/schedule",
            json={
                "frequency": "invalid",
                "start_time": "09:00"
            }
        )
        
        assert response.status_code == 400
        assert "Invalid frequency" in response.json()["detail"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
