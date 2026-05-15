"""
Sitemap Parser Module (FR-001b)

Provides functionality to parse sitemap.xml files for structured file discovery.
Supports both XML sitemaps and sitemap index files.
"""
import re
import requests
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
from datetime import datetime

from .url_validator import validate_url, extract_domain


# Supported file types for scraping (FR-001a)
SCRAPABLE_FILE_TYPES = [
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
    'txt', 'csv', 'rtf', 'html', 'htm', 'md', 'json',
    'xml', 'epub', 'odt', 'ods', 'odp',
]

# Non-scrapable file types (images, styles, scripts, etc.)
NON_SCRAPABLE_EXTENSIONS = [
    'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp', 'ico',
    'css', 'js', 'ts', 'jsx', 'tsx',
    'mp3', 'mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv',
    'zip', 'tar', 'gz', 'rar', '7z',
    'exe', 'dll', 'so', 'app', 'bin',
]


def parse_sitemap_xml(content: str, url: str = "") -> Dict[str, Any]:
    """
    Parse sitemap.xml content and extract URLs.
    
    Args:
        content: The sitemap.xml file content
        url: The URL of the sitemap (for context)
        
    Returns:
        Dictionary containing:
        - sitemap_type: "urlset" or "sitemapindex"
        - urls: List of discovered URLs
        - sitemaps: List of nested sitemap URLs (for sitemapindex)
        - lastmod: Last modification date (if available)
        - parsing_errors: List of any parsing errors encountered
        
    Acceptance Criteria (FR-001b):
    - Parse sitemap.xml files
    - Extract all URLs from <loc> tags
    - Handle both urlset and sitemapindex formats
    - Extract metadata (lastmod, changefreq, priority)
    """
    result = {
        "sitemap_type": "urlset",
        "urls": [],
        "sitemaps": [],
        "lastmod": None,
        "parsing_errors": [],
    }
    
    if not content or not content.strip():
        return result
    
    try:
        import xml.etree.ElementTree as ET
        
        # Try to parse with namespace handling
        try:
            root = ET.fromstring(content)
        except ET.ParseError:
            # Try removing namespace declarations
            content_cleaned = re.sub(r'xmlns[^"]*="[^"]*"', '', content)
            try:
                root = ET.fromstring(content_cleaned)
            except ET.ParseError as e:
                result["parsing_errors"].append(f"XML parsing error: {str(e)}")
                return result
        
        # Detect sitemap type
        if root.tag.endswith('sitemapindex'):
            result["sitemap_type"] = "sitemapindex"
            # Parse sitemap index
            for sitemap_elem in root.findall('.//{*}sitemap'):
                loc_elem = sitemap_elem.find('.//{*}loc')
                if loc_elem is not None and loc_elem.text:
                    sitemap_url = loc_elem.text.strip()
                    # Resolve relative URLs
                    if not sitemap_url.startswith(('http://', 'https://')):
                        sitemap_url = urljoin(url, sitemap_url)
                    result["sitemaps"].append(sitemap_url)
                    
                lastmod_elem = sitemap_elem.find('.//{*}lastmod')
                if lastmod_elem is not None and lastmod_elem.text:
                    result["lastmod"] = lastmod_elem.text.strip()
        
        elif root.tag.endswith('urlset'):
            result["sitemap_type"] = "urlset"
            # Parse URL set
            for url_elem in root.findall('.//{*}url'):
                loc_elem = url_elem.find('.//{*}loc')
                if loc_elem is not None and loc_elem.text:
                    page_url = loc_elem.text.strip()
                    # Resolve relative URLs
                    if not page_url.startswith(('http://', 'https://')):
                        page_url = urljoin(url, page_url)
                    result["urls"].append(page_url)
                
                # Extract metadata
                lastmod_elem = url_elem.find('.//{*}lastmod')
                if lastmod_elem is not None and lastmod_elem.text:
                    pass  # Metadata stored per-URL if needed
                    
                changefreq_elem = url_elem.find('.//{*}changefreq')
                priority_elem = url_elem.find('.//{*}priority')
        
    except Exception as e:
        result["parsing_errors"].append(f"Error parsing sitemap: {str(e)}")
    
    return result


