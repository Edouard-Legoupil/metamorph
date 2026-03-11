from typing import List
from scraper.cache import CacheEntry, RawCache
from scraper.config import SourceConfig
import asyncio


async def fetch_ungm(fetcher, source: SourceConfig) -> List[CacheEntry]:
    entries = []
    max_pages = source.max_pages
    page_num = 1
    next_exists = True

    while page_num <= max_pages and next_exists:
        entry = await fetcher._fetch_playwright(source, page=page_num)
        if entry:
            entries.append(entry)
            fetcher.raw_cache.set(entry.url, entry)
        next_exists = "<a" in (entry.body or "") and "Next" in (entry.body or "")
        if "Export to CSV" in (entry.body or "") or "Download" in (entry.body or ""):
            print(f"Detected CSV export on page {page_num} for {source.id}")
        await asyncio.sleep(source.rate_limit_ms / 1000)
        page_num += 1
    return entries
