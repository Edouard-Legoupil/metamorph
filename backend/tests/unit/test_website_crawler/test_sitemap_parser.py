"""
Tests for sitemap.xml parsing functionality (FR-001b)

Sitemap parsing is used for structured file discovery on websites.
Supports both XML sitemaps and sitemap index files.
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime


def test_parse_sitemap_xml_basic():
    """Test parsing a basic sitemap.xml with URLs"""
    from app.services.website_crawler.sitemap_parser import parse_sitemap_xml
    
    sitemap_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://example.com/page1.html</loc>
        <lastmod>2024-01-01</lastmod>
        <changefreq>daily</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>https://example.com/page2.html</loc>
        <lastmod>2024-01-02</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.6</priority>
    </url>
</urlset>
"""
    
    result = parse_sitemap_xml(sitemap_content, "https://example.com/sitemap.xml")
    
    assert len(result["urls"]) == 2
    assert "https://example.com/page1.html" in result["urls"]
    assert "https://example.com/page2.html" in result["urls"]
    assert result["sitemap_type"] == "urlset"


def test_parse_sitemap_xml_with_file_types():
    """Test parsing sitemap.xml with various file types"""
    from app.services.website_crawler.sitemap_parser import parse_sitemap_xml
    
    sitemap_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://example.com/documents/report.pdf</loc>
    </url>
    <url>
        <loc>https://example.com/data/sheet.xlsx</loc>
    </url>
    <url>
        <loc>https://example.com/presentation.pptx</loc>
    </url>
    <url>
        <loc>https://example.com/notes.txt</loc>
    </url>
    <url>
        <loc>https://example.com/page.html</loc>
    </url>
</urlset>
"""
    
    result = parse_sitemap_xml(sitemap_content, "https://example.com/sitemap.xml")
    
    assert len(result["urls"]) == 5
    # All URLs should be extracted regardless of file type
    assert "https://example.com/documents/report.pdf" in result["urls"]
    assert "https://example.com/data/sheet.xlsx" in result["urls"]
    assert "https://example.com/presentation.pptx" in result["urls"]
    assert "https://example.com/notes.txt" in result["urls"]
    assert "https://example.com/page.html" in result["urls"]


def test_parse_sitemap_index():
    """Test parsing a sitemap index file"""
    from app.services.website_crawler.sitemap_parser import parse_sitemap_xml
    
    sitemap_content = """<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <sitemap>
        <loc>https://example.com/sitemap1.xml</loc>
        <lastmod>2024-01-01</lastmod>
    </sitemap>
    <sitemap>
        <loc>https://example.com/sitemap2.xml</loc>
        <lastmod>2024-01-02</lastmod>
    </sitemap>
</sitemapindex>
"""
    
    result = parse_sitemap_xml(sitemap_content, "https://example.com/sitemapindex.xml")
    
    assert result["sitemap_type"] == "sitemapindex"
    assert len(result["sitemaps"]) == 2
    assert "https://example.com/sitemap1.xml" in result["sitemaps"]
    assert "https://example.com/sitemap2.xml" in result["sitemaps"]


def test_parse_sitemap_xml_empty():
    """Test parsing empty or invalid sitemap.xml"""
    from app.services.website_crawler.sitemap_parser import parse_sitemap_xml
    
    # Empty content
    result = parse_sitemap_xml("", "https://example.com/sitemap.xml")
    assert result["urls"] == []
    assert result["sitemaps"] == []
    
    # Invalid XML
    result = parse_sitemap_xml("not valid xml", "https://example.com/sitemap.xml")
    assert result["urls"] == []
    assert result["sitemaps"] == []


def test_parse_sitemap_xml_with_namespaces():
    """Test parsing sitemap.xml with different namespace formats"""
    from app.services.website_crawler.sitemap_parser import parse_sitemap_xml
    
    # With namespace prefix
    sitemap_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns:s="http://www.sitemaps.org/schemas/sitemap/0.9">
    <s:url>
        <s:loc>https://example.com/page1.html</s:loc>
    </s:url>
</urlset>
"""
    
    result = parse_sitemap_xml(sitemap_content, "https://example.com/sitemap.xml")
    assert len(result["urls"]) == 1
    assert "https://example.com/page1.html" in result["urls"]


def test_fetch_sitemap_xml_success():
    """Test fetching sitemap.xml from a website"""
    from app.services.website_crawler.sitemap_parser import fetch_sitemap_xml
    
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://example.com/page1.html</loc>
    </url>
