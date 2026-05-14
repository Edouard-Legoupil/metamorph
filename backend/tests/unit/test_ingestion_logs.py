"""Unit tests for Ingestion Logs Service"""
import pytest
import tempfile
import os
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

from app.services.ingestion_logs import IngestionLogsService, IngestionLog


def test_ingestion_logs_initialization():
    """Test IngestionLogsService initialization"""
    service = IngestionLogsService()
    assert service.logs_dir.exists()
    assert service.max_log_size == 10 * 1024 * 1024  # 10MB
    assert service.logger is not None


def test_log_message_creation():
    """Test log message creation"""
    service = IngestionLogsService()
    
    # Test basic log message
    log_entry = service.log_message(
        job_id=1,
        level="INFO",
        message="Test log message",
        context={"key": "value"}
    )
    
    assert log_entry is not None
    assert log_entry.job_id == 1
    assert log_entry.level == "INFO"
    assert log_entry.message == "Test log message"
    assert log_entry.context["key"] == "value"
    assert log_entry.timestamp is not None


def test_log_file_creation():
    """Test log file creation and structure"""
    service = IngestionLogsService()
    job_id = 123
    
    # Log a message to create the file
    service.log_message(job_id, "INFO", "Test message")
    
    # Check that log file exists
    log_file = service._get_job_log_file(job_id)
    assert log_file.exists()
    
    # Check file content structure
    content = log_file.read_text()
    assert "# Ingestion Job Log" in content
    assert f"# Job ID: {job_id}" in content
    assert "# Started:" in content
    assert "# Format:" in content
    assert f"[{log_entry.timestamp}] [INFO] Test message" in content


def test_get_job_logs():
    """Test retrieving logs for a specific job"""
    service = IngestionLogsService()
    job_id = 456
    
    # Add some log entries
    service.log_message(job_id, "INFO", "First message", {"step": 1})
    service.log_message(job_id, "WARNING", "Warning message", {"step": 2})
    service.log_message(job_id, "ERROR", "Error message", {"step": 3})
    
    # Retrieve logs
    logs = service.get_job_logs(job_id)
    
    assert len(logs) == 3
    assert logs[0]["level"] == "INFO"
    assert logs[1]["level"] == "WARNING"
    assert logs[2]["level"] == "ERROR"
    assert all(log["job_id"] == job_id for log in logs)


def test_get_job_logs_with_level_filter():
    """Test retrieving logs with level filtering"""
    service = IngestionLogsService()
    job_id = 789
    
    # Add log entries with different levels
    service.log_message(job_id, "INFO", "Info message")
    service.log_message(job_id, "WARNING", "Warning message")
    service.log_message(job_id, "ERROR", "Error message")
    service.log_message(job_id, "INFO", "Another info message")
    
    # Retrieve only ERROR logs
    error_logs = service.get_job_logs(job_id, level="ERROR")
    assert len(error_logs) == 1
    assert error_logs[0]["level"] == "ERROR"
    
    # Retrieve only INFO logs
    info_logs = service.get_job_logs(job_id, level="INFO")
    assert len(info_logs) == 2
    assert all(log["level"] == "INFO" for log in info_logs)


def test_get_job_logs_with_limit():
    """Test retrieving logs with limit"""
    service = IngestionLogsService()
    job_id = 101
    
    # Add many log entries
    for i in range(10):
        service.log_message(job_id, "INFO", f"Message {i}")
    
    # Retrieve with limit
    limited_logs = service.get_job_logs(job_id, limit=5)
    assert len(limited_logs) == 5


def test_get_job_log_file_content():
    """Test getting raw log file content"""
    service = IngestionLogsService()
    job_id = 202
    
    # Add some log entries
    service.log_message(job_id, "INFO", "Test message 1")
    service.log_message(job_id, "WARNING", "Test message 2")
    
    # Get raw content
    content = service.get_job_log_file_content(job_id)
    
    assert "# Ingestion Job Log" in content
    assert "Test message 1" in content
    assert "Test message 2" in content


def test_download_job_logs():
    """Test downloading job logs"""
    service = IngestionLogsService()
    job_id = 303
    
    # Add some log entries
    service.log_message(job_id, "INFO", "Download test message")
    
    # Test download
    file_path, filename = service.download_job_logs(job_id)
    
    assert file_path is not None
    assert filename.startswith(f"ingestion_job_{job_id}_")
    assert filename.endswith(".log")
    assert Path(file_path).exists()


def test_download_nonexistent_job_logs():
    """Test downloading logs for nonexistent job"""
    service = IngestionLogsService()
    
    # Try to download logs for job that doesn't exist
    with pytest.raises(Exception) as exc_info:
        service.download_job_logs(999999)
    
    assert "No logs found" in str(exc_info.value)


def test_get_all_job_logs_summary():
    """Test getting summary of all job logs"""
    service = IngestionLogsService()
    
    # Create logs for multiple jobs
    job_ids = [1001, 1002, 1003]
    for job_id in job_ids:
        service.log_message(job_id, "INFO", f"Log for job {job_id}")
        service.log_message(job_id, "WARNING", f"Warning for job {job_id}")
    
    # Get summary
    summary = service.get_all_job_logs_summary()
    
    assert len(summary) == 3
    assert all(item["job_id"] in job_ids for item in summary)
    assert all(item["line_count"] >= 2 for item in summary)
    assert all(item["file_size"] > 0 for item in summary)


