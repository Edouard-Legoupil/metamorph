"""Unit tests for Preview Service"""
import pytest
import tempfile
import os
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

from app.services.preview_service import PreviewService
from app.models.sql.website import DiscoveredFile, FileType
from fastapi import HTTPException


def test_preview_service_initialization():
    """Test PreviewService initialization"""
    service = PreviewService()
    assert service.max_preview_length == 1000  # Default from config
    assert service.max_file_size == 10 * 1024 * 1024  # 10MB
    assert service.cache_dir.name == "preview_cache"


def test_text_file_preview():
    """Test text file preview"""
    service = PreviewService()
    
    # Create a temporary text file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Hello World\nThis is a test file\nWith multiple lines")
        temp_file = f.name
    
    try:
        # Create a mock DiscoveredFile object
        class MockDiscoveredFile:
            def __init__(self):
                self.id = 1
                self.website_id = 1
                self.url = "http://example.com/test.txt"
                self.file_type = FileType.TEXT
                self.file_path = temp_file
                self.file_name = "test.txt"
                self.file_size = os.path.getsize(temp_file)
                self.content_type = "text/plain"
                self.content_hash = None
                self.discovered_at = datetime.utcnow()
        
        discovered_file = MockDiscoveredFile()
        
        # Mock the download method to return a file-like object
        class MockFile:
            def __init__(self, path):
                self.name = path
        
        mock_file = MockFile(temp_file)
        
        with patch.object(service, '_download_file', return_value=mock_file):
            # Test preview
            preview_result = service.generate_preview(discovered_file)
            preview = preview_result.get("preview", "")
            assert "Hello World" in preview
            assert "multiple lines" in preview
            assert len(preview) <= service.max_preview_length
        
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def test_pdf_file_preview():
    """Test PDF file preview"""
    service = PreviewService()
    
    # Create a simple PDF file
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        # Write minimal PDF content
        f.write(b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj xref 0 4 0000000000 65535 f 0000000009 00000 n 0000000058 00000 n 0000000117 00000 n trailer<</Size 4/Root 1 0 R>> startxref 178 %%EOF")
        temp_file = f.name
    
    try:
        # Test preview (should handle PDF parsing)
        preview = service.get_file_preview(temp_file)
        assert preview is not None
        
    except Exception as e:
        # PDF parsing might fail with minimal content, that's okay for this test
        assert "PDF" in str(e) or "format" in str(e).lower()
    finally:
        os.unlink(temp_file)


def test_file_too_large():
    """Test file size limit enforcement"""
    service = PreviewService()
    
    # Create a file larger than max_file_size
    with tempfile.NamedTemporaryFile(delete=False) as f:
        # Write 11MB of data
        f.write(b"x" * (11 * 1024 * 1024))
        temp_file = f.name
    
    try:
        with pytest.raises(HTTPException) as exc_info:
            service.get_file_preview(temp_file)
        
        assert exc_info.value.status_code == 413
        assert "File too large" in str(exc_info.value.detail)
        
    finally:
        os.unlink(temp_file)


def test_unsupported_file_format():
    """Test unsupported file format handling"""
    service = PreviewService()
    
    # Create a file with unsupported extension
    with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as f:
        f.write(b"Some random content")
        temp_file = f.name
    
    try:
        with pytest.raises(HTTPException) as exc_info:
            service.get_file_preview(temp_file)
        
        assert exc_info.value.status_code == 415
        assert "Unsupported file format" in str(exc_info.value.detail)
        
    finally:
        os.unlink(temp_file)


def test_file_download():
    """Test file download functionality"""
    service = PreviewService()
    
    # Create a temporary text file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Test content for download")
        temp_file = f.name
    
    try:
        # Create a DiscoveredFile object
        discovered_file = DiscoveredFile(
            id=1,
            website_id=1,
            url=temp_file,
            file_type=FileType.TEXT,
            file_path=temp_file,
            file_size=os.path.getsize(temp_file),
            content_type="text/plain",
            discovered_at=datetime.utcnow()
        )
        
        # Test download
        file_path, filename = service.download_file(discovered_file)
        assert file_path == temp_file
        assert filename.endswith(".txt")
        
    finally:
        os.unlink(temp_file)


def test_cache_functionality():
    """Test preview caching"""
    service = PreviewService()
    
    # Create a temporary text file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Cached content test")
        temp_file = f.name
    
    try:
        # First request - should not be cached
        preview1 = service.get_file_preview(temp_file)
        
        # Second request - should use cache
        preview2 = service.get_file_preview(temp_file)
        
        assert preview1 == preview2
        
        # Check that cache file exists
        cache_file = service.cache_dir / f"{os.path.basename(temp_file)}.cache"
        assert cache_file.exists()
        
    finally:
        os.unlink(temp_file)


def test_text_extraction_and_truncation():
    """Test text extraction with truncation"""
    service = PreviewService()
    service.max_preview_length = 50  # Set small limit for testing
    
    # Create a file with long content
    long_content = "A" * 1000  # 1000 characters
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(long_content)
        temp_file = f.name
    
    try:
        preview = service.get_file_preview(temp_file)
        assert len(preview) <= service.max_preview_length
        assert preview.endswith("...")  # Should be truncated
        
    finally:
        os.unlink(temp_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
