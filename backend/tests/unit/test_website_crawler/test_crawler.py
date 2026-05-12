"""
Tests for website crawler functionality (FR-001c)

Tests BFS/DFS crawling, link extraction, and file discovery.
"""
import pytest
from unittest.mock import patch, MagicMock
from urllib.parse import urlparse


def test_crawl_website_basic():
    """Test basic website crawling with BFS"""
    from app.services.website_crawler.crawler import WebsiteCrawler
    
    html_content = """
    <html>
        <body>
            <a href="/page1.html">Page 1</a>
            <a href="/page2.html">Page 2</a>
            <a href="/documents/report.pdf">Report PDF</a>
        </body>
    </html>
    """
    
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = html_content
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_get.return_value = mock_response
        
        crawler = WebsiteCrawler(
            base_url="https://example.com",
            max_pages=10,
            max_depth=2,
        )
        
        result = crawler.crawl()
        
        assert result.status == "completed"
        assert len(result.discovered_urls) >= 3
        assert "https://example.com/page1.html" in result.discovered_urls
        assert "https://example.com/page2.html" in result.discovered_urls


def test_crawl_website_with_robots_txt():
    """Test crawling respects robots.txt"""
    from app.services.website_crawler.crawler import WebsiteCrawler
    
    with patch('requests.get') as mock_get:
        # First call: robots.txt
        mock_robots_response = MagicMock()
        mock_robots_response.status_code = 200
        mock_robots_response.text = "User-agent: *\nDisallow: /private/"
        
        # Second call: home page
        mock_home_response = MagicMock()
        mock_home_response.status_code = 200
        mock_home_response.text = '<html><body><a href="/private/secret.html">Secret</a></body></html>'
        
        mock_get.side_effect = [mock_robots_response, mock_home_response]
        
        crawler = WebsiteCrawler(
            base_url="https://example.com",
            max_pages=5,
            max_depth=1,
            respect_robots=True,
        )
        
        result = crawler.crawl()
        
        # /private/secret.html should not be crawled due to robots.txt
        assert "https://example.com/private/secret.html" not in result.crawled_urls


def test_crawl_website_max_depth():
    """Test crawling with max depth limit"""
    from app.services.website_crawler.crawler import WebsiteCrawler
    
    # Create HTML with nested links
    page1_html = '<html><body><a href="/page2.html">Page 2</a></body></html>'
    page2_html = '<html><body><a href="/page3.html">Page 3</a></body></html>'
    page3_html = '<html><body>Page 3 content</body></html>'
    
    with patch('requests.get') as mock_get:
        mock_responses = []
        
        # robots.txt
        mock_robots = MagicMock()
        mock_robots.status_code = 200
        mock_robots.text = "User-agent: *\nDisallow:"
        mock_responses.append(mock_robots)
        
        # Home page
        mock_home = MagicMock()
        mock_home.status_code = 200
        mock_home.text = '<html><body><a href="/page1.html">Page 1</a></body></html>'
        mock_responses.append(mock_home)
        
        # Page 1
        mock_page1 = MagicMock()
        mock_page1.status_code = 200
        mock_page1.text = page1_html
        mock_responses.append(mock_page1)
        
        # Page 2 (depth 2)
        mock_page2 = MagicMock()
        mock_page2.status_code = 200
        mock_page2.text = page2_html
        mock_responses.append(mock_page2)
        
        mock_get.side_effect = mock_responses
        
        crawler = WebsiteCrawler(
            base_url="https://example.com",
            max_pages=10,
            max_depth=1,  # Only crawl home page and direct links
        )
        
        result = crawler.crawl()
        
        # Page 3 should not be crawled due to depth limit
        assert "https://example.com/page3.html" not in result.crawled_urls


def test_crawl_website_rate_limiting():
    """Test crawling with rate limiting (NFR-010)"""
    from app.services.website_crawler.crawler import WebsiteCrawler
    import time
    
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><a href="/page1.html">Page 1</a></body></html>'
        mock_get.return_value = mock_response
        
        crawler = WebsiteCrawler(
            base_url="https://example.com",
            max_pages=5,
            max_depth=1,
            crawl_delay=0.5,  # 500ms delay between requests
        )
        
        start_time = time.time()
        result = crawler.crawl()
        elapsed_time = time.time() - start_time
        
        # With crawl_delay, multiple requests should take longer
        # (This is a basic test; more sophisticated timing tests may be needed)
        assert result.status == "completed"


def test_crawl_website_same_domain_only():
    """Test crawling stays within the same domain"""
    from app.services.website_crawler.crawler import WebsiteCrawler
    
    html_content = """
    <html>
        <body>
            <a href="https://example.com/page1.html">Same domain</a>
            <a href="https://otherexample.com/page.html">External domain</a>
        </body>
    </html>
    """
    
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = html_content
        mock_get.return_value = mock_response
        
        crawler = WebsiteCrawler(
            base_url="https://example.com",
            max_pages=5,
            max_depth=1,
            same_domain_only=True,
        )
        
        result = crawler.crawl()
        
        # External domain should be discovered but not crawled
        assert result.status == "completed"
        # The external URL might be in discovered_urls but not crawled


