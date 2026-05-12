"""
Website Crawler Module (FR-001c, FR-001e)

Provides BFS/DFS crawling functionality for website exploration and file discovery.
Supports Cloudflare authentication to bypass robots.txt prevention.
"""
import re
import time
import requests
import json
from typing import Dict, Any, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse, urlunparse
from collections import deque
from dataclasses import dataclass, field

from .url_validator import validate_url, extract_domain, URLValidationError
from .robots_parser import fetch_robots_txt, check_url_against_robots
from .sitemap_parser import SCRAPABLE_FILE_TYPES, NON_SCRAPABLE_EXTENSIONS


# User agent for the crawler
USER_AGENT = "MetamorphBot/1.0 (+https://metamorph.example.com/bot-info)"

# Default headers for requests
DEFAULT_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}


@dataclass
class CloudflareConfig:
    """Configuration for Cloudflare authentication"""
    enabled: bool = False
    cf_access_client_id: str = ""
    cf_access_client_secret: str = ""
    token_url: str = "https://www.cloudflare.com/cdn-cgi/access/cfaccess"  # Default Cloudflare auth URL
    token: Optional[str] = None
    token_expiry: float = 0.0  # Unix timestamp when token expires
    auto_refresh: bool = True


@dataclass
class CrawlConfig:
    """Configuration for website crawling"""
    base_url: str
    max_pages: int = 100
    max_depth: int = 5
    same_domain_only: bool = True
    respect_robots: bool = True
    crawl_delay: float = 0.5  # seconds between requests (NFR-010)
    timeout: int = 30  # request timeout in seconds
    user_agent: str = USER_AGENT
    follow_redirects: bool = True
    max_redirects: int = 5
    skip_anchor_links: bool = True
    skip_javascript_links: bool = True
    skip_mailto_links: bool = True
    
    # File discovery settings
    discover_files: bool = True
    file_types: List[str] = field(default_factory=lambda: list(SCRAPABLE_FILE_TYPES))
    skip_non_file_urls: bool = False
    
    # Authentication settings (FR-001e)
    cloudflare: CloudflareConfig = field(default_factory=CloudflareConfig)
    basic_auth: Optional[Tuple[str, str]] = None  # (username, password)
    cookies: Optional[Dict[str, str]] = None  # Session cookies
    headers: Optional[Dict[str, str]] = None  # Custom headers


@dataclass
class CrawlResult:
    """Result of a crawl operation"""
    status: str = "completed"  # "completed", "stopped", "error"
    base_url: str = ""
    crawled_urls: List[str] = field(default_factory=list)
    discovered_urls: List[str] = field(default_factory=list)
    discovered_files: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    robots_permission: bool = True
    crawl_delay: float = 0.0
    pages_crawled: int = 0
    files_discovered: int = 0
    start_time: float = 0.0
    end_time: float = 0.0
    duration: float = 0.0


