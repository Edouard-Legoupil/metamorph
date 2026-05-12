# Metamorph Constitution (v3.0)

## 1. Project Principles
- **Human judgment is not optional:** The system assists curators; it does not replace judgment
- **Every claim must be traceable:** Provenance, website URL, file URL, date, and curator must be stored for every piece of knowledge
- **Honesty over presentation:** Surface difficulties, risks, and gaps
- **Expiry is a feature:** Validity periods enforced for all cards
- **Website-first:** Users start by defining websites to scrape, not by uploading documents manually

## 2. Technical Stack
- **Website Crawling:** Python (requests, BeautifulSoup) with Playwright fallback for JS sites
- **Document Parsing:** Docling, MinerU
- **Graph Storage:** Neo4j (Labeled Property Graph)
- **API:** FastAPI
- **Frontend:** React with TypeScript
- **Agentic System:** Mistral Vibe CLI, Claude Code, etc.

## 3. Workflow
1. **Website Definition:** User provides a URL to scrape
2. **Automatic Exploration:** System crawls the website and identifies all scrapable files
3. **File Selection:** User reviews discovered files and selects which ones to ingest
4. **Automatic Ingestion:** Selected files are automatically parsed and ingested into the knowledge graph
5. **Knowledge Processing:** Extracted knowledge goes through reconciliation, curation, and card generation workflows

## 4. Data Model
- **New Entities (v3.0):** Website, DiscoveredFile, ScrapeSession, IngestionJob, Document
- **Nodes:** Websites, DiscoveredFiles, Documents, Entities, Events, Interventions, Outcomes, Knowledge Cards
- **Edges:** Relationships (discovered_from, ingested_from, funded_by, affected_by, implemented_by, operates_in, covers)
- **Properties:** Provenance (source website URL, source file URL, download date, extraction date), validity period, curator, status, verification_state
