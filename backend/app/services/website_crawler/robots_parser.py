"""
Robots.txt Parser Module (FR-001d, NFR-009)

Provides functionality to parse and respect robots.txt files.
Implements respectful scraping as per NFR-009.
"""
import re
import requests
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin

from .url_validator import URLValidationError, extract_domain

# Default user agent for Metamorph crawler
DEFAULT_USER_AGENT = "MetamorphBot/1.0"


def parse_robots_txt(content: str, url: str = "") -> Dict[str, Any]:
    """
    Parse robots.txt content and extract rules.
    
    Args:
        content: The robots.txt file content
        url: The URL of the robots.txt file (for context)
        
    Returns:
        Dictionary containing:
        - can_crawl: Whether crawling is allowed
        - crawl_delay: Crawl delay in seconds (None if not specified)
        - disallowed_paths: List of disallowed paths
        - allowed_paths: List of allowed paths
        - user_agents: List of user agents with specific rules
        
    Acceptance Criteria (FR-001d, NFR-009):
    - Parse robots.txt directives
    - Respect disallow rules
    - Extract crawl-delay
    - Handle user-agent specific rules
    """
    result = {
        "can_crawl": True,
        "crawl_delay": None,
        "disallowed_paths": [],
        "allowed_paths": [],
        "user_agents": [],
        "sitemaps": [],
    }
    
    if not content or not content.strip():
        # Empty robots.txt means all is allowed
        return result
    
    try:
        current_user_agent = None
        current_rules = {}
        
        for line in content.split('\n'):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Parse key-value pairs
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if key == 'user-agent':
                    # Save previous user agent rules
                    if current_user_agent:
                        result["user_agents"].append({
                            "user_agent": current_user_agent,
                            **current_rules
                        })
                    # Start new user agent rules
                    current_user_agent = value
                    current_rules = {}
                elif key == 'disallow':
                    if value:
                        if 'disallowed_paths' not in current_rules:
                            current_rules['disallowed_paths'] = []
                        current_rules['disallowed_paths'].append(value)
                elif key == 'allow':
                    if value:
                        if 'allowed_paths' not in current_rules:
                            current_rules['allowed_paths'] = []
                        current_rules['allowed_paths'].append(value)
                elif key == 'crawl-delay':
                    try:
                        current_rules['crawl_delay'] = int(value)
                    except ValueError:
                        pass  # Invalid crawl delay, ignore
                elif key == 'sitemap':
                    result["sitemaps"].append(value)
        
        # Save last user agent rules
        if current_user_agent:
            result["user_agents"].append({
                "user_agent": current_user_agent,
                **current_rules
            })
        
        # Find rules for our user agent or wildcard
        our_rules = None
        for ua_rules in result["user_agents"]:
            if ua_rules["user_agent"] == "*":
                our_rules = ua_rules
                break
        
        if not our_rules:
            # Check for our specific user agent
            for ua_rules in result["user_agents"]:
                if ua_rules["user_agent"] == DEFAULT_USER_AGENT:
                    our_rules = ua_rules
                    break
        
        # Apply our rules
        if our_rules:
            if 'disallowed_paths' in our_rules:
                result["disallowed_paths"] = our_rules['disallowed_paths']
            if 'allowed_paths' in our_rules:
                result["allowed_paths"] = our_rules['allowed_paths']
            if 'crawl_delay' in our_rules:
                result["crawl_delay"] = our_rules['crawl_delay']
            
            # If any path is disallowed, check if root is disallowed
            if '/' in result["disallowed_paths"]:
                result["can_crawl"] = False
            
            # Check for specific disallows
            if result["disallowed_paths"]:
                # If '/' is disallowed, crawling is not allowed
                if '/' in result["disallowed_paths"]:
                    result["can_crawl"] = False
        
    except Exception as e:
        # If parsing fails, default to allowed (fail-open)
        # This respects NFR-009: be respectful but don't break on errors
        pass
    
    return result


def is_path_allowed(path: str, robots_result: Dict[str, Any]) -> bool:
    """
    Check if a specific path is allowed based on robots.txt rules.
    
    Args:
        path: The path to check
        robots_result: Result from parse_robots_txt
        
    Returns:
        True if path is allowed, False otherwise
    """
    if not robots_result.get("disallowed_paths"):
        return True
    
    for disallowed in robots_result["disallowed_paths"]:
        if path.startswith(disallowed):
            return False
    
    # Check allowed paths (Allow takes precedence over Disallow)
    for allowed in robots_result.get("allowed_paths", []):
        if path.startswith(allowed):
            return True
    
    return True


