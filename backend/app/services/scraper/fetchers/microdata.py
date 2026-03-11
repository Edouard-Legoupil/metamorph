from typing import List
from scraper.cache import CacheEntry, RawCache
from scraper.config import SourceConfig
import json


async def fetch_microdata(fetcher, cache: RawCache) -> List[CacheEntry]:
    entries = []
    page = 1
    keep_going = True
    seen_ids = set()
    source = fetcher.source_by_id("A01")
    while keep_going and page <= source.max_pages:
        entry = await fetcher.fetch(source, page=page)
        if not entry:
            break
        page_json = json.loads(entry.body)
        datasets = page_json.get("datasets", [])
        if not datasets:
            break
        for ds in datasets:
            if ds.get("data_access_type") != "open":
                continue
            ds_id = ds.get("id")
            if not ds_id or ds_id in seen_ids:
                continue
            seen_ids.add(ds_id)
            if ds.get("direct_data_url"):
                pass  # parser handles metadata
        cache.set(entry.url, entry)
        entries.append(entry)
        page += 1
    return entries
