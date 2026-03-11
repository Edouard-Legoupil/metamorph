# Metamorph Developer Guide

## Project Structure

```
metamorph/
  backend/app/              # FastAPI backend (triplets, ingestion, wiki, curation, alerts, trust, MCP)
  scraper/                  # Standalone ingest/fetch delivery utility
  frontend/src/             # React UI, curation dashboard, block preview, workspace, agents
  mcp/                      # Agentic access, SSE, SDK, audit, webhook
  docs/                     # System and API docs
```

## Logging & Audit
- All major steps use logging and/or audit logging (see mcp/audit.py)
  - INFO: success flows (fetch, deliver, approve)
  - WARNING: robots.txt, non-open datasets, PDF fetch fails
  - ERROR: HTTP/network, ingestion reject, alert failed delivery
  - AUDIT: curation actions, agent/bot access, webhooks

## Adding New Content
- New scraper: add to `SOURCES` in `config.py`, optional fetcher in `fetchers/`
- New knowledge card/section: add to `card_templates.py` and YAML
- New curation/approval rules: implement via trust router or delta engine in backend
- New agentic access: add handler to `mcp/server.py` as @mcp_tool

## Testing
- Unit: pytest for backend, Playwright for frontend, fetchers, and scraper delivery
- E2E: test full document-to-card ingestion, shadow update, delta escalation, and agent verification flows

## Pipeline Invariants
- All raw content is cached on-disk before delivery
- Every major event is logged and audit-trailed
- Every knowledge card section/block is sourced from graph with traceable provenance
