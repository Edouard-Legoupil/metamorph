from typing import List
from scraper.cache import CacheEntry, RawCache
from scraper.config import SourceConfig
from selectolax.parser import HTMLParser


async def fetch_iati(fetcher, cache: RawCache) -> List[CacheEntry]:
    overview_entry = await fetcher.fetch(fetcher.source_by_id("B16-iati"))
    if not overview_entry:
        return []
    html = HTMLParser(overview_entry.body)
    xml_links = []
    for a in html.css('a[href$=".xml"]'):
        link = a.attributes.get("href")
        if link.startswith("/"):
            link = "https://reporting.unhcr.org" + link
        xml_links.append(link)
    entries = []
    for xml_url in xml_links:
        try:
            xml_entry = await fetcher._fetch_http(
                SourceConfig(
                    id="B16-iati",
                    label="IATI Feed",
                    url=xml_url,
                    format="xml",
                    round=2,
                    fetch_strategy="http",
                    pagination="none",
                    rate_limit_ms=500,
                    max_pages=1,
                ),
                page=1,
            )
            if xml_entry:
                cache.set(xml_url, xml_entry)
                entries.append(xml_entry)
        except Exception:
            continue
    dl_url = "https://reporting.unhcr.org/iati/download"
    try:
        dl_entry = await fetcher._fetch_http(
            SourceConfig(
                id="B16-iati",
                label="IATI Feed",
                url=dl_url,
                format="xml",
                round=2,
                fetch_strategy="http",
                pagination="none",
                rate_limit_ms=500,
                max_pages=1,
            ),
            page=1,
        )
        if dl_entry:
            cache.set(dl_url, dl_entry)
            entries.append(dl_entry)
    except Exception:
        pass
    return entries
