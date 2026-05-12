# Metamorph Research Notes (v3.0 - Website-First)

**Spec ID:** 001-metamorph  
**Version:** 3.0  
**Status:** Draft  
**Date:** 2026-05-12

---

## Overview

This document captures research findings, technical decisions, and reference materials for Metamorph v3.0. **Key Change:** The system now starts with website URL input, automatically explores the site to discover files, allows user selection, and triggers automatic ingestion.

---

## 🌐 Website Crawling & Discovery Research (NEW)

### Website Crawling Approaches

#### Approach 1: Custom Crawler (Recommended)
**Implementation:** Python with `requests` + `BeautifulSoup` or `lxml`

**Pros:**
- Full control over crawling logic
- Easy to customize for humanitarian websites
- Can implement respectful scraping (NFR-009)
- Can parse sitemap.xml directly (FR-001b)
- Lightweight and fast

**Cons:**
- More development effort
- Need to handle edge cases manually
- No built-in JavaScript rendering

**Libraries:**
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `lxml` - Fast HTML/XML parsing
- `urllib.robotparser` - robots.txt parsing
- `aiohttp` - Async HTTP (for performance)

**Decision:** ✅ **Primary choice** - Custom crawler for full control

#### Approach 2: Scrapy Framework
**Implementation:** Python Scrapy framework

**Pros:**
- Mature, production-ready crawler framework
- Built-in support for robots.txt (NFR-009)
- Built-in support for sitemaps (FR-001b)
- Built-in rate limiting (NFR-010)
- Built-in item pipelines
- Extensible with middlewares

**Cons:**
- Steeper learning curve
- More complex to customize
- Overkill for simple crawling needs

**Libraries:**
- `scrapy` - Main framework
- `scrapy-splash` - JavaScript rendering
- `scrapy-proxy-pool` - Proxy rotation

**Decision:** ⚠️ **Backup option** - Use if custom crawler becomes too complex

#### Approach 3: Headless Browser (Playwright/Puppeteer)
**Implementation:** Node.js with Playwright or Puppeteer

**Pros:**
- Can handle JavaScript-heavy websites
- Can interact with pages (click buttons, fill forms)
- Can extract data from SPAs (Single Page Applications)
- Can render pages for preview generation

**Cons:**
- Resource intensive (CPU, memory)
- Slower than direct HTTP requests
- More complex setup
- Different language (Node.js vs Python backend)

**Libraries:**
- `playwright` - Cross-browser automation
- `puppeteer` - Chrome/Chromium automation

**Decision:** ⚠️ **Fallback for JS sites** - Use for websites that require JavaScript

#### Approach 4: Hybrid (Recommended)
**Implementation:** Custom Python crawler + Playwright for JS sites

**Strategy:**
1. Try custom crawler first (fast, lightweight)
2. Detect if site requires JavaScript (check for SPA indicators)
3. Fall back to Playwright for JavaScript-heavy sites
4. Cache results to avoid re-crawling

**Decision:** ✅ **Selected approach** - Best of both worlds

---

### File Discovery Strategies

#### Strategy 1: Sitemap.xml Parsing (High Priority - FR-001b)
**Implementation:** Parse `/sitemap.xml` and `/robots.txt` for sitemap locations

**Pros:**
- Structured, reliable source of URLs
- Includes metadata (lastmod, changefreq, priority)
- Fast to parse
- Standard across most websites

**Cons:**
- Not all websites have sitemaps
- May not include all files (especially dynamically generated)
- Format varies slightly between sites

**Implementation Notes:**
- Check common sitemap locations: `/sitemap.xml`, `/sitemap_index.xml`
- Parse XML and extract `<loc>` tags
- Handle sitemap index files (files that point to other sitemaps)
- Respect `<lastmod>` for incremental updates (FR-028)
- Extract file types from URLs

**Decision:** ✅ **Primary strategy** - Fast and reliable

#### Strategy 2: Crawl from Root URL (FR-001c)
**Implementation:** BFS/DFS crawl starting from user-provided URL