class WebsiteCrawler:
    """
    Website crawler that uses BFS to explore a website and discover files.
    
    Features:
    - BFS crawling with configurable depth
    - Respects robots.txt (NFR-009)
    - Rate limiting (NFR-010)
    - File type detection (FR-001a)
    - Domain boundary enforcement
    - Cloudflare authentication support (FR-001e)
    - Basic authentication support
    - Cookie-based session support
    - Error handling and retries
    
    Acceptance Criteria (FR-001c, FR-001e):
    - Crawl website using BFS strategy
    - Discover and follow internal links
    - Identify files that can be scraped
    - Handle errors gracefully
    - Support Cloudflare site token authentication
    - Support basic HTTP authentication
    - Support session cookies
    """
    
    def __init__(self, base_url: str, **kwargs):
        """
        Initialize the crawler.
        
        Args:
            base_url: The base URL to start crawling from
            **kwargs: Additional configuration options including:
                - cloudflare: CloudflareConfig with cf_access_client_id and cf_access_client_secret
                - basic_auth: Tuple of (username, password)
                - cookies: Dict of session cookies
                - headers: Dict of custom headers
        """
        self.config = CrawlConfig(base_url=base_url, **kwargs)
        self.base_url = base_url
        self.domain = extract_domain(base_url)
        self.robots_result: Optional[Dict[str, Any]] = None
        self.crawl_delay = self.config.crawl_delay
        self.session: Optional[requests.Session] = None
        
        # Validate base URL
        try:
            self.base_url = validate_url(base_url)
        except URLValidationError as e:
            raise ValueError(f"Invalid base URL: {str(e)}")
        
        # Initialize Cloudflare token if enabled
        if self.config.cloudflare.enabled:
            self._init_cloudflare_session()
        
        # Initialize request session
        self._init_session()
    
    def _init_session(self) -> requests.Session:
        """
        Initialize a requests session with configured authentication.
        
        Returns:
            Configured requests.Session
        """
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update(DEFAULT_HEADERS)
        
        # Add custom headers if provided
        if self.config.headers:
            self.session.headers.update(self.config.headers)
        
        # Add basic auth if provided
        if self.config.basic_auth:
            username, password = self.config.basic_auth
            self.session.auth = (username, password)
        
        # Add cookies if provided
        if self.config.cookies:
            self.session.cookies.update(self.config.cookies)
        
        # Add Cloudflare token if available
        if self.config.cloudflare.enabled and self.config.cloudflare.token:
            self.session.headers["Authorization"] = f"Bearer {self.config.cloudflare.token}"
        
        return self.session
    
    def _init_cloudflare_session(self) -> None:
        """
        Initialize Cloudflare authentication.
        Gets token from Cloudflare using client ID and secret.
        
        Cloudflare Access uses OAuth2 client credentials flow.
        Token URL: https://<team-name>.cloudflareaccess.com/cdn-cgi/access/cfaccess
        """
        if not self.config.cloudflare.cf_access_client_id or not self.config.cloudflare.cf_access_client_secret:
            raise ValueError("Cloudflare client ID and secret are required when enabled")
        
        # Get token from Cloudflare
        token_data = self._get_cloudflare_token()
        if token_data:
            self.config.cloudflare.token = token_data.get("access_token")
            expiry = token_data.get("expires_in", 3600)  # Default 1 hour
            self.config.cloudflare.token_expiry = time.time() + expiry - 60  # 1 minute buffer
    
    def _get_cloudflare_token(self) -> Optional[Dict[str, Any]]:
        """
        Get access token from Cloudflare using client credentials.
        
        Returns:
            Dictionary with token data or None if failed
        """
        try:
            # Prepare request data
            data = {
                "grant_type": "client_credentials",
                "client_id": self.config.cloudflare.cf_access_client_id,
                "client_secret": self.config.cloudflare.cf_access_client_secret,
                "audience": self.base_url,
            }
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": USER_AGENT,
            }
            
            # Send token request
            response = requests.post(
                self.config.cloudflare.token_url,
                data=data,
                headers=headers,
                timeout=self.config.timeout,
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                # Log error but continue without Cloudflare auth
                return None
                
        except Exception as e:
            # Log error but continue without Cloudflare auth
            return None
    
    def _refresh_cloudflare_token_if_needed(self) -> bool:
        """
        Refresh Cloudflare token if it's expired or about to expire.
        
        Returns:
            True if token was refreshed, False otherwise
        """
        if not self.config.cloudflare.enabled or not self.config.cloudflare.auto_refresh:
            return False
        
        if not self.config.cloudflare.token:
            # No token yet, try to get one
            token_data = self._get_cloudflare_token()
            if token_data:
                self.config.cloudflare.token = token_data.get("access_token")
                expiry = token_data.get("expires_in", 3600)
                self.config.cloudflare.token_expiry = time.time() + expiry - 60
                if self.session:
                    self.session.headers["Authorization"] = f"Bearer {self.config.cloudflare.token}"
                return True
            return False
        
        # Check if token is expired or about to expire
        if time.time() >= self.config.cloudflare.token_expiry:
            token_data = self._get_cloudflare_token()
            if token_data:
                self.config.cloudflare.token = token_data.get("access_token")
                expiry = token_data.get("expires_in", 3600)
                self.config.cloudflare.token_expiry = time.time() + expiry - 60
                if self.session:
                    self.session.headers["Authorization"] = f"Bearer {self.config.cloudflare.token}"
                return True
        
        return False
    
    def is_cloudflare_challenge(self, response: requests.Response) -> bool:
        """
        Check if a response indicates a Cloudflare challenge.
        
        Args:
            response: HTTP response to check
            
        Returns:
            True if response indicates Cloudflare challenge
        """
        if response.status_code in [403, 429, 503]:
            # Check for Cloudflare-specific indicators
            content = response.text.lower()
            headers = response.headers
            
            # Cloudflare challenge indicators
            if "cloudflare" in content or "cloudflare" in str(headers).lower():
                return True
            if "cf-ray" in str(headers).lower():
                return True
            if "access denied" in content:
                return True
        
        return False
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for requests.
        
        Returns:
            Dictionary of headers including Cloudflare token if available
        """
        headers = {}
        if self.config.cloudflare.enabled and self.config.cloudflare.token:
            headers["Authorization"] = f"Bearer {self.config.cloudflare.token}"
        return headers
    
    def fetch_robots(self) -> Dict[str, Any]:
        """
        Fetch and parse robots.txt for the website.
        Uses Cloudflare authentication if configured.
        
        Returns:
            Dictionary with robots.txt parsing results
        """
        if self.robots_result is None:
            # Prepare auth headers
            auth_headers = self._get_auth_headers()
            
            # Try with session first (includes auth)
            if self.session:
                try:
                    robots_url = urljoin(self.base_url, "/robots.txt")
                    response = self.session.get(robots_url, timeout=self.config.timeout)
                    if response.status_code == 200:
                        from .robots_parser import parse_robots_txt
                        self.robots_result = parse_robots_txt(response.text, robots_url)
                        self.robots_result["found"] = True
                        self.robots_result["url"] = robots_url
                        self.robots_result["content"] = response.text
                        
                        # Extract crawl delay
                        if self.robots_result.get("crawl_delay") and self.config.respect_robots:
                            self.crawl_delay = max(self.crawl_delay, self.robots_result["crawl_delay"])
                        return self.robots_result
                except Exception:
                    pass
            
            # Fallback to fetch_robots_txt with auth
            self.robots_result = fetch_robots_txt(
                self.base_url,
                timeout=self.config.timeout,
                headers=auth_headers,
                cookies=self.config.cookies,
                auth=self.config.basic_auth,
            )
            
            # Extract crawl delay from robots.txt
            if self.robots_result.get("crawl_delay") and self.config.respect_robots:
                self.crawl_delay = max(self.crawl_delay, self.robots_result["crawl_delay"])
        
        return self.robots_result
    
    def is_allowed_by_robots(self, url: str) -> bool:
        """
        Check if a URL is allowed by robots.txt.
        
        Args:
            url: URL to check
            
        Returns:
            True if allowed, False if disallowed
        """
        if not self.config.respect_robots:
            return True
        
        robots_result = self.fetch_robots()
        
        if not robots_result.get("found"):
            return True  # Fail-open if robots.txt not found
        
        if not robots_result.get("can_crawl", True):
            return False
        
        return check_url_against_robots(url, robots_result)
    
    def is_same_domain(self, url: str) -> bool:
        """
        Check if a URL is on the same domain as the base URL.
        
        Args:
            url: URL to check
            
        Returns:
            True if same domain, False otherwise
        """
        try:
            domain = extract_domain(url)
            return domain == self.domain or domain.endswith(f".{self.domain}")
        except:
            return False
    
    def normalize_url(self, url: str) -> Optional[str]:
        """
        Normalize a URL for crawling.
        
        Args:
            url: URL to normalize
            
        Returns:
            Normalized URL or None if invalid
        """
        try:
            # Skip empty URLs
            if not url or not isinstance(url, str):
                return None
            
            # Skip anchor links
            if url.startswith('#'):
                return None
            
            # Skip javascript links
            if url.lower().startswith('javascript:'):
                return None
            
            # Skip mailto links
            if url.lower().startswith('mailto:'):
                return None
            
            # Skip tel links
            if url.lower().startswith('tel:'):
                return None
            
            # Validate and normalize
            if not url.startswith(('http://', 'https://')):
                # Relative URL - join with base
                url = urljoin(self.base_url, url)
            
            url = validate_url(url)
            
            # Remove fragments
            parsed = urlparse(url)
            url = urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                parsed.query,
                ''  # Remove fragment
            ))
            
            # Remove duplicate slashes
            url = re.sub(r'(https?://[^/]+)/+', r'\1/', url)
            
            return url
            
        except (URLValidationError, Exception):
            return None
    
    def is_scrapable_file_type(self, url: str) -> bool:
        """
        Check if a URL points to a scrapable file type.
        
        Args:
            url: URL to check
            
        Returns:
            True if the file type is scrapable
        """
        try:
            parsed = urlparse(url)
            path = parsed.path.lower()
            
            if not path or path == '/':
                return False
            
            # Extract file extension
            if '.' in path:
                ext = path.rsplit('.', 1)[-1].split('?')[0].split('#')[0]
                
                # Check against scrapable types
                if ext in self.config.file_types:
                    return True
                
                # Check against non-scrapable types
                if ext in NON_SCRAPABLE_EXTENSIONS:
                    return False
            
            # URLs without extensions might still be HTML pages
            return True
            
        except Exception:
            return False
    
    def extract_metadata_from_url(self, url: str) -> Dict[str, Any]:
        """
        Extract metadata from a URL.
        
        Args:
            url: URL to extract metadata from
            
        Returns:
            Dictionary with file metadata
        """
        try:
            parsed = urlparse(url)
            path = parsed.path
            
            result = {
                "url": url,
                "file_name": None,
                "file_type": None,
                "path": "/",
                "domain": self.domain,
                "is_directory": path.endswith('/'),
                "size": None,
                "last_modified": None,
            }
            
            if path and path != '/':
                clean_path = path.rstrip('/')
                
                # Extract directory path
                if '/' in clean_path:
                    directory_path = clean_path.rsplit('/', 1)[0]
                    result["path"] = directory_path + "/" if directory_path else "/"
                
                # Extract file name
                file_name = clean_path.rsplit('/', 1)[-1]
                result["file_name"] = file_name
                
                # Extract file extension
                if '.' in file_name and not file_name.startswith('.'):
                    ext = file_name.rsplit('.', 1)[-1].split('?')[0].split('#')[0].lower()
                    result["file_type"] = ext
            
            return result
            
        except Exception:
            return {
                "url": url,
                "file_name": None,
                "file_type": None,
                "path": "/",
                "domain": self.domain,
                "is_directory": False,
                "size": None,
                "last_modified": None,
            }
    
    def extract_links(self, html_content: str, current_url: str) -> Set[str]:
        """
        Extract all links from HTML content.
        
        Args:
            html_content: HTML content to parse
            current_url: Current page URL (for resolving relative links)
            
        Returns:
            Set of normalized URLs found in the HTML
        """
        links = set()
        
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract all anchor tags
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                
                # Skip empty hrefs
                if not href or href.isspace():
                    continue
                
                # Normalize the URL
                normalized = self.normalize_url(href)
                if normalized:
                    links.add(normalized)
            
            # Extract links from other elements (img, link, script, etc.)
            for tag in soup.find_all(['img', 'link', 'script', 'iframe'], src=True):
                src = tag['src']
                normalized = self.normalize_url(src)
                if normalized:
                    links.add(normalized)
            
            for tag in soup.find_all(['link'], href=True):
                href = tag['href']
                normalized = self.normalize_url(href)
                if normalized:
                    links.add(normalized)
                    
        except Exception as e:
            # Log error but continue
            pass
        
        return links
    
    def should_crawl_url(self, url: str, depth: int, visited: Set[str]) -> Tuple[bool, Optional[str]]:
        """
        Determine if a URL should be crawled.
        
        Args:
            url: URL to check
            depth: Current crawl depth
            visited: Set of already visited URLs
            
        Returns:
            Tuple of (should_crawl, reason_if_not)
        """
        # Check if already visited
        if url in visited:
            return False, "already_visited"
        
        # Check depth limit
        if depth > self.config.max_depth:
            return False, "max_depth_exceeded"
        
        # Check if same domain
        if self.config.same_domain_only and not self.is_same_domain(url):
            return False, "different_domain"
        
        # Check robots.txt
        if not self.is_allowed_by_robots(url):
            return False, "disallowed_by_robots"
        
        # Check if we've reached max pages
        # (This check is done by the caller)
        
        return True, None
    
    def crawl_page(self, url: str, depth: int = 0, retry_on_cloudflare: bool = True) -> Dict[str, Any]:
        """
        Crawl a single page and extract links.
        
        Args:
            url: URL to crawl
            depth: Current crawl depth
            retry_on_cloudflare: Whether to retry with Cloudflare auth if blocked
            
        Returns:
            Dictionary with page data and extracted links
        """
        result = {
            "url": url,
            "status_code": None,
            "content_type": None,
            "links": set(),
            "files": [],
            "error": None,
            "is_cloudflare_blocked": False,
        }
        
        try:
            # Respect crawl delay
            if self.crawl_delay > 0 and depth > 0:
                time.sleep(self.crawl_delay)
            
            # Refresh Cloudflare token if needed
            if self.config.cloudflare.enabled:
                self._refresh_cloudflare_token_if_needed()
            
            # Use session if available
            if self.session:
                response = self.session.get(
                    url,
                    timeout=self.config.timeout,
                    allow_redirects=self.config.follow_redirects,
                )
            else:
                # Fallback to direct request
                headers = DEFAULT_HEADERS.copy()
                if self.config.cloudflare.enabled and self.config.cloudflare.token:
                    headers["Authorization"] = f"Bearer {self.config.cloudflare.token}"
                if self.config.headers:
                    headers.update(self.config.headers)
                
                response = requests.get(
                    url,
                    headers=headers,
                    timeout=self.config.timeout,
                    allow_redirects=self.config.follow_redirects,
                    auth=self.config.basic_auth,
                    cookies=self.config.cookies,
                )
            
            result["status_code"] = response.status_code
            result["content_type"] = response.headers.get('Content-Type', '')
            
            # Check for Cloudflare challenge
            if self.is_cloudflare_challenge(response):
                result["is_cloudflare_blocked"] = True
                result["error"] = f"Cloudflare challenge detected (status: {response.status_code})"
                
                # Try with Cloudflare auth if enabled and not already tried
                if retry_on_cloudflare and self.config.cloudflare.enabled:
                    # Force token refresh
                    self._init_cloudflare_session()
                    # Retry with fresh token
                    return self.crawl_page(url, depth, retry_on_cloudflare=False)
                return result
            
            # Check if successful
            if response.status_code >= 400:
                result["error"] = f"HTTP {response.status_code}"
                return result
            
            # Extract content
            content = response.text
            
            # Check if it's HTML
            if 'text/html' in result["content_type"]:
                # Extract links
                result["links"] = self.extract_links(content, url)
            
            # Check if it's a file we want to scrape
            if self.config.discover_files:
                # Check file type from URL
                if self.is_scrapable_file_type(url):
                    file_metadata = self.extract_metadata_from_url(url)
                    result["files"].append(file_metadata)
                
                # Also check Content-Type for files
                content_type = result["content_type"].lower()
                if any(ft in content_type for ft in ['pdf', 'word', 'excel', 'powerpoint', 'text']):
                    file_metadata = self.extract_metadata_from_url(url)
                    if file_metadata not in result["files"]:
                        result["files"].append(file_metadata)
            
        except requests.exceptions.RequestException as e:
            result["error"] = f"Request error: {str(e)}"
        except Exception as e:
            result["error"] = f"Error: {str(e)}"
        
        return result
    
    def crawl(self) -> CrawlResult:
        """
        Perform a BFS crawl of the website.
        
        Returns:
            CrawlResult with all discovered URLs and files
        """
        result = CrawlResult(
            status="completed",
            base_url=self.base_url,
            start_time=time.time(),
        )
        
        try:
            # Fetch robots.txt first
            self.fetch_robots()
            result.robots_permission = self.robots_result.get("can_crawl", True) if self.robots_result else True
            result.crawl_delay = self.crawl_delay
            
            # Check if crawling is allowed
            if not result.robots_permission:
                result.status = "stopped"
                result.errors.append("Crawling disallowed by robots.txt")
                result.end_time = time.time()
                result.duration = result.end_time - result.start_time
                return result
            
            # Initialize BFS
            visited: Set[str] = set()
            queue: deque = deque()
            
            # Start with base URL
            normalized_base = self.normalize_url(self.base_url)
            if normalized_base:
                queue.append((normalized_base, 0))  # (url, depth)
                visited.add(normalized_base)
            
            # Crawl loop
            while queue and len(visited) < self.config.max_pages:
                url, depth = queue.popleft()
                
                # Crawl the page
                page_result = self.crawl_page(url, depth)
                result.crawled_urls.append(url)
                result.pages_crawled += 1
                
                # Add to discovered URLs
                if url not in result.discovered_urls:
                    result.discovered_urls.append(url)
                
                # Add files
                for file_meta in page_result.get("files", []):
                    # Check if already discovered
                    already_found = any(
                        f["url"] == file_meta["url"] 
                        for f in result.discovered_files
                    )
                    if not already_found:
                        result.discovered_files.append(file_meta)
                        result.files_discovered += 1
                
                # Process links for next pages
                for link in page_result.get("links", set()):
                    if link not in visited:
                        should_crawl, reason = self.should_crawl_url(link, depth + 1, visited)
                        
                        if should_crawl:
                            visited.add(link)
                            queue.append((link, depth + 1))
                        
                        # Add to discovered URLs even if not crawled
                        if link not in result.discovered_urls:
                            result.discovered_urls.append(link)
                
                # Check for errors
                if page_result.get("error"):
                    result.errors.append(f"{url}: {page_result['error']}")
            
            result.status = "completed"
            
        except Exception as e:
            result.status = "error"
            result.errors.append(f"Crawl failed: {str(e)}")
        
        result.end_time = time.time()
        result.duration = result.end_time - result.start_time
        
        return result


# Standalone helper functions (for testing and external use)

def extract_links(html_content: str, base_url: str) -> List[str]:
    """
    Extract links from HTML content.
    
    Args:
        html_content: HTML content to parse
        base_url: Base URL for resolving relative links
        
    Returns:
        List of extracted URLs
    """
    crawler = WebsiteCrawler(base_url)
    return list(crawler.extract_links(html_content, base_url))


def normalize_url_for_crawling(url: str, base_url: str) -> str:
    """
    Normalize a URL for crawling.
    
    Args:
        url: URL to normalize
        base_url: Base URL
        
    Returns:
        Normalized URL
    """
    crawler = WebsiteCrawler(base_url)
    return crawler.normalize_url(url) or url


def filter_file_urls(urls: List[str]) -> List[str]:
    """
    Filter a list of URLs to only include file URLs.
    
    Args:
        urls: List of URLs to filter
        
    Returns:
        List of URLs that point to files
    """
    if not urls:
        return []
    
    # Use the first URL as base for domain checking
    base_url = urls[0]
    try:
        crawler = WebsiteCrawler(base_url)
        return [url for url in urls if crawler.is_scrapable_file_type(url)]
    except:
        return urls


def is_scrapable_file_type(file_extension: str) -> bool:
    """
    Check if a file extension is scrapable.
    
    Args:
        file_extension: File extension to check (e.g., "pdf", "docx")
        
    Returns:
        True if scrapable
    """
    ext = file_extension.lower()
    return ext in SCRAPABLE_FILE_TYPES and ext not in NON_SCRAPABLE_EXTENSIONS
