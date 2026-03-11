Add a **standalone Python scraper** that sits in front of the existing FastAPI ingestion pipeline.

```
[ This module ]                        [ Your existing stack ]
  Source Registry
       ↓
  Scheduler / Round Gate
       ↓
  Fetcher (HTTP + robots.txt)
       ↓
  Raw Cache  ──────────────────────→  POST /ingest  (FastAPI)
       ↓                               { source_id, format, content, url, fetched_at }
  Delivery Client
```

It does **not** parse, extract entities, or write RDF. It hands off a payload and moves on.


---

## FILE STRUCTURE

```
scraper/
├── config.py          ← source registry + settings
├── cache.py           ← raw response cache (diskcache)
├── fetcher.py         ← HTTP + Playwright fetch logic
├── robots.py          ← robots.txt parser + enforcement
├── scheduler.py       ← round gate + APScheduler jobs
├── delivery.py        ← POST payload to FastAPI /ingest
├── fetchers/          ← one file per source requiring custom logic
│   ├── iati.py
│   ├── microdata.py
│   ├── ungm.py
│   ├── multilang.py
│   └── funding_tracker.py
├── cli.py             ← `python -m scraper run --round 1`
└── .env
```

Build each file completely before moving to the next.

---

## `config.py` — Source Registry

Define these two models and the full registry list.

```python
from pydantic import BaseModel
from typing import Literal

FetchStrategy = Literal["http", "playwright"]
PaginationStrategy = Literal["none", "offset", "page", "sitemap"]
SourceFormat = Literal["html", "xml", "json", "pdf"]

class SourceConfig(BaseModel):
    id: str
    label: str
    url: str
    format: SourceFormat
    round: Literal[1, 2, 3]
    fetch_strategy: FetchStrategy
    pagination: PaginationStrategy
    rate_limit_ms: int        # min ms between requests to this domain
    requires_auth: bool = False
    max_pages: int = 1        # hard cap — never exceed
    notes: str = ""
```

Populate `SOURCES: list[SourceConfig]` with exactly these entries:

| id | url | format | round | fetch_strategy | pagination | rate_limit_ms | max_pages |
|----|-----|--------|-------|----------------|------------|---------------|-----------|
| A01 | https://microdata.unhcr.org/index.php/api/catalog/search | json | 2 | http | offset | 1000 | 50 |
| A06 | https://www.ungm.org/Public/ContractAward?agencyEnglishAbbreviation=UNHCR | html | 3 | playwright | page | 3000 | 20 |
| A07 | https://www.unhcr.org/evaluation | html | 3 | http | page | 1500 | 30 |
| A10 | https://www.ungm.org/Public/Notice?agencyEnglishAbbreviation=UNHCR | html | 3 | playwright | page | 3000 | 20 |
| A12 | https://reporting.unhcr.org/operations | html | 1 | http | sitemap | 1500 | 100 |
| B02 | https://intranet.unhcr.org/en/about/strategic-directions.html | pdf | 1 | http | none | 0 | 1 |
| B16-pop | https://www.unhcr.org/population-data.html | html | 1 | http | none | 1000 | 1 |
| B16-fig | https://www.unhcr.org/figures-at-a-glance.html | html | 1 | http | none | 1000 | 1 |
| B16-main | https://www.unhcr.org/ | html | 1 | http | none | 2000 | 1 |
| B16-iati | https://reporting.unhcr.org/iati | xml | 2 | http | none | 500 | 1 |
| B16-help | https://help.unhcr.org/ | html | 1 | http | none | 1500 | 1 |
| B16-ar | https://www.unhcr.org/ar/ | html | 2 | http | none | 2000 | 1 |
| B16-fr | https://www.unhcr.org/fr/ | html | 2 | http | none | 2000 | 1 |
| B16-es | https://www.unhcr.org/es/ | html | 2 | http | none | 2000 | 1 |
| B17 | http://refugee-funding-tracker.org/ | html | 2 | playwright | none | 2000 | 1 |

Also define:

```python
class Settings(BaseModel):
    fastapi_ingest_url: str   # e.g. "http://localhost:8000/ingest"
    cache_dir: str = "./data/raw"
    cache_ttl_hours: dict[int, int] = {1: 24, 2: 6, 3: 6}  # per round
    max_concurrency: int = 3  # global async concurrency cap
    user_agent: str = "UNHCR-KG-Scraper/1.0 (research; contact: kg@unhcr.org)"
```

