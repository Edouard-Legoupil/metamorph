# Metamorph Task List (v3.0 - Website-First)

## Phase 1: Website Crawling & File Discovery
- [x] Implement URL input and validation
- [x] Build website crawler with robots.txt support
- [x] Parse sitemap.xml for file discovery
- [x] Implement BFS/DFS crawling strategy
- [x] Identify scrapable file types (PDF, Word, Excel, PowerPoint, HTML, text)
- [x] Extract file metadata (name, URL, size, last modified)
- [x] Implement rate limiting and adaptive delay
- [x] Handle authentication (basic auth, session cookies)
- [x] Create file list UI with categorization by type
- [x] Implement file preview (text, PDF, Word, HTML)
- [x] Add bulk selection controls (Select All, by Type, by Date Range)
- [x] Implement search and filter for discovered files
- [x] Connect website input to crawler and file list

## Phase 2: Automatic Ingestion & Processing
- [x] Implement automatic ingestion trigger on user confirmation
- [x] Create ingestion queue system with progress tracking
- [x] Implement file download from URLs
- [x] Handle download errors and retries with exponential backoff
- [x] Integrate Docling for standard document parsing
- [x] Integrate MinerU for complex document layouts
- [x] Create unified parsing interface with fallback
- [x] Set up Neo4j for v3.0 schema (Website, DiscoveredFile, ScrapeSession, IngestionJob, Document)
- [x] Add provenance tracking: website URL, file URL, download date, extraction date

## Phase 3: Semantic Extraction & Knowledge Graph
- [x] Design semantic triplet schema
- [x] Implement entity recognition for 8 humanitarian domains
- [x] Implement relationship extraction
- [x] Add extraction confidence scoring
- [x] Store triplets in Neo4j with provenance
- [x] Create knowledge graph validation

## Phase 4: Knowledge Reconciliation
- [x] Implement delta detection engine
- [x] Build trust routing system (consider website domain reputation)
- [x] Create validation card workflow
- [x] Implement curation interface (MVP)
- [x] Add verification state transitions

## Phase 5: Knowledge Cards
- [x] Define templates for KC-1 to KC-6
- [x] Implement card generation from graph data
- [x] Add card approval and expiry workflows
- [x] Build card management interface

## Phase 6: Agentic Proposal Drafting & Deployment
- [x] Implement agentic proposal drafting
- [x] Deploy three knowledge surfaces
- [x] Deploy API layer with authentication
- [x] Set up staging environment

## Phase 7: Advanced Features & Production
- [x] Implement website scraping scheduling
- [x] Implement incremental updates (only process new/changed files)
- [x] Deploy watchers and notifications
- [x] Implement community trust scoring
- [x] Full production deployment
