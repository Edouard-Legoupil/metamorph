"""
Tests for URL validation functionality (FR-001)
"""
import pytest
from pydantic import ValidationError


def test_validate_url_valid_http():
    """Test validation of valid HTTP URL"""
    from app.services.website_crawler.url_validator import validate_url, URLValidationError
    
    # Should not raise for valid URLs
    result = validate_url("http://example.com")
    assert result == "http://example.com"
    
    result = validate_url("https://example.com")
    assert result == "https://example.com"
    
    result = validate_url("https://www.unhcr.org/refugees")
    assert result == "https://www.unhcr.org/refugees"


def test_validate_url_valid_with_port():
    """Test validation of URLs with ports"""
    from app.services.website_crawler.url_validator import validate_url
    
    result = validate_url("http://localhost:8080")
    assert result == "http://localhost:8080"
    
    result = validate_url("https://example.com:443")
    assert result == "https://example.com:443"


def test_validate_url_valid_with_path():
    """Test validation of URLs with paths"""
    from app.services.website_crawler.url_validator import validate_url
    
    result = validate_url("https://example.com/path/to/page")
    assert result == "https://example.com/path/to/page"
    
    result = validate_url("https://example.com/path/?query=param")
    assert result == "https://example.com/path/?query=param"


def test_validate_url_invalid_no_scheme():
    """Test validation rejects URLs without scheme"""
    from app.services.website_crawler.url_validator import validate_url, URLValidationError
    
    with pytest.raises(URLValidationError) as exc_info:
        validate_url("example.com")
    
    assert "Invalid URL" in str(exc_info.value)
    assert "must start with http:// or https://" in str(exc_info.value)


def test_validate_url_invalid_scheme():
    """Test validation rejects non-HTTP/HTTPS schemes"""
    from app.services.website_crawler.url_validator import validate_url, URLValidationError
    
    with pytest.raises(URLValidationError) as exc_info:
        validate_url("ftp://example.com")
    
    assert "Invalid URL" in str(exc_info.value)
    
    with pytest.raises(URLValidationError) as exc_info:
        validate_url("mailto:test@example.com")
    
    assert "Invalid URL" in str(exc_info.value)


def test_validate_url_invalid_format():
    """Test validation rejects malformed URLs"""
    from app.services.website_crawler.url_validator import validate_url, URLValidationError
    
    with pytest.raises(URLValidationError) as exc_info:
        validate_url("")
    
    assert "Invalid URL" in str(exc_info.value)
    
    with pytest.raises(URLValidationError) as exc_info:
        validate_url("not a url")
    
    assert "Invalid URL" in str(exc_info.value)
    
    with pytest.raises(URLValidationError) as exc_info:
        validate_url("http://")
    
    assert "Invalid URL" in str(exc_info.value)


def test_validate_url_normalization():
    """Test URL normalization"""
    from app.services.website_crawler.url_validator import validate_url
    
    # Remove trailing slashes
    result = validate_url("https://example.com/")
    assert result == "https://example.com"
    
    # Remove duplicate slashes
    result = validate_url("https://example.com//path")
    assert result == "https://example.com/path"
    
    # Ensure scheme is lowercase
    result = validate_url("HTTPS://example.com")
    assert result == "https://example.com"


def test_validate_url_extract_domain():
    """Test domain extraction from URL"""
    from app.services.website_crawler.url_validator import extract_domain
    
    assert extract_domain("https://example.com") == "example.com"
    assert extract_domain("http://www.example.com") == "www.example.com"
    assert extract_domain("https://sub.example.com/path") == "sub.example.com"
    assert extract_domain("https://example.com:8080/path") == "example.com"


def test_validate_and_extract_website_metadata():
    """Test URL validation with metadata extraction"""
    from app.services.website_crawler.url_validator import validate_and_extract_metadata
    
    result = validate_and_extract_metadata("https://www.unhcr.org/refugees")
    
    assert result["url"] == "https://www.unhcr.org/refugees"
    assert result["domain"] == "www.unhcr.org"
    assert result["scheme"] == "https"
    assert "path" in result
    assert result["path"] == "/refugees"
