import os
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.security.api_key import APIKeyHeader
from starlette.concurrency import run_until_first_complete
from sse_starlette.sse import EventSourceResponse
from typing import List, Dict, Any
import time
from functools import wraps
import asyncio

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)
MCP_API_KEYS = [os.getenv("MCP_API_KEY", "changeme")]  # List of valid agent keys
client_requests = {}

app = FastAPI(title="Metamorph MCP Agentic Server")

RATE_LIMIT = 30  # requests per minute


# --- Auth + Rate limit ---
def auth_dep(api_key: str = Depends(API_KEY_HEADER)):
    if api_key not in MCP_API_KEYS:
        raise HTTPException(401, "Invalid MCP API Key")
    # rudimentary rate limit per key
    key = f"{api_key}_{int(time.time() // 60)}"
    client_requests[key] = client_requests.get(key, 0) + 1
    if client_requests[key] > RATE_LIMIT:
        raise HTTPException(429, "Rate limit exceeded")
    return api_key


# ---- MCP protocol decorator stubs ----
def mcp_tool(fn):
    fn._mcp_tool = True

    @wraps(fn)
    async def wrapper(*args, **kwargs):
        return await fn(*args, **kwargs)

    return wrapper


def mcp_resource(uri_template):
    def decorator(fn):
        fn._mcp_resource = uri_template

        @wraps(fn)
        async def wrapper(*args, **kwargs):
            return await fn(*args, **kwargs)

        return wrapper

    return decorator


# --- TOOLS ---
@mcp_tool
async def get_entity(
    entity_id: str = None, name: str = None, label: str = None
) -> dict:
    # TODO: Query Neo4j
    return {"entity": {"id": entity_id or name, "label": label, "edges": []}}


@mcp_tool
async def search_knowledge(
    query: str, limit: int = 20, verified_only: bool = True
) -> list:
    # TODO: Use vector store + metadata filter
    return [{"block_id": "b1", "content": "Sample...", "score": 0.96}]


@mcp_tool
async def get_conflicts(status: str = "UNRESOLVED", severity: str = None) -> list:
    # TODO: Query conflicts/journal
    return [{"conflict_id": "c1", "status": status, "severity": severity}]


@mcp_tool
async def get_document_triplets(document_id: str) -> list:
    # TODO: Lookup triplets by doc
    return [{"triplet_id": "t1", "confidence": 0.89, "page": 5}]


@mcp_tool
async def get_wiki_page(page_id: str = None, slug: str = None) -> dict:
    # TODO: Render from block assembler, include block verification statuses
    return {"page_id": page_id or slug, "blocks": []}


@mcp_tool
async def get_knowledge_card(card_id: str, include_sections: List[str] = None) -> dict:
    # TODO: Render card/sections by graph
    return {"card_id": card_id, "sections": []}


# --- RESOURCES ---
@mcp_resource("knowledge://{country}/{crisis_type}")
async def get_context_resources(country: str, crisis_type: str) -> list:
    # TODO: List cards for context
    return [f"KC-2-{country}-{crisis_type}"]


@mcp_resource("evidence://{outcome_code}")
async def get_evidence_resources(outcome_code: str) -> list:
    # TODO: List findings for UNHCR outcome
    return [f"OA-{outcome_code}"]


# ----- MCP PROTOCOL ENDPOINTS -----
@app.get("/mcp/{tool_name}")
async def call_tool(tool_name: str, request: Request, api_key: str = Depends(auth_dep)):
    tool = globals().get(tool_name)
    if not tool or not getattr(tool, "_mcp_tool", False):
        raise HTTPException(404, "Unknown MCP tool")
    params = dict(request.query_params)
    resp = await tool(**params)
    return resp


@app.get("/mcp/events/stream")
async def mcp_stream(request: Request, api_key: str = Depends(auth_dep)):
    # Demo: Server-sent events stub
    async def event_publisher():
        for i in range(5):
            yield {"data": f"ping {i}"}
            await asyncio.sleep(1)

    return EventSourceResponse(event_publisher())


@app.get("/mcp/resource/{resource_type}")
async def call_resource(
    resource_type: str, request: Request, api_key: str = Depends(auth_dep)
):
    # Extract params and dispatch resource
    resource_map = {
        "knowledge": get_context_resources,
        "evidence": get_evidence_resources,
    }
    resource_fn = resource_map.get(resource_type)
    if not resource_fn:
        raise HTTPException(404, "Unknown MCP resource")
    params = dict(request.query_params)
    resp = await resource_fn(**params)
    return resp