def check_robots_permission(robots_content: str, base_url: str, user_agent: str = DEFAULT_USER_AGENT) -> bool:
    """
    Check if crawling is permitted based on robots.txt content.
    
    Args:
        robots_content: The robots.txt file content
        base_url: The base URL of the website
        user_agent: The user agent string to check
        
    Returns:
        True if crawling is permitted, False otherwise
        
    Acceptance Criteria (NFR-009):
    - Honor robots.txt directives
    - Respect website scraping policies
    """
    result = parse_robots_txt(robots_content, base_url)
    
    # If user agent is specifically disallowed
    for ua_rules in result["user_agents"]:
        if ua_rules["user_agent"] == user_agent:
            if ua_rules.get("disallowed_paths") and '/' in ua_rules["disallowed_paths"]:
                return False
    
    # Check wildcard rules
    for ua_rules in result["user_agents"]:
        if ua_rules["user_agent"] == "*":
            if ua_rules.get("disallowed_paths") and '/' in ua_rules["disallowed_paths"]:
                return False
    
    return result["can_crawl"]


def check_robots_permission_with_delay(robots_content: str, base_url: str, user_agent: str = DEFAULT_USER_AGENT) -> Dict[str, Any]:
    """
    Check robots permission and extract crawl delay.
    
    Args:
        robots_content: The robots.txt file content
        base_url: The base URL of the website
        user_agent: The user agent string to check
        
    Returns:
        Dictionary with can_crawl and crawl_delay
    """
    result = parse_robots_txt(robots_content, base_url)
    
    # Extract crawl delay for our user agent or wildcard
    crawl_delay = None
    for ua_rules in result["user_agents"]:
        if ua_rules["user_agent"] in (user_agent, "*"):
            if 'crawl_delay' in ua_rules:
                crawl_delay = ua_rules['crawl_delay']
            break
    
    return {
        "can_crawl": check_robots_permission(robots_content, base_url, user_agent),
        "crawl_delay": crawl_delay,
        "disallowed_paths": result.get("disallowed_paths", []),
        "sitemaps": result.get("sitemaps", []),
    }


def fetch_robots_txt(base_url: str, timeout: int = 5) -> Dict[str, Any]:
    """
    Fetch and parse robots.txt from a website.
    
    Args:
        base_url: The base URL of the website
        timeout: Timeout in seconds
        
    Returns:
        Dictionary containing:
        - url: The robots.txt URL
        - content: The robots.txt content
        - found: Whether robots.txt was found
        - can_crawl: Whether crawling is permitted
        - crawl_delay: Crawl delay in seconds (None if not specified)
        - disallowed_paths: List of disallowed paths
        - sitemaps: List of sitemap URLs
        
    Acceptance Criteria (FR-001d, NFR-009):
    - Fetch robots.txt from website
    - Parse and respect its directives
    - Fail-open: if robots.txt cannot be fetched, assume crawling is allowed
    """
    robots_url = urljoin(base_url, "/robots.txt")
    
    result = {
        "url": robots_url,
        "content": "",
        "found": False,
        "can_crawl": True,  # Default to allowed (fail-open)
        "crawl_delay": None,
        "disallowed_paths": [],
        "sitemaps": [],
    }
    
    try:
        response = requests.get(robots_url, timeout=timeout)
        
        if response.status_code == 200:
            result["found"] = True
            result["content"] = response.text
            
            # Parse the content
            parsed = parse_robots_txt(response.text, robots_url)
            result["can_crawl"] = parsed["can_crawl"]
            result["crawl_delay"] = parsed["crawl_delay"]
            result["disallowed_paths"] = parsed.get("disallowed_paths", [])
            result["sitemaps"] = parsed.get("sitemaps", [])
        elif response.status_code == 404:
            # robots.txt not found, assume crawling is allowed
            result["found"] = False
            result["can_crawl"] = True
        else:
            # Other errors, assume crawling is allowed
            result["found"] = False
            result["can_crawl"] = True
            
    except Exception:
        # Connection error or any other exception, assume crawling is allowed
        # Fail-open strategy as per NFR-009
        result["found"] = False
        result["can_crawl"] = True
    
    return result


def check_url_against_robots(url: str, robots_result: Dict[str, Any]) -> bool:
    """
    Check if a specific URL is allowed based on robots.txt rules.
    
    Args:
        url: The URL to check
        robots_result: Result from fetch_robots_txt
        
    Returns:
        True if URL is allowed, False otherwise
    """
    if not robots_result.get("found"):
        # No robots.txt found, assume allowed
        return True
    
    if not robots_result.get("can_crawl"):
        # Crawling is generally disallowed
        return False
    
    # Check specific path
    from urllib.parse import urlparse
    path = urlparse(url).path
    
    return is_path_allowed(path, robots_result)