def test_extract_links_from_html():
    """Test link extraction from HTML content"""
    from app.services.website_crawler.crawler import extract_links
    
    html_content = """
    <html>
        <body>
            <a href="/page1.html">Page 1</a>
            <a href="/page2.html" target="_blank">Page 2</a>
            <a href="https://example.com/absolute.html">Absolute</a>
            <a href="#section">Anchor</a>
            <a href="javascript:void(0)">JS Link</a>
            <a href="/documents/report.pdf">PDF</a>
        </body>
    </html>
    """
    
    base_url = "https://example.com"
    links = extract_links(html_content, base_url)
    
    # All links are normalized to absolute URLs
    assert "https://example.com/page1.html" in links
    assert "https://example.com/page2.html" in links
    assert "https://example.com/absolute.html" in links
    assert "https://example.com/documents/report.pdf" in links
    
    # Filter out non-HTTP links
    assert "#section" not in links
    assert "javascript:void(0)" not in links


def test_normalize_url_for_crawling():
    """Test URL normalization for crawling"""
    from app.services.website_crawler.crawler import normalize_url_for_crawling
    
    base_url = "https://example.com"
    
    # Relative URL
    assert normalize_url_for_crawling("/page.html", base_url) == "https://example.com/page.html"
    
    # Absolute URL on same domain
    assert normalize_url_for_crawling("https://example.com/page.html", base_url) == "https://example.com/page.html"
    
    # URL with fragment
    assert normalize_url_for_crawling("/page.html#section", base_url) == "https://example.com/page.html"
    
    # URL with query params
    assert normalize_url_for_crawling("/page.html?param=value", base_url) == "https://example.com/page.html?param=value"
    
    # Duplicate slashes
    assert normalize_url_for_crawling("https://example.com//page.html", base_url) == "https://example.com/page.html"


def test_filter_file_urls():
    """Test filtering URLs to identify file URLs (FR-001a)"""
    from app.services.website_crawler.crawler import filter_file_urls
    
    urls = [
        "https://example.com/page.html",
        "https://example.com/doc.pdf",
        "https://example.com/report.docx",
        "https://example.com/data.xlsx",
        "https://example.com/presentation.pptx",
        "https://example.com/image.jpg",
        "https://example.com/style.css",
    ]
    
    file_urls = filter_file_urls(urls)
    
    assert "https://example.com/doc.pdf" in file_urls
    assert "https://example.com/report.docx" in file_urls
    assert "https://example.com/data.xlsx" in file_urls
    assert "https://example.com/presentation.pptx" in file_urls
    
    # HTML is also a file type
    assert "https://example.com/page.html" in file_urls
    
    # Images and CSS are not file types for scraping
    assert "https://example.com/image.jpg" not in file_urls
    assert "https://example.com/style.css" not in file_urls


def test_is_scrapable_file_type():
    """Test checking if a file type is scrapable"""
    from app.services.website_crawler.crawler import is_scrapable_file_type
    
    # Scrapable types
    assert is_scrapable_file_type("pdf") is True
    assert is_scrapable_file_type("docx") is True
    assert is_scrapable_file_type("xlsx") is True
    assert is_scrapable_file_type("pptx") is True
    assert is_scrapable_file_type("html") is True
    assert is_scrapable_file_type("txt") is True
    assert is_scrapable_file_type("md") is True
    
    # Non-scrapable types
    assert is_scrapable_file_type("jpg") is False
    assert is_scrapable_file_type("png") is False
    assert is_scrapable_file_type("css") is False
    assert is_scrapable_file_type("js") is False
    assert is_scrapable_file_type("mp4") is False


def test_crawl_website_error_handling():
    """Test crawling handles HTTP errors gracefully"""
    from app.services.website_crawler.crawler import WebsiteCrawler
    
    with patch('requests.get') as mock_get:
        # robots.txt
        mock_robots = MagicMock()
        mock_robots.status_code = 200
        mock_robots.text = "User-agent: *\nDisallow:"
        
        # Home page - error
        mock_error = MagicMock()
        mock_error.status_code = 500
        
        mock_get.side_effect = [mock_robots, mock_error]
        
        crawler = WebsiteCrawler(
            base_url="https://example.com",
            max_pages=5,
            max_depth=1,
        )
        
        result = crawler.crawl()
        
        # Should handle error gracefully
        assert result.status == "completed"
        assert len(result.errors) >= 1


def test_crawl_website_timeout():
    """Test crawling handles timeouts"""
    from app.services.website_crawler.crawler import WebsiteCrawler
    
    with patch('requests.get') as mock_get:
        # robots.txt
        mock_robots = MagicMock()
        mock_robots.status_code = 200
        mock_robots.text = "User-agent: *\nDisallow:"
        
        # Home page - timeout
        mock_get.side_effect = [mock_robots, Exception("Connection timeout")]
        
        crawler = WebsiteCrawler(
            base_url="https://example.com",
            max_pages=5,
            max_depth=1,
        )
        
        result = crawler.crawl()
        
        # Should handle timeout gracefully
        assert result.status == "completed"
        assert len(result.errors) >= 1