def test_clear_job_logs():
    """Test clearing logs for a job"""
    service = IngestionLogsService()
    job_id = 404
    
    # Add some log entries
    service.log_message(job_id, "INFO", "Message to be cleared")
    service.log_message(job_id, "WARNING", "Another message")
    
    # Verify logs exist
    log_file = service._get_job_log_file(job_id)
    assert log_file.exists()
    
    # Clear logs
    result = service.clear_job_logs(job_id)
    assert result["success"] is True
    
    # Verify logs are cleared
    assert not log_file.exists()


def test_clear_nonexistent_job_logs():
    """Test clearing logs for nonexistent job"""
    service = IngestionLogsService()
    
    # Try to clear logs for job that doesn't exist
    result = service.clear_job_logs(999999)
    assert result["success"] is True
    assert "No logs found" in result["message"]


def test_get_logs_with_filter():
    """Test getting logs with various filters"""
    service = IngestionLogsService()
    
    # Create logs for multiple jobs with different timestamps
    job_ids = [501, 502]
    
    # Add logs with different timestamps
    now = datetime.utcnow()
    past_time = (now - timedelta(hours=2)).isoformat()
    future_time = (now + timedelta(hours=2)).isoformat()
    
    for job_id in job_ids:
        service.log_message(job_id, "INFO", "Old message", {"timestamp": past_time})
        service.log_message(job_id, "WARNING", "Current message")
        service.log_message(job_id, "ERROR", "Future message", {"timestamp": future_time})
    
    # Test time range filtering
    current_time = now.isoformat()
    recent_logs = service.get_logs_with_filter(
        start_time=(now - timedelta(hours=1)).isoformat(),
        end_time=(now + timedelta(hours=1)).isoformat()
    )
    
    # Should get current messages
    assert len(recent_logs) >= 2
    assert all("Current message" in log["message"] for log in recent_logs)


def test_get_logs_with_search_query():
    """Test getting logs with search query"""
    service = IngestionLogsService()
    job_id = 606
    
    # Add logs with different content
    service.log_message(job_id, "INFO", "This is a test message about funding")
    service.log_message(job_id, "WARNING", "Warning about processing")
    service.log_message(job_id, "ERROR", "Error in the funding process")
    
    # Search for "funding"
    funding_logs = service.get_logs_with_search_query("funding")
    assert len(funding_logs) == 2
    assert all("funding" in log["message"].lower() for log in funding_logs)


def test_get_job_log_stats():
    """Test getting statistics for job logs"""
    service = IngestionLogsService()
    job_id = 707
    
    # Add logs with different levels
    service.log_message(job_id, "INFO", "Info message 1")
    service.log_message(job_id, "INFO", "Info message 2")
    service.log_message(job_id, "WARNING", "Warning message")
    service.log_message(job_id, "ERROR", "Error message 1")
    service.log_message(job_id, "ERROR", "Error message 2")
    service.log_message(job_id, "ERROR", "Error message 3")
    
    # Get statistics
    stats = service.get_job_log_stats(job_id)
    
    assert stats["job_id"] == job_id
    assert stats["total_logs"] == 6
    assert stats["levels"]["INFO"] == 2
    assert stats["levels"]["WARNING"] == 1
    assert stats["levels"]["ERROR"] == 3
    assert stats["error_count"] == 3
    assert stats["warning_count"] == 1


def test_get_job_log_stats_nonexistent_job():
    """Test getting statistics for nonexistent job"""
    service = IngestionLogsService()
    
    # Get statistics for job that doesn't exist
    stats = service.get_job_log_stats(999999)
    
    assert stats["job_id"] == 999999
    assert stats["total_logs"] == 0
    assert stats["error_count"] == 0


def test_export_logs_csv():
    """Test exporting logs as CSV"""
    service = IngestionLogsService()
    job_id = 808
    
    # Add some log entries
    service.log_message(job_id, "INFO", "CSV test message 1", {"key": "value1"})
    service.log_message(job_id, "WARNING", "CSV test message 2", {"key": "value2"})
    
    # Export as CSV
    csv_content = service.export_logs_csv(job_id=job_id)
    
    assert "timestamp,level,message,context,job_id" in csv_content
    assert "CSV test message 1" in csv_content
    assert "CSV test message 2" in csv_content
    assert str(job_id) in csv_content


def test_integrate_with_ingestion_manager():
    """Test integration with ingestion manager"""
    service = IngestionLogsService()
    
    # Mock ingestion manager
    mock_manager = MagicMock()
    mock_manager.process_ingestion_job = MagicMock()
    
    # Integrate
    integrated_manager = service.integrate_with_ingestion_manager(mock_manager)
    
    assert integrated_manager is not None
    assert hasattr(integrated_manager, 'process_ingestion_job')
    
    # Test that the integrated method logs events
    mock_db = MagicMock()
    
    # Mock the original method to return a result
    mock_manager.process_ingestion_job.return_value = {"status": "completed"}
    
    # Call the integrated method
    result = integrated_manager.process_ingestion_job(mock_db, 123)
    
    # Verify that log messages were created
    log_file = service._get_job_log_file(123)
    assert log_file.exists()
    
    content = log_file.read_text()
    assert "Ingestion job started" in content
    assert "Ingestion job completed" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
