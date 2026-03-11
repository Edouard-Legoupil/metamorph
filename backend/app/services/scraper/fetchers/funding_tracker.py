from typing import List
from scraper.cache import CacheEntry, RawCache
from scraper.config import SourceConfig
import asyncio


async def fetch_funding_tracker(fetcher, cache: RawCache) -> List[CacheEntry]:
    """
    For the funding tracker (B17):
      - Launch Playwright w/ interception
      - Save all XHRs with content-type application/json (one CacheEntry per)
      - Save rendered HTML
      - If 0 API calls, flag notes
    """
    entries = []
    from playwright.async_api import async_playwright

    url = fetcher._build_playwright_url(fetcher.source_by_id("B17"), 1)
    api_responses = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        api_payloads = []

        def handle_response(response):
            ct = response.headers.get("content-type", "")
            if "application/json" in ct and (
                "powerbi" in response.url or "$format=json" in response.url
            ):
                api_payloads.append(
                    (response.url, asyncio.ensure_future(response.text()))
                )

        page.on("response", handle_response)
        await page.goto(url, wait_until="networkidle", timeout=45000)
        html = await page.content()
        html_entry = CacheEntry(
            url=url,
            source_id="B17",
            fetched_at=datetime.utcnow(),
            status_code=200,
            content_type="text/html",
            body=html,
            is_base64=False,
        )
        cache.set(url, html_entry)
        entries.append(html_entry)
        await browser.close()
        # Now get all JSON API responses
        count = 0
        for url, fut in api_payloads:
            try:
                body = await fut
                json_entry = CacheEntry(
                    url=url,
                    source_id="B17",
                    fetched_at=datetime.utcnow(),
                    status_code=200,
                    content_type="application/json",
                    body=body,
                    is_base64=False,
                )
                cache.set(url, json_entry)
                entries.append(json_entry)
                count += 1
            except Exception as ex:
                print(f"FundingTracker: failed to capture {url}: {ex}")
        if count == 0:
            print("FundingTracker: no-api-data-found")
    return entries