</urlset>
"""
        mock_get.return_value = mock_response
        
        result = fetch_sitemap_xml("https://example.com/sitemap.xml")
        
        assert result["found"] is True
        assert result["url"] == "https://example.com/sitemap.xml"
        assert len(result["urls"]) == 1


def test_fetch_sitemap_xml_not_found():
    """Test fetching sitemap.xml when not found"""
    from app.services.website_crawler.sitemap_parser import fetch_sitemap_xml
    
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = fetch_sitemap_xml("https://example.com/sitemap.xml")
        
        assert result["found"] is False
        assert result["urls"] == []


def test_fetch_sitemap_xml_error():
    """Test fetching sitemap.xml when error occurs"""
    from app.services.website_crawler.sitemap_parser import fetch_sitemap_xml
    
    with patch('requests.get') as mock_get:
        mock_get.side_effect = Exception("Connection error")
        
        result = fetch_sitemap_xml("https://example.com/sitemap.xml")
        
        assert result["found"] is False
        assert result["urls"] == []


def test_discover_sitemaps_from_robots_txt():
    """Test discovering sitemap URLs from robots.txt"""
    from app.services.website_crawler.sitemap_parser import discover_sitemaps
    
    # Simulate robots.txt with sitemap references
    with patch('requests.get') as mock_get:
        # First call: robots.txt
        mock_robots_response = MagicMock()
        mock_robots_response.status_code = 200
        mock_robots_response.text = "User-agent: *\nSitemap: https://example.com/sitemap.xml"
        
        # Second call: sitemap.xml
        mock_sitemap_response = MagicMock()
        mock_sitemap_response.status_code = 200
        mock_sitemap_response.text = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://example.com/page1.html</loc>
    </url>
</urlset>
"""
        
        # Create mock responses for all expected calls
        # robots.txt + sitemap.xml + common locations (sitemap_index.xml, etc.)
        mock_responses = []
        
        # robots.txt
        mock_responses.append(mock_robots_response)
        
        # sitemap.xml (from robots.txt)
        mock_responses.append(mock_sitemap_response)
        
        # Common locations (will return 404)
        for _ in range(4):  # sitemap_index.xml, sitemap.xml.gz, sitemap-index.xml, sitemap/
            mock_404 = MagicMock()
            mock_404.status_code = 404
            mock_404.text = "Not found"
            mock_responses.append(mock_404)
        
        mock_get.side_effect = mock_responses
        
        result = discover_sitemaps("https://example.com")
        
        # Should include the sitemap from robots.txt plus common locations
        assert "https://example.com/sitemap.xml" in result["sitemap_urls"]
        # Should have discovered at least the URL from the sitemap
        assert len(result["discovered_urls"]) >= 1


def test_filter_scrapable_files():
    """Test filtering URLs to identify scrapable files"""
    from app.services.website_crawler.sitemap_parser import filter_scrapable_files
    
    urls = [
        "https://example.com/doc.pdf",
        "https://example.com/report.docx",
        "https://example.com/data.xlsx",
        "https://example.com/presentation.pptx",
        "https://example.com/notes.txt",
        "https://example.com/page.html",
        "https://example.com/image.jpg",
        "https://example.com/style.css",
        "https://example.com/script.js",
    ]
    
    scrapable = filter_scrapable_files(urls)
    
    # PDF, Word, Excel, PowerPoint, HTML, text should be scrapable
    assert "https://example.com/doc.pdf" in scrapable
    assert "https://example.com/report.docx" in scrapable
    assert "https://example.com/data.xlsx" in scrapable
    assert "https://example.com/presentation.pptx" in scrapable
    assert "https://example.com/notes.txt" in scrapable
    assert "https://example.com/page.html" in scrapable
    
    # Images, CSS, JS should not be scrapable by default
    assert "https://example.com/image.jpg" not in scrapable
    assert "https://example.com/style.css" not in scrapable
    assert "https://example.com/script.js" not in scrapable


def test_extract_metadata_from_sitemap_url():
    """Test extracting metadata from sitemap URL entries"""
    from app.services.website_crawler.sitemap_parser import extract_metadata_from_sitemap_url
    
    url = "https://example.com/documents/report.pdf"
    metadata = extract_metadata_from_sitemap_url(url)
    
    assert metadata["url"] == url
    assert metadata["file_name"] == "report.pdf"
    assert metadata["file_type"] == "pdf"
    assert metadata["path"] == "/documents/"