**Algorithm:**
```python
# Breadth-First Search (recommended for most sites)
def bfs_crawl(start_url, max_depth=3, max_pages=1000):
    visited = set()
    queue = Queue([(start_url, 0)])
    discovered_files = []
    
    while queue and len(visited) < max_pages:
        url, depth = queue.dequeue()
        if url in visited or depth > max_depth:
            continue
        
        visited.add(url)
        page = fetch(url)
        
        # Extract links
        links = extract_links(page, base_url=url)
        
        # Filter by same domain
        same_domain_links = filter_same_domain(links, start_url)
        
        # Identify scrapable files
        files = identify_scrapable_files(links)
        discovered_files.extend(files)
        
        # Queue new links
        for link in same_domain_links:
            if link not in visited:
                queue.enqueue((link, depth + 1))
    
    return discovered_files
```

**Pros:**
- Discovers files not in sitemap
- Can find deeply nested files
- Works on all websites

**Cons:**
- Slower than sitemap parsing
- May miss files behind forms/login
- Resource intensive for large sites

**Optimizations:**
- Use BFS for most sites (finds files closer to root faster)
- Use DFS for deep hierarchical sites
- Limit depth (configurable, default=3)
- Limit total pages (configurable, default=1000)
- Respect robots.txt crawl-delay

**Decision:** ✅ **Secondary strategy** - Use after sitemap parsing

#### Strategy 3: Direct File Pattern Matching
**Implementation:** Check common file paths directly

**Patterns:**
```
Documents:
- /documents/*.pdf
- /downloads/*.pdf
- /reports/*.pdf
- /publications/*.pdf
- /files/*.docx
- /files/*.xlsx

Media:
- /media/*.jpg
- /media/*.png
- /images/*.jpg

Data:
- /data/*.csv
- /data/*.json
- /exports/*.xlsx
```

**Pros:**
- Fast for known patterns
- Works even if files not linked
- Can find files behind broken links

**Cons:**
- Only finds files matching known patterns
- May produce false positives
- Website-specific patterns needed

**Decision:** ⚠️ **Optional enhancement** - Can be added for known humanitarian sites

---

### File Type Detection (FR-001a)

#### Method 1: URL Extension Matching
**Implementation:** Match file extensions in URLs

**Extensions to Detect:**
```python
SCRAPABLE_EXTENSIONS = {
    # Documents
    '.pdf': 'pdf',
    '.doc': 'word',
    '.docx': 'word',
    '.rtf': 'word',
    
    # Spreadsheets
    '.xls': 'excel',
    '.xlsx': 'excel',
    '.csv': 'csv',
    '.ods': 'spreadsheet',
    
    # Presentations
    '.ppt': 'powerpoint',
    '.pptx': 'powerpoint',
    '.odp': 'presentation',
    
    # Text
    '.txt': 'text',
    '.md': 'text',
    '.text': 'text',
    
    # Web
    '.html': 'html',
    '.htm': 'html',
    
    # Data
    '.json': 'json',
    '.xml': 'xml',
    
    # Archives (optional)
    '.zip': 'archive',
    '.rar': 'archive',
}
```

**Pros:**
- Fast and simple
- Works without downloading file
- Low resource usage

**Cons:**
- URL may not reflect actual content type
- Some sites use URL rewriting
- May miss files with non-standard extensions

**Decision:** ✅ **Primary method** - Fast and effective

#### Method 2: Content-Type Header
**Implementation:** Send HEAD request and check Content-Type header

**Example:**
```python
import requests

def get_content_type(url):
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        return response.headers.get('Content-Type', '')
    except:
        return None

# Map Content-Type to file type
CONTENT_TYPE_MAP = {
    'application/pdf': 'pdf',
    'application/msword': 'word',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'word',
    'application/vnd.ms-excel': 'excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'excel',
    'application/vnd.ms-powerpoint': 'powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'powerpoint',
    'text/html': 'html',
    'text/plain': 'text',
    'text/csv': 'csv',
    'application/json': 'json',
}
```

**Pros:**
- More accurate than URL extension
- Works with URL rewriting
- Standard HTTP method

**Cons:**
- Requires additional HTTP request
- Slower for large numbers of files
- Some servers don't return correct Content-Type

**Decision:** ⚠️ **Secondary validation** - Use to confirm URL-based detection

#### Method 3: File Content Sniffing
**Implementation:** Download first few bytes and detect file type

