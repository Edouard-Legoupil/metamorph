"""Unit tests for Scheduling Service"""
import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from app.services.scheduling_service import SchedulingService


def test_scheduling_service_initialization():
    """Test SchedulingService initialization"""
    service = SchedulingService()
    assert service.scheduler is not None
    assert service.change_detection_enabled is True
    assert service.max_concurrent_jobs == 5


def test_add_website_schedule():
    """Test adding website schedule"""
    service = SchedulingService()
    
    # Test adding a schedule
    website_id = 1
    frequency = "daily"
    start_time = "09:00"
    
    schedule_id = service.add_website_schedule(website_id, frequency, start_time)
    assert schedule_id is not None
    assert isinstance(schedule_id, str)


def test_remove_website_schedule():
    """Test removing website schedule"""
    service = SchedulingService()
    
    # Add a schedule first
    website_id = 1
    schedule_id = service.add_website_schedule(website_id, "daily", "09:00")
    
    # Remove the schedule
    result = service.remove_website_schedule(schedule_id)
    assert result is True


def test_get_website_schedules():
    """Test getting website schedules"""
    service = SchedulingService()
    
    # Add some schedules
    website_id = 1
    schedule_id1 = service.add_website_schedule(website_id, "daily", "09:00")
    schedule_id2 = service.add_website_schedule(website_id, "weekly", "10:00")
    
    # Get schedules for website
    schedules = service.get_website_schedules(website_id)
    assert len(schedules) == 2
    assert any(sched['frequency'] == 'daily' for sched in schedules)
    assert any(sched['frequency'] == 'weekly' for sched in schedules)


def test_get_all_schedules():
    """Test getting all schedules"""
    service = SchedulingService()
    
    # Add schedules for different websites
    service.add_website_schedule(1, "daily", "09:00")
    service.add_website_schedule(2, "hourly", "10:00")
    
    # Get all schedules
    all_schedules = service.get_all_schedules()
    assert len(all_schedules) == 2


def test_update_schedule():
    """Test updating a schedule"""
    service = SchedulingService()
    
    # Add a schedule
    website_id = 1
    schedule_id = service.add_website_schedule(website_id, "daily", "09:00")
    
    # Update the schedule
    result = service.update_schedule(schedule_id, frequency="weekly", start_time="10:00")
    assert result is True
    
    # Verify update
    schedules = service.get_website_schedules(website_id)
    assert len(schedules) == 1
    assert schedules[0]['frequency'] == 'weekly'
    assert schedules[0]['start_time'] == '10:00'


def test_get_schedule_statistics():
    """Test schedule statistics"""
    service = SchedulingService()
    
    # Add some schedules
    service.add_website_schedule(1, "daily", "09:00")
    service.add_website_schedule(1, "weekly", "10:00")
    service.add_website_schedule(2, "hourly", "11:00")
    
    # Get statistics
    stats = service.get_schedule_statistics()
    assert stats.total_schedules == 3
    assert stats.websites_with_schedules == 2


def test_change_detection():
    """Test change detection functionality"""
    service = SchedulingService()
    
    # Test with no previous content
    previous_content = None
    current_content = "<html><body>Test content</body></html>"
    
    has_changed = service._detect_content_changes(previous_content, current_content)
    assert has_changed is True
    
    # Test with same content
    has_changed = service._detect_content_changes(current_content, current_content)
    assert has_changed is False
    
    # Test with different content
    new_content = "<html><body>Different content</body></html>"
    has_changed = service._detect_content_changes(current_content, new_content)
    assert has_changed is True


def test_schedule_frequency_validation():
    """Test schedule frequency validation"""
    service = SchedulingService()
    
    # Test valid frequencies
    valid_frequencies = ["hourly", "daily", "weekly", "monthly"]
    for freq in valid_frequencies:
        assert service._validate_frequency(freq) is True
    
    # Test invalid frequency
    assert service._validate_frequency("yearly") is False
    assert service._validate_frequency("invalid") is False


def test_time_format_validation():
    """Test time format validation"""
    service = SchedulingService()
    
    # Test valid time formats
    assert service._validate_time_format("09:00") is True
    assert service._validate_time_format("14:30") is True
    assert service._validate_time_format("23:59") is True
    
    # Test invalid time formats
    assert service._validate_time_format("9:00") is False  # Missing leading zero
    assert service._validate_time_format("0900") is False  # Missing colon
    assert service._validate_time_format("24:00") is False  # Invalid hour
    assert service._validate_time_format("12:60") is False  # Invalid minute


def test_scheduler_start_stop():
    """Test scheduler start/stop functionality"""
    service = SchedulingService()
    
    # Test that scheduler is running
    assert service.scheduler.running is True
    
    # Test stopping scheduler
    service.stop()
    assert service.scheduler.running is False
    
    # Test starting scheduler again
    service.start()
    assert service.scheduler.running is True


def test_get_next_run_time():
    """Test getting next run time for a schedule"""
    service = SchedulingService()
    
    # Add a schedule
    website_id = 1
    schedule_id = service.add_website_schedule(website_id, "daily", "09:00")
    
    # Get next run time
    next_run = service.get_next_run_time(schedule_id)
    assert next_run is not None
    assert isinstance(next_run, datetime)


def test_get_schedule_by_id():
    """Test getting schedule by ID"""
    service = SchedulingService()
    
    # Add a schedule
    website_id = 1
    schedule_id = service.add_website_schedule(website_id, "daily", "09:00")
    
    # Get schedule by ID
    schedule = service.get_schedule_by_id(schedule_id)
    assert schedule is not None
    assert schedule['website_id'] == website_id
    assert schedule['frequency'] == 'daily'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
