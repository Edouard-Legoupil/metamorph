import requests
import sseclient
from typing import Dict, Any, List


class MCPAgentClient:
    def __init__(self, api_key: str, mcp_base_url: str = "http://localhost:8000"):
        self.api_key = api_key
        self.mcp_base_url = mcp_base_url.rstrip("/")
        self.headers = {"X-API-Key": self.api_key}

    def _get(self, path: str, params: Dict[str, Any] = None):
        url = f"{self.mcp_base_url}{path}"
        response = requests.get(url, params=params, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_entity(self, **kwargs) -> dict:
        return self._get("/mcp/get_entity", kwargs)

    def search_knowledge(self, **kwargs) -> List[dict]:
        return self._get("/mcp/search_knowledge", kwargs)

    def get_conflicts(self, **kwargs) -> List[dict]:
        return self._get("/mcp/get_conflicts", kwargs)

    def get_document_triplets(self, document_id: str) -> List[dict]:
        return self._get("/mcp/get_document_triplets", {"document_id": document_id})

    def get_wiki_page(self, **kwargs) -> dict:
        return self._get("/mcp/get_wiki_page", kwargs)

    def get_knowledge_card(self, **kwargs) -> dict:
        return self._get("/mcp/get_knowledge_card", kwargs)

    def resource(self, resource_type: str, **kwargs) -> List[dict]:
        return self._get(f"/mcp/resource/{resource_type}", kwargs)

    def sse_listen(self, on_event, stream_path="/mcp/events/stream"):
        url = f"{self.mcp_base_url}{stream_path}"
        r = requests.get(url, headers=self.headers, stream=True)
        client = sseclient.SSEClient(r)
        for event in client.events():
            on_event(event.data)