**Libraries:**
- `python-magic` - File type detection from content
- `filetype` - Pure Python file type detection

**Pros:**
- Most accurate detection
- Works regardless of URL or headers

**Cons:**
- Requires downloading file content
- Slow for large numbers of files
- Resource intensive

**Decision:** ❌ **Not recommended** - Too slow for discovery phase

---

### File Preview Generation (FR-002c)

#### Text Files (.txt, .csv, .json)
**Implementation:** Read first N bytes/lines

```python
def preview_text_file(url, max_chars=500):
    response = requests.get(url, timeout=10)
    content = response.text
    return content[:max_chars] + ('...' if len(content) > max_chars else '')
```

**Pros:** Fast, simple
**Cons:** Need to download file

#### PDF Files
**Implementation:** Use `PyPDF2` or `pdfminer.six`

```python
from PyPDF2 import PdfReader
import io
import requests

def preview_pdf(url, max_chars=500):
    response = requests.get(url, timeout=10)
    pdf_reader = PdfReader(io.BytesIO(response.content))
    first_page = pdf_reader.pages[0]
    text = first_page.extract_text()
    return text[:max_chars] + ('...' if len(text) > max_chars else '')
```

**Libraries:**
- `PyPDF2` - Simple PDF reading
- `pdfminer.six` - More robust PDF text extraction
- `pypdf` - Modern PDF library

**Decision:** ✅ **Use PyPDF2** - Fast and sufficient for preview

#### Word Documents
**Implementation:** Use `python-docx` or `textract`

```python
from docx import Document
import io
import requests

def preview_word(url, max_chars=500):
    response = requests.get(url, timeout=10)
    doc = Document(io.BytesIO(response.content))
    text = '\n'.join([para.text for para in doc.paragraphs])
    return text[:max_chars] + ('...' if len(text) > max_chars else '')
```

**Libraries:**
- `python-docx` - Word document reading
- `textract` - Multi-format text extraction
- `docx2txt` - Simple Word to text

**Decision:** ✅ **Use python-docx** - Good balance of features and simplicity

#### HTML Pages
**Implementation:** Extract text from HTML

```python
from bs4 import BeautifulSoup
import requests

def preview_html(url, max_chars=500):
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Remove script and style elements
    for script in soup(['script', 'style']):
        script.decompose()
    text = soup.get_text()
    # Clean up whitespace
    text = ' '.join(text.split())
    return text[:max_chars] + ('...' if len(text) > max_chars else '')
```

**Pros:** Fast, built into crawler
**Cons:** May include boilerplate text

---

### Rate Limiting & Respectful Scraping (NFR-009, NFR-010)

#### Rate Limiting Strategies

**1. Fixed Delay**
```python
import time

def fetch_with_delay(url, delay=1.0):
    time.sleep(delay)
    return requests.get(url)
```

**Pros:** Simple, predictable
**Cons:** Same delay for all sites, may be too slow or too fast

**2. Adaptive Delay (Recommended)**
```python
import time

def fetch_with_adaptive_delay(url, base_delay=1.0, last_request_time=None):
    if last_request_time:
        elapsed = time.time() - last_request_time
        delay = max(0, base_delay - elapsed)
        time.sleep(delay)
    return requests.get(url), time.time()
```

**Pros:** Maintains consistent rate, efficient
**Cons:** Slightly more complex

**3. Token Bucket**
```python
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=10, period=1)  # 10 requests per second
climited_request = requests.get
```

**Pros:** Flexible, allows bursts
**Cons:** More complex to implement

**Decision:** ✅ **Adaptive delay** - Simple and effective

#### robots.txt Compliance (NFR-009)

**Implementation:**
```python
from urllib.robotparser import RobotFileParser

def check_robots_txt(base_url, user_agent='MetamorphBot/1.0'):
    robots_url = f"{base_url.rstrip('/')}/robots.txt"
    rp = RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
        crawl_delay = rp.crawl_delay(user_agent)
        can_fetch = rp.can_fetch(user_agent, base_url)
        return can_fetch, crawl_delay
    except:
        # If robots.txt not found or error, assume crawling is allowed
        return True, 0
```

**Rules:**
- Always check robots.txt before crawling
- Respect `Disallow` directives
- Respect `Crawl-delay` if specified
- Use custom user-agent: `MetamorphBot/1.0`
- Cache robots.txt for 24 hours

