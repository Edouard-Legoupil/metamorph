# 📚 Auto-Generated API Documentation (docs/API_AUTO.md)

> To refresh: `python scripts/build_api_docs.py`

---

(This is a placeholder. Run the script above to snapshot all current FastAPI and MCP endpoints including parameters, types, and responses as exported by OpenAPI. The below is a sample structure.)

## /ingest (POST)
- Accepts: IngestPayload (source_id, url, content, fetched_at, ...)
- Returns: 201 (created), 422 (validation error)

## /api/v1/blocks/card/{card_id}/preview (GET)
- Returns: all wiki blocks for a card (markdown, trust, verification, ...)

## /api/v1/curation/conflicts (GET)
- Curation dashboard queue

## /api/v1/cards (GET, POST, PATCH)
- Cards listing, creation, update

## /api/v1/alerts/card/{card_id}/alerts (GET)
- Delta alerting

## /api/v1/trust/batch-route (POST)
- Batch trust-routing of triplets (auto/shadow/human escalation)

## /mcp/get_entity, search_knowledge, get_knowledge_card, ... (GET)
- All MCP tools, API-key required

---

To regenerate with all schema and parameter info, rerun the build script after any backend API change.
