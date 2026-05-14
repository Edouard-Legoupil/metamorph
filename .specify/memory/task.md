# Metamorph Task List (v3.0 - Website-First)

## Phase 1: Website Crawling & File Discovery
- [ ] Implement URL input and validation
- [ ] Build website crawler with robots.txt support
- [ ] Parse sitemap.xml for file discovery
- [ ] Implement BFS/DFS crawling strategy
- [ ] Identify scrapable file types (PDF, Word, Excel, PowerPoint, HTML, text)
- [ ] Extract file metadata (name, URL, size, last modified)
- [ ] Implement rate limiting and adaptive delay
- [ ] Handle authentication (basic auth, session cookies)
- [ ] Create file list UI with categorization by type
- [ ] Implement file preview (text, PDF, Word, HTML)
- [ ] Add bulk selection controls (Select All, by Type, by Date Range)
- [ ] Implement search and filter for discovered files
- [ ] Connect website input to crawler and file list

## Phase 2: Automatic Ingestion & Processing
- [ ] Implement automatic ingestion trigger on user confirmation
- [ ] Create ingestion queue system with progress tracking
- [ ] Implement file download from URLs
- [ ] Handle download errors and retries with exponential backoff
- [ ] Integrate Docling for standard document parsing
- [ ] Integrate MinerU for complex document layouts
- [ ] Create unified parsing interface with fallback
- [ ] Set up Neo4j for v3.0 schema (Website, DiscoveredFile, ScrapeSession, IngestionJob, Document)
- [ ] Add provenance tracking: website URL, file URL, download date, extraction date

## Phase 3: Semantic Extraction & Knowledge Graph
- [ ] Design semantic triplet schema
- [ ] Implement entity recognition for 8 humanitarian domains
- [ ] Implement relationship extraction
- [ ] Add extraction confidence scoring
- [ ] Store triplets in Neo4j with provenance
- [ ] Create knowledge graph validation

## Phase 4: Knowledge Reconciliation
- [ ] Implement delta detection engine
- [ ] Build trust routing system (consider website domain reputation)
- [ ] Create validation card workflow
- [ ] Implement curation interface (MVP)
- [ ] Add verification state transitions

## Phase 5: Knowledge Cards
- [ ] Define templates for KC-1 to KC-6
- [ ] Implement card generation from graph data
- [ ] Add card approval and expiry workflows
- [ ] Build card management interface

## Phase 6: Agentic Proposal Drafting & Deployment
- [ ] Implement agentic proposal drafting
- [ ] Deploy three knowledge surfaces
- [ ] Deploy API layer with authentication
- [ ] Set up staging environment

## Phase 7: Advanced Features & Production
- [ ] Implement website scraping scheduling
- [ ] Implement incremental updates (only process new/changed files)
- [ ] Deploy watchers and notifications
- [ ] Implement community trust scoring
- [ ] Full production deployment
