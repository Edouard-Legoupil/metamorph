import os
import httpx
from typing import Dict, Any, Optional


class WikiJSClient:
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = base_url or os.getenv(
            "WIKIJS_URL", "http://localhost:4100/api/"
        ).rstrip("/")
        self.api_key = api_key or os.getenv("WIKIJS_API_KEY", "changeme")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def publish_page(
        self,
        path: str,
        markdown: str,
        title: str,
        tags: list = None,
        description: str = "",
    ) -> Dict:
        url = f"{self.base_url}/pages"
        payload = {
            "path": path,
            "markdown": markdown,
            "title": title,
            "description": description,
            "tags": tags or [],
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    async def update_page(self, page_id: str, markdown: str, title: str = None) -> Dict:
        url = f"{self.base_url}/pages/{page_id}"
        payload = {"markdown": markdown}
        if title:
            payload["title"] = title
        async with httpx.AsyncClient() as client:
            resp = await client.put(url, json=payload, headers=self.headers)
            resp.raise_for_status()
            return resp.json()
