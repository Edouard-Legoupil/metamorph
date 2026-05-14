Build a standalone Python scraper module, organized as a subpackage, to orchestrate, fetch, and deliver UNHCR and related humanitarian open data to the Metamorph ingestion API. The scraper must:
- Maintain a registry of all sources, fetch methods, and schedules.
- Enforce robots.txt and domain rate limits, using disk cache for raw responses and enforcing job/round gating as in PIPELINE.md.
- Support HTTP and Playwright-based fetching with pagination, XHR/JSON interception, PDF handling, and content caching for all major UNHCR-facing and IATI/similar feeds.
- Persist and deliver raw content to the Metamorph ingestion API (not parsing or extracting entities at this stage). Track fetch metadata, job stats, failure/skip reasons, and cache all fetched content. CLI must support round-running, manual/discovery runs, delivery retries, cache clear/stats, and display real-time/final job statistics.
- Must comply with all listed constraints in spec: never parse/ingest outside API, cache before delivery, only use Playwright where required, gracefully handle authentication skips, and deliver unprocessed PDFs as base64.

Verification & Test Guidance
- [ ] All expected modules are present in scraper/ (config, cache, fetcher, robots, delivery, scheduler, CLI, fetchers/[src]).
- [ ] CLI commands (run, status, retry, cache clear/stats) are implemented and display job and cache state for all sources.
- [ ] Cache is populated, enforces TTL/unique rules, and delivery to /ingest API is observed in test or via logs.
- [ ] robots.txt and rate limiting are respected and documented in job logs (see skips, waits).
- [ ] PDF bytes are base64'd and only delivered, not parsed; round and job gating works as described.
- [ ] Manual test: run round 1 and ensure every source delivers, caches, skips where required, and logs match all schema and flow steps.