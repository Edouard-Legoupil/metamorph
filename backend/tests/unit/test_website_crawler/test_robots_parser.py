"""
Tests for robots.txt parsing functionality (FR-001d, NFR-009)
"""
import pytest
from unittest.mock import patch, MagicMock


def test_parse_robots_txt_allowed():
    """Test parsing robots.txt that allows crawling"""
    from app.services.website_crawler.robots_parser import parse_robots_txt, check_robots_permission
    
    robots_content = """
User-agent: *
Disallow:

User-agent: BadBot
Disallow: /
"""
    
    result = parse_robots_txt(robots_content, "http://example.com/robots.txt")
    
    assert result["can_crawl"] is True
    assert result["crawl_delay"] is None
    
    # Test with MetamorphBot user agent
    assert check_robots_permission(robots_content, "http://example.com", "MetamorphBot/1.0") == True


def test_parse_robots_txt_disallowed():
    """Test parsing robots.txt that disallows crawling"""
    from app.services.website_crawler.robots_parser import parse_robots_txt, check_robots_permission
    
    robots_content = """
User-agent: *
Disallow: /
"""
    
    result = parse_robots_txt(robots_content, "http://example.com/robots.txt")
    
    assert result["can_crawl"] is False
    
    # Test with any user agent
    assert check_robots_permission(robots_content, "http://example.com", "MetamorphBot/1.0") == False


def test_parse_robots_txt_with_crawl_delay():
    """Test parsing robots.txt with crawl-delay"""
    from app.services.website_crawler.robots_parser import parse_robots_txt
    
    robots_content = """
User-agent: *
Crawl-delay: 5
Disallow: /private
"""
    
    result = parse_robots_txt(robots_content, "http://example.com/robots.txt")
    
    assert result["can_crawl"] is True
    assert result["crawl_delay"] == 5


def test_parse_robots_txt_specific_path_disallowed():
    """Test parsing robots.txt with specific paths disallowed"""
    from app.services.website_crawler.robots_parser import parse_robots_txt, is_path_allowed
    
    robots_content = """
User-agent: *
Disallow: /private
Disallow: /admin
Allow: /public
"""
    
    result = parse_robots_txt(robots_content, "http://example.com/robots.txt")
    
    assert result["can_crawl"] is True
    assert result["disallowed_paths"] == ["/private", "/admin"]
    
    # Test path checking
    assert is_path_allowed("/public/file.pdf", result) == True
    assert is_path_allowed("/private/file.pdf", result) == False
    assert is_path_allowed("/admin/file.pdf", result) == False
    assert is_path_allowed("/other/file.pdf", result) == True


def test_parse_robots_txt_multiple_user_agents():
    """Test parsing robots.txt with multiple user agents"""
    from app.services.website_crawler.robots_parser import parse_robots_txt
    
    robots_content = """
User-agent: Googlebot
Disallow: /search

User-agent: *
Disallow: /private
"""
    
    # Parse for MetamorphBot (falls under *)
    result = parse_robots_txt(robots_content, "http://example.com/robots.txt")
    
    assert result["can_crawl"] is True
    assert "/private" in result["disallowed_paths"]
    # /search is allowed for MetamorphBot (only disallowed for Googlebot)


def test_parse_robots_txt_empty():
    """Test parsing empty robots.txt"""
    from app.services.website_crawler.robots_parser import parse_robots_txt
    
    result = parse_robots_txt("", "http://example.com/robots.txt")
    
    # Empty robots.txt means all is allowed
    assert result["can_crawl"] is True
    assert result["crawl_delay"] is None


def test_parse_robots_txt_invalid():
    """Test parsing invalid robots.txt"""
    from app.services.website_crawler.robots_parser import parse_robots_txt
    
    # Invalid content should default to allowed
    result = parse_robots_txt("invalid content", "http://example.com/robots.txt")
    
    assert result["can_crawl"] is True


def test_fetch_robots_txt_success():
    """Test fetching robots.txt from a website"""
    from app.services.website_crawler.robots_parser import fetch_robots_txt
    
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "User-agent: *\nDisallow: /private"
        mock_get.return_value = mock_response
        
        result = fetch_robots_txt("http://example.com")
        
        assert result["url"] == "http://example.com/robots.txt"
        assert result["content"] == "User-agent: *\nDisallow: /private"
        assert result["found"] is True
        assert result["can_crawl"] is True


def test_fetch_robots_txt_not_found():
    """Test fetching robots.txt when not found"""
    from app.services.website_crawler.robots_parser import fetch_robots_txt
    
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = fetch_robots_txt("http://example.com")
        
        assert result["found"] is False
        # If robots.txt not found, assume crawling is allowed
        assert result["can_crawl"] is True


def test_fetch_robots_txt_error():
    """Test fetching robots.txt when error occurs"""
    from app.services.website_crawler.robots_parser import fetch_robots_txt
    
    with patch('requests.get') as mock_get:
        mock_get.side_effect = Exception("Connection error")
        
        result = fetch_robots_txt("http://example.com")
        
        assert result["found"] is False
        # If error fetching, assume crawling is allowed (fail-open)
        assert result["can_crawl"] is True


def test_check_robots_permission_respects_delay():
    """Test that robots permission respects crawl delay"""
    from app.services.website_crawler.robots_parser import check_robots_permission_with_delay
    
    robots_content = """
User-agent: *
Crawl-delay: 10
"""
    
    result = check_robots_permission_with_delay(robots_content, "http://example.com", "MetamorphBot/1.0")
    
    assert result["can_crawl"] is True
    assert result["crawl_delay"] == 10
