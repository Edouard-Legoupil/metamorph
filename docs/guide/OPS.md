# Metamorph Operational Playbook

## Scheduler & Scraper
- Use `python -m scraper run --round N` to trigger batch ingestion by round
- `python -m scraper status` for live progress and error states
- Raw fetch failures: check for robots.txt, 403s, and credentials
- Ingestion errors: view FastAPI logs and `/api/v1/alerts/card/{card_id}/alerts` for delivery and processing

## Monitoring
- REST `/api/v1/alerts/analytics` for trending open/closed alerts and mean time to resolution
- MCP `/mcp/events/stream` and webhook delivery for real-time notifications and integration with Slack/Teams
- Use MCP audit log to review curation and agent actions by user, route, and event type

## Data Safety
- All raw files cached by key (url+page) before delivery to ingestion; cache persistency is a guarantee against data loss
- Rejected or failed deliveries are retried, and never deleted unless intentionally cleared

## DevOps
- .env (`cfAccessClientId`/`cfAccessClientSecret`, `FASTAPI_INGEST_URL`) must be set before running in prod
- Regenerate API docs (as Markdown) with `python scripts/build_api_docs.py`
- MCP API Keys should be managed as secrets and rotated regularly
