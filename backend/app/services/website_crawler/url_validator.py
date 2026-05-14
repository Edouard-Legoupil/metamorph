"""
URL Validation Module (FR-001)

Provides functionality to validate, normalize, and extract metadata from URLs.
"""
import re
from urllib.parse import urlparse, urlunparse
from typing import Dict, Any


class URLValidationError(Exception):
    """Raised when URL validation fails"""
    pass


def validate_url(url: str) -> str:
    """
    Validate a URL and return normalized version.
    
    Args:
        url: URL string to validate
        
    Returns:
        Normalized URL string
        
    Raises:
        URLValidationError: If URL is invalid
        
    Acceptance Criteria (FR-001):
    - Validates URL format
    - Checks URL is accessible (basic syntax check)
    - Extracts domain information
    """
    if not url or not isinstance(url, str):
        raise URLValidationError("Invalid URL: URL must be a non-empty string")
    
    # Parse the URL
    parsed = urlparse(url)
    
    # Check scheme
    if parsed.scheme not in ('http', 'https'):
        raise URLValidationError(
            f"Invalid URL: must start with http:// or https://, got '{parsed.scheme}://'"
        )
    
    # Check netloc (domain)
    if not parsed.netloc:
        raise URLValidationError("Invalid URL: missing domain/host")
    
    # Reconstruct URL with normalized scheme (lowercase)
    normalized = urlunparse((
        parsed.scheme.lower(),
        parsed.netloc,
        parsed.path,
        parsed.params,
        parsed.query,
        parsed.fragment
    ))
    
    # Remove trailing slash from path if present (but keep root /)
    if normalized.endswith('/') and len(normalized) > len(parsed.scheme) + 3:
        normalized = normalized.rstrip('/')
    
    # Remove duplicate slashes in path
    normalized = re.sub(r'(https?://[^/]+)/+', r'\1/', normalized)
    
    return normalized


def extract_domain(url: str) -> str:
    """
    Extract domain from URL.
    
    Args:
        url: URL string (can be validated or not)
        
    Returns:
        Domain string (e.g., "example.com", "www.unhcr.org")
        Port numbers are stripped from the domain.
    """
    parsed = urlparse(url)
    netloc = parsed.netloc
    # Strip port number if present
    if ':' in netloc:
        netloc = netloc.split(':')[0]
    return netloc


def validate_and_extract_metadata(url: str) -> Dict[str, Any]:
    """
    Validate URL and extract metadata.
    
    Args:
        url: URL string to validate and extract from
        
    Returns:
        Dictionary containing:
        - url: Normalized URL
        - domain: Domain name
        - scheme: URL scheme (http/https)
        - path: URL path
        - query: Query string (if any)
        - fragment: Fragment (if any)
        
    Raises:
        URLValidationError: If URL is invalid
    """
    validated_url = validate_url(url)
    parsed = urlparse(validated_url)
    
    return {
        "url": validated_url,
        "domain": parsed.netloc,
        "scheme": parsed.scheme,
        "path": parsed.path if parsed.path else "/",
        "query": parsed.query,
        "fragment": parsed.fragment,
        "port": parsed.port if parsed.port else None,
    }


def is_same_domain(url1: str, url2: str) -> bool:
    """
    Check if two URLs have the same domain.
    
    Args:
        url1: First URL
        url2: Second URL
        
    Returns:
        True if both URLs have the same domain, False otherwise
    """
    try:
        domain1 = extract_domain(url1)
        domain2 = extract_domain(url2)
        return domain1.lower() == domain2.lower()
    except:
        return False


def is_url_accessible(url: str, timeout: int = 5) -> bool:
    """
    Check if a URL is accessible (can be reached).
    
    Args:
        url: URL to check
        timeout: Timeout in seconds
        
    Returns:
        True if URL is accessible, False otherwise
    """
    import requests
    
    try:
        # Try HEAD request first (faster)
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        # Some servers don't support HEAD, try GET as fallback
        if response.status_code >= 400:
            response = requests.get(url, timeout=timeout, stream=True)
            response.close()
        return response.status_code < 400
    except requests.RequestException:
        return False


def get_website_title(url: str, timeout: int = 10) -> str:
    """
    Extract website title from URL.
    
    Args:
        url: URL to extract title from
        timeout: Timeout in seconds
        
    Returns:
        Website title or empty string if not found
    """
    import requests
    from bs4 import BeautifulSoup
    
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title
        if title:
            return title.string.strip()
        return ""
    except:
        return ""