Load `Settings` from `.env` via `python-dotenv`.

---

## `cache.py` — Raw Response Cache

Use `diskcache.Cache` with the cache directory from Settings.

```python
class RawCache:
    def get(self, url: str) -> CacheEntry | None
    def set(self, url: str, entry: CacheEntry) -> None
    def is_fresh(self, url: str, ttl_hours: int) -> bool
    def invalidate(self, url: str) -> None
    def clear_source(self, source_id: str) -> None  # delete all entries tagged with source_id
    def stats(self) -> dict  # hit_count, miss_count, total_entries, size_mb
```

```python
class CacheEntry(BaseModel):
    url: str
    source_id: str
    fetched_at: datetime
    status_code: int
    content_type: str
    body: str           # always str — bytes are base64-encoded for PDFs
    is_base64: bool = False
    page_number: int = 1
```

Cache key: `sha256(url + str(page_number))` — so paginated pages are cached independently.

---

## `robots.py` — Robots.txt Enforcement

```python
class RobotsGuard:
    async def is_allowed(self, url: str) -> bool
    async def crawl_delay(self, domain: str) -> int | None  # returns Crawl-delay value if set
```

- Fetch and cache `robots.txt` per root domain (cache for 24h, separate from content cache)
- Parse with Python's `urllib.robotparser.RobotFileParser`
- Check against the configured `user_agent`
- If `is_allowed` returns False: do not fetch, mark job status `"skipped"`, log reason
- If `crawl_delay` returns a value: use `max(rate_limit_ms, crawl_delay * 1000)` as effective delay

---

## `fetcher.py` — Core Fetch Logic

```python
class Fetcher:
    async def fetch(self, source: SourceConfig, page: int = 1) -> CacheEntry | None
```

### HTTP fetcher (httpx)

- Async `httpx.AsyncClient` with `follow_redirects=True`, timeout 30s
- Set `User-Agent` from Settings
- For `format="pdf"`: fetch bytes, base64-encode, set `is_base64=True`
- For `format="json"` + `pagination="offset"`: build URL as `{base_url}?ps=50&from={(page-1)*50}`
- For `format="html"` + `pagination="page"`: build URL as `{base_url}&page={page}`
- For `pagination="sitemap"`: fetch `/sitemap.xml`, parse all `<loc>` URLs, enqueue each as a separate page fetch
- Retry with `tenacity`: 3 attempts, exponential backoff 2s/4s/8s, retry on 429/500/502/503
- On 429: respect `Retry-After` header if present
- Rate limiting: use `asyncio.sleep(rate_limit_ms / 1000)` between consecutive requests to the same domain

### Playwright fetcher

Use for sources where `fetch_strategy="playwright"` (UNGM pages, funding tracker).

```python
async def fetch_playwright(self, url: str) -> str:  # returns page HTML after JS render
```

