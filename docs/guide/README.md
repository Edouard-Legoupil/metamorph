# Metamorph: Humanitarian Knowledge Graph Platform

Transforms humanitarian documents, data, and web sources into a dynamic, curator-driven wiki and graph for UNHCR and partners.

## Main Pipeline Stages

1. Scraper fetches raw documents (PDF, HTML, JSON, XML) from trusted sources using robust registry and robots.txt enforcement.
2. Ingestion pipeline detects format, stores versioned copy, routes to Docling/MinerU for Markdown extraction.
3. Triplet extractor (LiteLLM-based) generates semantic triplets with confidence scoring, traceability, chunking.
4. Entity resolution with GLinker ensures all real-world entities are linked or shadowed with confidence.
5. Delta engine reconciles proposed triplets with graph, detects contradictions, classifies conflicts, and assigns curation routes.
6. Wiki block assembler and knowledge card templates enable real-time, sectioned, live-updating pages with graph queries per block.
7. Curation UI (dashboard, validation cards, in-wiki curation) manages approvals, trust routing, shadow updates, and agentic handoff.
8. MCP server exposes all knowledge graph and curation endpoints to LLM-powered agents with secure auth, SSE, webhooks, and audit logging.