**User-Agent String:**
```
MetamorphBot/1.0 (+https://metamorph.example.com/bot-info)
```

**Decision:** ✅ **Mandatory** - Must comply with robots.txt

#### Error Handling & Retries

**Retry Strategy:**
```python
import time
import requests
from requests.exceptions import RequestException

def fetch_with_retry(url, max_retries=3, backoff_factor=2):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response
            elif response.status_code == 429:  # Too Many Requests
                delay = backoff_factor ** attempt
                time.sleep(delay)
            elif response.status_code >= 500:  # Server Error
                delay = backoff_factor ** attempt
                time.sleep(delay)
            else:
                return response  # Return non-200 response
        except RequestException as e:
            delay = backoff_factor ** attempt
            time.sleep(delay)
    
    raise Exception(f"Failed after {max_retries} retries: {url}")
```

**HTTP Status Codes:**
- `200 OK` - Success
- `403 Forbidden` - Respect, do not retry
- `404 Not Found` - Skip, do not retry
- `429 Too Many Requests` - Retry with backoff
- `5xx Server Error` - Retry with backoff
- `Timeout` - Retry with backoff

**Decision:** ✅ **Exponential backoff** - Standard best practice

---

## 📚 Technology Research (Updated)

### Document Parsing Libraries (Updated for v3.0)

#### Docling (FR-004)
- **Website:** https://github.com/DS4SD/Docling
- **Use Case:** Standard document formats (PDF, Word, HTML)
- **Decision:** ✅ **Primary parser** - High accuracy, actively maintained

#### MinerU (FR-004)
- **Website:** https://github.com/wirelesscosmos/mineru
- **Use Case:** Complex document layouts, forms, tables
- **Decision:** ✅ **Secondary parser** - Specialized for complex layouts

#### Combined Approach (Updated)
- Use Docling as primary parser
- Use MinerU for complex layouts
- Fallback: Docling → MinerU → Manual
- **NEW:** Add fallback to raw text extraction for unparseable files
- **NEW:** Store which parser was used for each document

### Web Crawling Libraries (NEW)

#### Requests + BeautifulSoup
- **Use Case:** Custom crawler implementation
- **Decision:** ✅ **Primary choice** - Full control, lightweight

#### Scrapy
- **Use Case:** Full-featured crawling framework
- **Decision:** ⚠️ **Backup option** - If custom crawler becomes too complex

#### Playwright
- **Use Case:** JavaScript-heavy websites
- **Decision:** ⚠️ **Fallback** - For sites requiring JS rendering

#### aiohttp
- **Use Case:** Async HTTP requests for performance
- **Decision:** ⚠️ **Optional** - Can be added for high-performance crawling

---

### Graph Databases

#### Neo4j (Updated for v3.0)
- **Status:** ✅ **Primary choice**
- **Schema Updates for v3.0:**
  - Add Website nodes
  - Add DiscoveredFile nodes
  - Add ScrapeSession nodes
  - Add IngestionJob nodes
  - Add Document nodes
  - Add new relationship types (DISCOVERED, INGESTED, SCRAPED, PROCESSED)
  - Add provenance properties (website_url, file_url, discovered_at, ingested_at)

---

## 🏗️ Architecture Decisions (Updated)

### Decision 1: Crawler Architecture
**Decision:** Python-based custom crawler with fallback to Playwright

**Rationale:**
- Python aligns with backend stack
- Custom crawler gives full control
- Playwright fallback handles JS sites
- Respectful scraping is mandatory (NFR-009)

**Implementation:**
```
┌─────────────────┐
│   Crawler        │
│  Controller      │
└─────────┬───────┘
          │
    ┌─────┴─────┐
    │           │
┌───▼───┐   ┌───▼───┐
│Custom  │   │Playwright│
│Crawler │   │  (JS)   │
└────────┘   └────────┘
     │             │
     └──────┬──────┘
            │
     ┌──────▼──────┐
     │   Queue      │
     │   Manager    │
     └──────┬──────┘
            │
     ┌──────▼──────┐
     │   Database   │
     │   (Neo4j)    │
     └─────────────┘
```