- Launch headless Chromium
- Wait for `networkidle` before capturing HTML
- Intercept and log any XHR/fetch calls that return JSON (save them too — they may contain structured data)
- For funding tracker (B17): specifically intercept requests matching `*powerbi*` or `*$format=json*` and save the response body separately with suffix `-api-response`
- Close browser after each fetch (don't reuse across sources)
- Timeout: 45s

---

## `fetchers/` — Source-Specific Fetch Logic

Each file handles pagination and link discovery for one source family.  
They call `Fetcher.fetch()` internally and return a list of `CacheEntry` objects ready for delivery.

### `fetchers/iati.py`  (B16-iati)

The IATI feed may be a redirect to a file download or an XML index page.

```python
async def fetch_iati(fetcher: Fetcher, cache: RawCache) -> list[CacheEntry]:
```

1. Fetch the overview page with HTTP
2. Parse HTML with selectolax — find all `<a href>` pointing to `.xml` files
3. For each XML link: fetch and cache independently (one CacheEntry per XML file)
4. Also try `https://reporting.unhcr.org/iati/download` directly
5. Return all entries — the downstream parser will handle XML splitting

### `fetchers/microdata.py`  (A01)

```python
async def fetch_microdata(fetcher: Fetcher, cache: RawCache) -> list[CacheEntry]:
```

1. Page through the JSON API: `GET ?ps=50&from=0`, `?ps=50&from=50`, … until `datasets` is empty
2. For each dataset entry that has `data_access_type != "open"`, skip and log
3. For entries with `direct_data_url` populated: add the URL to a secondary fetch queue (these are the actual data files — fetch metadata only, not the data itself)
4. Return one CacheEntry per API page (not per dataset — let the parser split them)

### `fetchers/ungm.py`  (A06, A10)

```python
async def fetch_ungm(fetcher: Fetcher, source: SourceConfig) -> list[CacheEntry]:
```

1. Use Playwright to load the first page
2. After `networkidle`: check if there is a "Next" pagination button
3. If yes: click it, wait for `networkidle`, capture HTML — repeat up to `source.max_pages`
4. Also check for any "Export to CSV" or "Download" buttons — if present, click and save the downloaded file as a separate CacheEntry with `content_type="text/csv"`
5. On each page, look for detail-link `<a>` elements pointing to individual award/notice pages — do NOT follow them (let the parser decide)

### `fetchers/multilang.py`  (B16-ar, B16-fr, B16-es)

```python
async def fetch_multilang(fetcher: Fetcher, source: SourceConfig) -> list[CacheEntry]:
```

1. Fetch the homepage only (no deep crawl)
2. Extract all internal `<a href>` links from the main navigation using selectolax
3. Filter to only: `/news`, `/stories`, `/where-we-work`, `/what-we-do` path prefixes
4. Fetch each — up to 20 pages total per language — with the source's `rate_limit_ms`
5. Tag each entry with `source.id` so the parser knows the language

### `fetchers/funding_tracker.py`  (B17)

```python
async def fetch_funding_tracker(fetcher: Fetcher, cache: RawCache) -> list[CacheEntry]:
```

1. Launch Playwright with request interception enabled
2. Collect ALL XHR responses with `content-type: application/json` during page load
3. Save each JSON response as a separate CacheEntry keyed by its URL
4. Also save the rendered HTML
5. Log how many JSON payloads were intercepted — if 0, flag entry with `notes="no-api-data-found"`

---

## `delivery.py` — POST to FastAPI

```python
class IngestPayload(BaseModel):
    source_id: str
    format: SourceFormat
    url: str
    fetched_at: datetime
    content: str          # HTML/XML/JSON body, or base64 for PDF
    is_base64: bool = False
    page_number: int = 1
    content_type: str
    metadata: dict = {}   # any extra context (language, pagination offset, etc.)

class DeliveryClient:
    async def deliver(self, entry: CacheEntry, source: SourceConfig) -> bool
    async def deliver_batch(self, entries: list[CacheEntry], source: SourceConfig) -> DeliveryReport
```

- POST each `CacheEntry` as an `IngestPayload` to `Settings.fastapi_ingest_url`
- If FastAPI returns 200/201: mark delivered
- If FastAPI returns 422 (validation error): log body, mark `"rejected"`, do not retry
- If FastAPI returns 5xx: retry up to 3 times with 5s delay, then mark `"failed"`
- If FastAPI is unreachable: cache entries locally and retry on next scheduler tick
- Batch delivery: send up to 10 payloads concurrently, collect per-item results

```python
class DeliveryReport(BaseModel):
    source_id: str
    total: int
    delivered: int
    rejected: int
    failed: int
    errors: list[str]
```

---

## `scheduler.py` — Round Gate + Job Runner

```python
class ScraperScheduler:
    def run_round(self, round_number: int) -> None
    def run_source(self, source_id: str) -> None
    def get_status(self) -> dict
    def retry_failed(self) -> None
```

Round gating rules (enforce strictly):
- Round 2 sources will not start until **all** Round 1 sources have status `done` or `skipped`
- Round 3 sources will not start until **all** Round 2 sources have status `done` or `skipped`
- If a Round N source is `failed`, log a warning but do not block Round N+1 (allow operator override)

Job state persists to `./data/queue/scraper_jobs.json`. Fields per job:

```python
class JobState(BaseModel):
    source_id: str
    round: int
    status: Literal["pending", "running", "done", "failed", "skipped"]
    started_at: datetime | None = None
    completed_at: datetime | None = None
    pages_fetched: int = 0
    bytes_fetched: int = 0
    entries_delivered: int = 0
    error: str | None = None
    skip_reason: str | None = None
```

For each job execution:
1. Check `RobotsGuard.is_allowed()` — if blocked, set `status="skipped"`, `skip_reason="robots.txt"`
2. Check if `requires_auth=True` and env vars absent — set `status="skipped"`, `skip_reason="no-credentials"`
3. Call the appropriate fetcher (custom fetcher if in `fetchers/`, else generic `Fetcher.fetch()`)
4. On each page fetched: immediately deliver via `DeliveryClient` (stream, don't batch all pages first)
5. Respect `max_pages` hard cap
6. On completion: write final `JobState`, emit log line with summary stats

---

## `cli.py` — Command Line Interface

```bash
python -m scraper run --round 1
python -m scraper run --source B16-iati
python -m scraper status
python -m scraper retry
python -m scraper cache --stats
python -m scraper cache --clear --source A01
```

Use `rich` for all output:
- `run`: live progress table (source | status | pages | bytes | delivered) updating in place
- `status`: static table of all 15 sources with current job state + colour-coded status badges
- `cache --stats`: table showing entries per source, total size, oldest entry

----

## Apply Cloudfare Toke for UNHCR.org - and detect pdf doc 


```python
        # Check if this is a UNHCR PDF.js viewer URL
        is_unhcr_pdfjs = (parsed_url.netloc == "www.unhcr.org" and 
                          "/media/" in parsed_url.path)
        
        if parsed_url.netloc == "www.unhcr.org" or is_unhcr_pdfjs:
            logger.info("UNHCR URL detected, adding authentication headers and delay.")
            time.sleep(10)  # Add a 10-second delay
            client_id = os.getenv("cfAccessClientId")
            client_secret = os.getenv("cfAccessClientSecret")
            if client_id and client_secret:
                auth_token = f"{client_id}:{client_secret}"
                headers["Authorization"] = f"Bearer {auth_token}"
                headers["CF-Access-Client-Id"] = f"{client_id}"
            else:
                logger.warning("Cloudflare credentials not found in environment variables.")

        # Handle PDF.js viewer URLs - extract the actual PDF URL
        if is_unhcr_pdfjs:
            logger.info("UNHCR PDF.js viewer detected, extracting actual PDF URL.")
            # Extract the file parameter from query string
            query_params = parse_qs(parsed_url.query)
            file_param = query_params.get('file', [None])[0]
            
            if file_param:
                # Construct the actual PDF URL
                if file_param.startswith('/'):
                    # Absolute path
                    pdf_url = f"https://www.unhcr.org{file_param}"
                else:
                    # Relative path - construct based on current path
                    base_path = parsed_url.path.rsplit('/pdf.js/web/viewer.html', 1)[0]
                    pdf_url = f"https://www.unhcr.org{base_path}/{file_param}"
                
                logger.info(f"Extracted PDF URL: {pdf_url}")
                url = pdf_url  # Replace URL with the actual PDF URL

        logger.info("Sending GET request...")
        response = requests.get(url, timeout=20, headers=headers)
        logger.info(f"Received response with status code: {response.status_code}")
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "").lower()
        logger.info(f"Detected Content-Type: {content_type}")
```

---

## CONSTRAINTS

1. **Playwright only where specified.** Do not use it for `fetch_strategy="http"` sources — it's slower and heavier.
2. **One domain, one semaphore.** Use `asyncio.Semaphore` keyed by root domain to enforce `rate_limit_ms`. Never fire two concurrent requests to the same root domain.
3. **PDFs are not parsed here.** Fetch bytes, base64-encode, deliver to FastAPI as-is. No text extraction in this module.
4. **Auth sources skip gracefully.** B02 (intranet) will likely be inaccessible. `status="skipped"` is the correct outcome, not `"failed"`.
5. **Cache before delivering.** Always write to `RawCache` before POSTing to FastAPI. If delivery fails, the raw content is not lost.
7. **No entity extraction.** This module outputs raw HTTP responses. Zero NLP, zero RDF, zero ontology references.


