from typing import List
from scraper.cache import CacheEntry, RawCache
from scraper.config import SourceConfig
from selectolax.parser import HTMLParser
import asyncio

NAV_PATHS = ["/news", "/stories", "/where-we-work", "/what-we-do"]


async def fetch_multilang(fetcher, source: SourceConfig) -> List[CacheEntry]:
    """
    For sites like UNHCR Arabic, French, Spanish:
      - Fetch homepage only
      - Extract all <a href> links from navigation
      - Filter to certain prefixes
      - Fetch each (up to 20), tagged with language/code
    """
    entries = []
    main_entry = await fetcher.fetch(source, page=1)
    if not main_entry:
        return entries
    entries.append(main_entry)
    fetcher.raw_cache.set(main_entry.url, main_entry)
    html = HTMLParser(main_entry.body)
    link_set = set()
    for a in html.css("a[href]"):
        href = a.attributes.get("href", "")
        if href.startswith("/") and any(href.startswith(p) for p in NAV_PATHS):
            full_url = source.url.rstrip("/") + href
            link_set.add(full_url)
    n_pages = 1
    for url in list(link_set)[:20]:
        try:
            fake_source = SourceConfig(**{**source.dict(), "url": url})
            e = await fetcher.fetch(fake_source, page=1)
            if e:
                fetcher.raw_cache.set(e.url, e)
                entries.append(e)
            n_pages += 1
            if n_pages >= 20:
                break
            await asyncio.sleep(source.rate_limit_ms / 1000)
        except Exception as ex:
            print(f"Multilang fetch fail: {url} -- {ex}")
    return entries
