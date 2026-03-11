# CLI Manpage: Metamorph Knowledge Scraper & Curation Tools

## scraper: Universal Document Fetcher CLI

```
Usage:
    python -m scraper run --round N               # Run crawl for all sources in round N
    python -m scraper run --source SRCID          # Run crawl for one source (e.g. B16-iati)
    python -m scraper status                      # Show crawl/delivery status for all sources
    python -m scraper retry                       # Retry failed jobs (delivery will re-attempt failed POSTs)
    python -m scraper cache --stats               # Display cache statistics and usage per source
    python -m scraper cache --clear [--source S]  # Clear raw cache for all or one source
```

## curation_api: HTTP API (Manpage)

```
GET   /api/v1/curation/conflicts           # List all current curation queue items/conflicts
POST  /api/v1/curation/conflicts/:id/approve      # Approve a proposed value
POST  /api/v1/curation/conflicts/:id/reject       # Reject a proposed value
POST  /api/v1/curation/conflicts/:id/edit         # Edit/merge value interactively
POST  /api/v1/curation/conflicts/:id/escalate     # Escalate to next tier
GET   /api/v1/alerts/card/:card_id/alerts         # List unresolved/active alerts for card (for wiki banners)
GET   /api/v1/alerts/analytics                   # View alert stats, mean times to resolution
```

## agentic: MCP API Tools

```
GET /mcp/get_entity?entity_id=...           # Fetch entity/node + all edges
GET /mcp/search_knowledge?query=Q&limit=n   # Semantic vector search (only on verified knowledge)
GET /mcp/get_conflicts?status=UNRESOLVED    # List all conflicts (with details)
GET /mcp/get_document_triplets?document_id= # List all triplets for a doc
GET /mcp/get_wiki_page?page_id=abc          # Return wiki block markdown/state
GET /mcp/get_knowledge_card?card_id=KC-2    # Render a full knowledge card (all sections)
GET /mcp/events/stream                      # Stream server-sent events (SSE) for live changes
```

## Examples:

```
python -m scraper run --round 2
python -m scraper status
python -m scraper cache --clear --source B16-fr

# MCP Client Example:
curl -H "X-API-Key: $KEY" http://localhost:8000/mcp/search_knowledge?query=population

# Get all current delta alerts via API:
curl http://localhost:8000/api/v1/alerts/card/B16-main/alerts
```