### Decision 2: Crawling Strategy
**Decision:** Sitemap-first, then crawl, then pattern matching

**Rationale:**
- Sitemap is fastest and most reliable
- Crawling finds files not in sitemap
- Pattern matching catches files behind broken links

**Priority Order:**
1. Parse sitemap.xml (FR-001b)
2. Crawl from root URL (FR-001c)
3. Check common file patterns (optional)

### Decision 3: Preview Generation Strategy
**Decision:** Generate previews on-demand with caching

**Rationale:**
- On-demand avoids unnecessary processing
- Caching improves performance for repeated previews
- Balance between speed and resource usage

**Implementation:**
- Cache previews in Redis
- TTL: 24 hours
- Max cache size: 1000 previews
- Fallback to "Preview unavailable" if error

---

## 📊 Knowledge Domain Research (Unchanged)

[Previous domain research remains valid - see sections below]

---

## 🔬 Extraction Patterns Research (Updated)

### Confidence Scoring (Updated for v3.0)

**Factors:**
- Parser confidence: 0-1
- Source reliability: 0-1 (website domain reputation + file metadata)
- Extraction method: rule-based=0.9, ML=0.7, manual=1.0
- Corroboration: number of sources (1=1, 2=0.95, 3+=0.98)
- Freshness: days since publication (0-30=1, 31-90=0.9, 91-180=0.7, 181+=0.5)
- **NEW:** Website reliability: known domains=0.95, new domains=0.7

**Formula:**
```
confidence = (parser_confidence * 0.25 + 
              source_reliability * 0.25 + 
              extraction_method * 0.20 + 
              corroboration * 0.10 + 
              freshness * 0.10 + 
              website_reliability * 0.10)
```

### Website Domain Reliability

**Classification:**
- **Trusted (0.95):**
  - UN domains (un.org, unhcr.org, unicef.org, etc.)
  - Government domains (.gov, .gob, etc.)
  - Academic domains (.edu)
  - Known NGO domains

- **Known (0.85):**
  - Major news organizations
  - Established think tanks
  - International organizations

- **Unknown (0.70):**
  - New domains not in database
  - Requires manual review

- **Untrusted (0.30):**
  - Known problematic domains
  - Social media platforms
  - User-generated content sites

**Implementation:**
- Maintain domain reliability database
- Allow manual override
- Update based on curator feedback

---

## 🎯 Trust Routing Research (Updated)

### Source Reliability (Updated for v3.0)

**Trusted Sources:**
- UN official websites (un.org, unhcr.org, unicef.org, undp.org, etc.)
- Government websites (.gov, .gob, .mil, etc.)
- Academic institutions (.edu)
- Established NGOs (redcross.org, oxfam.org, etc.)
- **NEW:** Known humanitarian organizations

**Unverified Sources:**
- News articles (mainstream media)
- NGO reports (lesser known organizations)
- Social media (verified accounts)

**Untrusted Sources:**
- Social media (unverified)
- Rumors
- Anonymous sources
- **NEW:** Domains flagged as problematic

---

## 📈 Performance Benchmarks (Updated)

### Crawling Performance (NEW)
| Metric | Target | Current |
|--------|--------|---------|
| Pages crawled per minute | 100-200 | TBD |
| Files discovered per minute | 50-100 | TBD |
| Crawl completion time (500 pages) | <5 minutes | TBD |
| Memory usage per crawl | <100MB | TBD |
| CPU usage per crawl | <50% | TBD |

### File Discovery Performance (NEW)
| File Type | Discovery Time | Preview Time |
|-----------|----------------|--------------|
| PDF | <1s | <2s |
| Word | <1s | <2s |
| Excel | <1s | <2s |
| HTML | <1s | <1s |
| Text | <1s | <1s |

### Ingestion Performance (Updated)
| Metric | Target | Current |
|--------|--------|---------|
| Files queued per second | 50 | TBD |
| Files downloaded per second | 10 | TBD |
| Files parsed per second | 5 | TBD |
| Concurrent ingestion jobs | 10 | TBD |

### System Scalability (Updated)
| Metric | Target | Current |
|--------|--------|---------|
| Concurrent crawls | 50 | TBD |
| Websites stored | 10,000 | TBD |
| Discovered files stored | 1,000,000 | TBD |
| Documents ingested | 500,000 | TBD |
| API requests/second | 100 | TBD |