def fetch_sitemap_xml(sitemap_url: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Fetch and parse sitemap.xml from a URL.
    
    Args:
        sitemap_url: The URL of the sitemap.xml file
        timeout: Timeout in seconds
        
    Returns:
        Dictionary containing:
        - found: Whether sitemap was found and parsed
        - url: The sitemap URL
        - content: The raw content (if found)
        - urls: List of discovered URLs
        - sitemaps: List of nested sitemap URLs
        - sitemap_type: Type of sitemap
        - error: Error message (if any)
        
    Acceptance Criteria (FR-001b):
    - Fetch sitemap.xml from URL
    - Handle HTTP errors gracefully
    - Respect robots.txt rules
    """
    result = {
        "found": False,
        "url": sitemap_url,
        "content": "",
        "urls": [],
        "sitemaps": [],
        "sitemap_type": "urlset",
        "error": None,
    }
    
    try:
        # Validate URL first
        validate_url(sitemap_url)
        
        response = requests.get(sitemap_url, timeout=timeout)
        
        if response.status_code == 200:
            result["found"] = True
            result["content"] = response.text
            
            # Parse the content
            parsed = parse_sitemap_xml(response.text, sitemap_url)
            result.update(parsed)
            
        elif response.status_code == 404:
            result["error"] = "Sitemap not found"
        else:
            result["error"] = f"HTTP error: {response.status_code}"
            
    except requests.RequestException as e:
        result["error"] = f"Connection error: {str(e)}"
    except Exception as e:
        # Fail-open: don't crash on parsing errors
        result["error"] = f"Error: {str(e)}"
    
    return result


def discover_sitemaps(base_url: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Discover sitemap URLs from a website.
    
    Checks for sitemap references in:
    1. robots.txt Sitemap: directives
    2. Common sitemap locations (/sitemap.xml, /sitemap_index.xml)
    
    Args:
        base_url: The base URL of the website
        timeout: Timeout in seconds
        
    Returns:
        Dictionary containing:
        - sitemap_urls: List of discovered sitemap URLs
        - discovered_urls: List of URLs discovered from sitemaps
        - errors: List of any errors encountered
        
    Acceptance Criteria (FR-001b):
    - Discover sitemap.xml from robots.txt
    - Check common sitemap locations
    - Parse and aggregate URLs from all discovered sitemaps
    """
    from .robots_parser import fetch_robots_txt
    
    result = {
        "sitemap_urls": [],
        "discovered_urls": [],
        "errors": [],
    }
    
    try:
        validate_url(base_url)
        domain = extract_domain(base_url)
        
        # Check robots.txt for sitemap references
        robots_result = fetch_robots_txt(base_url, timeout=timeout)
        if robots_result.get("found") and robots_result.get("sitemaps"):
            for sitemap_url in robots_result["sitemaps"]:
                if sitemap_url not in result["sitemap_urls"]:
                    result["sitemap_urls"].append(sitemap_url)
        
        # Check common sitemap locations
        common_locations = [
            "/sitemap.xml",
            "/sitemap_index.xml",
            "/sitemap.xml.gz",
            "/sitemap-index.xml",
            "/sitemap/",
        ]
        
        for location in common_locations:
            sitemap_url = urljoin(base_url, location)
            # Normalize URL
            try:
                sitemap_url = validate_url(sitemap_url)
            except:
                continue
            
            if sitemap_url not in result["sitemap_urls"]:
                result["sitemap_urls"].append(sitemap_url)
        
        # Fetch and parse all discovered sitemaps
        for sitemap_url in result["sitemap_urls"]:
            try:
                sitemap_result = fetch_sitemap_xml(sitemap_url, timeout=timeout)
                if sitemap_result.get("found"):
                    result["discovered_urls"].extend(sitemap_result.get("urls", []))
                    # Handle nested sitemaps (sitemapindex)
                    if sitemap_result.get("sitemap_type") == "sitemapindex":
                        for nested_sitemap in sitemap_result.get("sitemaps", []):
                            if nested_sitemap not in result["sitemap_urls"]:
                                result["sitemap_urls"].append(nested_sitemap)
            except Exception as e:
                result["errors"].append(f"Error processing {sitemap_url}: {str(e)}")
        
        # Remove duplicates while preserving order
        result["discovered_urls"] = list(dict.fromkeys(result["discovered_urls"]))
        
    except Exception as e:
        result["errors"].append(f"Discovery error: {str(e)}")
    
    return result


def filter_scrapable_files(urls: List[str], additional_types: List[str] = None) -> List[str]:
    """
    Filter a list of URLs to only include scrapable file types.
    
    Args:
        urls: List of URLs to filter
        additional_types: Additional file extensions to include
        
    Returns:
        List of URLs that point to scrapable files
        
    Acceptance Criteria (FR-001a):
    - Identify supported file types (PDF, Word, Excel, PowerPoint, HTML, text)
    - Filter out non-scrapable files (images, CSS, JS, etc.)
    """
    if additional_types:
        scrapable_types = set(SCRAPABLE_FILE_TYPES + [t.lower() for t in additional_types])
    else:
        scrapable_types = set(SCRAPABLE_FILE_TYPES)
    
    non_scrapable = set(NON_SCRAPABLE_EXTENSIONS)
    
    scrapable_urls = []
    
    for url in urls:
        try:
            parsed = urlparse(url)
            path = parsed.path.lower()
            
            # Extract file extension
            if '.' in path:
                ext = path.rsplit('.', 1)[-1].split('?')[0].split('#')[0]
                
                # Check if extension is scrapable
                if ext in scrapable_types and ext not in non_scrapable:
                    scrapable_urls.append(url)
                    continue
                
                # Also check if URL ends with known scrapable pattern
                # (e.g., URLs without extensions but with scrapable content)
                if path.endswith('/') or not any(
                    path.endswith(f'.{e}') for e in non_scrapable
                ):
                    # HTML pages and directories are generally scrapable
                    scrapable_urls.append(url)
            else:
                # URLs without extensions (directories, clean URLs) are scrapable
                scrapable_urls.append(url)
                
        except Exception:
            # If we can't parse the URL, include it to be safe
            scrapable_urls.append(url)
    
    return scrapable_urls


def extract_metadata_from_sitemap_url(url: str) -> Dict[str, Any]:
    """
    Extract metadata from a URL discovered in sitemap.
    
    Args:
        url: The URL to extract metadata from
        
    Returns:
        Dictionary containing:
        - url: The URL
        - file_name: Extracted file name
        - file_type: Extracted file extension (or None)
        - path: Directory path (without filename)
        - domain: Domain name
        - is_directory: Whether URL points to a directory
        
    Acceptance Criteria (FR-001b):
    - Extract file names and types from URLs
    - Identify directory vs file URLs
    """
    try:
        validate_url(url)
    except:
        pass  # URL may not be fully validated yet
    
    parsed = urlparse(url)
    
    result = {
        "url": url,
        "file_name": None,
        "file_type": None,
        "path": "/",
        "domain": extract_domain(url),
        "is_directory": parsed.path.endswith('/'),
    }
    
    # Extract file name and type from path
    path = parsed.path
    if path and path != '/':
        # Remove trailing slash for processing
        clean_path = path.rstrip('/')
        
        # Extract directory path (without filename)
        if '/' in clean_path:
            directory_path = clean_path.rsplit('/', 1)[0]
            # Add trailing slash for directory paths
            result["path"] = directory_path + "/" if directory_path else "/"
        else:
            result["path"] = "/"
        
        # Extract file name
        file_name = clean_path.rsplit('/', 1)[-1]
        result["file_name"] = file_name
        
        # Extract file extension
        if '.' in file_name and not file_name.startswith('.'):
            ext = file_name.rsplit('.', 1)[-1].split('?')[0].split('#')[0].lower()
            result["file_type"] = ext
    
    return result


def get_sitemap_urls_from_robots(robots_content: str, base_url: str) -> List[str]:
    """
    Extract sitemap URLs from robots.txt content.
    
    Args:
        robots_content: The content of robots.txt
        base_url: The base URL to resolve relative paths
        
    Returns:
        List of sitemap URLs found in robots.txt
    """
    sitemap_urls = []
    
    if not robots_content:
        return sitemap_urls
    
    for line in robots_content.split('\n'):
        line = line.strip()
        if line.lower().startswith('sitemap:'):
            sitemap_path = line.split(':', 1)[1].strip()
            # Resolve relative URL
            if not sitemap_path.startswith(('http://', 'https://')):
                sitemap_path = urljoin(base_url, sitemap_path)
            sitemap_urls.append(sitemap_path)
    
    return sitemap_urls
