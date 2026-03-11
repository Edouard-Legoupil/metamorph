# Metamorph API Overview

## OpenAPI docs

To list all endpoints and schemas, call:

    python scripts/build_api_docs.py

and reference `docs/API_AUTO.md`

## Endpoints (selected)

### /ingest (POST)
- Accepts:
  - source_id, url, content, fetched_at, format, is_base64, content_type, metadata
- Returns: 200|201 or 422 (validation error)

### /api/v1/blocks/*
- Preview, trust actions, verification, flagging

### /api/v1/cards/*
- Knowledge card viewing, editing, approval, history

### /api/v1/curation/conflicts
- Dashboard and reviewer workflow
- ValidationCard actions (approve, reject, ...)

### /api/v1/alerts/*
- Delta alerting—get, acknowledge, snooze, analytics

### /mcp/* (Agentic and LLM access)
- All tools/resources described in AGENT.md
- SSE: /mcp/events/stream
- Auth: X-API-Key required

*See* `docs/API_AUTO.md` for full endpoint and schema dump.