---

## 🔒 Security Research (Updated)

### Data Provenance (NFR-002 - Updated)
**Requirements:**
- Every claim must be traceable to source website
- Every claim must be traceable to source file
- Every claim must include discovery metadata
- Every claim must include ingestion metadata

**Implementation:**
```python
@dataclass
class KnowledgeProvenance:
    website_id: str
    website_url: str
    discovered_file_id: str
    file_url: str
    file_type: str
    discovered_at: datetime
    scrape_session_id: str
    ingestion_job_id: str
    ingested_at: datetime
    parsing_tool: str  # docling, mineru, manual
    parsed_at: datetime
    confidence_score: float
    source_reliability: float
```

---

## 🌍 Humanitarian Context Research (Unchanged)

[Previous humanitarian context research remains valid]


---

## 📝 Open Questions (Updated)

### Website Crawling
1. **Crawling Depth:** What should be the default max depth? (Recommended: 3)
2. **Page Limit:** What should be the default max pages per crawl? (Recommended: 1000)
3. **Rate Limiting:** What delay between requests? (Recommended: 1-2 seconds)
4. **Concurrent Crawls:** How many websites can we crawl simultaneously? (Recommended: 10-20)
5. **JavaScript Sites:** How to handle single-page applications? (Fallback to Playwright)
6. **Authentication:** How to store credentials securely for protected sites?
7. **Large Sites:** How to handle websites with 10,000+ pages? (Incremental crawling)

### File Discovery
1. **File Size Limit:** What's the maximum file size to attempt preview? (Recommended: 10MB)
2. **Preview Cache:** How long to cache previews? (Recommended: 24 hours)
3. **Preview Length:** How many characters to extract for preview? (Recommended: 500)
4. **Binary Files:** Should we attempt to preview binary files? (Recommended: No, metadata only)

### Ingestion
1. **Queue Priority:** How to prioritize files in the queue? (Recommended: User-selected order)
2. **Download Retries:** How many retries for failed downloads? (Recommended: 3)
3. **Download Timeout:** What timeout for file downloads? (Recommended: 30 seconds)
4. **Parallel Processing:** How many files to process simultaneously? (Recommended: 5-10)

### Legal/Compliance
1. **Robots.txt Compliance:** How to handle sites that block all crawlers? (Recommended: Skip)
2. **Rate Limit Detection:** How to detect and respond to rate limiting? (Exponential backoff)
3. **DMCA Takedowns:** Process for handling copyright complaints?
4. **Data Retention:** How long to store downloaded files? (Recommended: Until ingestion complete, then delete)

---

## 📚 References (Updated)

### Crawling & Scraping
- [Robots.txt Specification](https://developers.google.com/search/docs/crawling-indexing/robots/intro)
- [Sitemap Protocol](https://www.sitemaps.org/protocol.html)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Scrapy Documentation](https://docs.scrapy.org/)
- [Playwright Documentation](https://playwright.dev/)
- [Respectful Web Scraping Guide](https://www.scrapingbee.com/blog/web-scraping-101/)

### Legal & Ethical
- [Google's Webmaster Guidelines](https://support.google.com/webmasters/answer/35769?hl=en)
- [GDPR Compliance for Web Scraping](https://gdpr-info.eu/)
- [Copyright Law for Web Scraping](https://www.copyright.gov/)

### Research Papers
- [Polite Web Crawling](https://dl.acm.org/doi/10.1145/335189.335436)
- [Focused Crawling](https://dl.acm.org/doi/10.1145/345342.345456)
- [Incremental Web Crawling](https://dl.acm.org/doi/10.1145/502585.502603)

---

## 🔄 Revision History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2026-05-12 | 3.0 | Edouard Legoupil | Major update for website-first workflow. Added comprehensive website crawling research: crawler approaches (custom, Scrapy, Playwright), file discovery strategies (sitemap, crawling, pattern matching), file type detection methods, preview generation techniques, rate limiting and respectful scraping strategies, error handling and retry logic. Updated technology research, architecture decisions, performance benchmarks, and open questions. Added new references for web scraping. |
| 2026-04-12 | 1.0 | Edouard Legoupil | Initial research document created |
