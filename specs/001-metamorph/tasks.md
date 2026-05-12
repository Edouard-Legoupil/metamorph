# Metamorph Task List (v3.0 - Website-First)

**Spec ID:** 001-metamorph  
**Version:** 3.0  
**Status:** Draft  
**Date:** 2026-05-12

---

## Task Tracking

This document tracks all implementation tasks for Metamorph v3.0. **Key Change:** The workflow now starts with website URL input, automatic exploration, file selection, and automatic ingestion.

---

## 🌐 Phase 1: Website Crawling & File Discovery

### High Priority (Website Scraper Role - US-SCR-001 to US-SCR-005)

#### FR-001: Website Crawling & Discovery
- [ ] **FR-001** Implement URL input validation
  - [ ] Validate URL format (http/https)
  - [ ] Check URL accessibility
  - [ ] Extract domain information
  - [ ] Display website metadata (title, description)

- [ ] **FR-001d + NFR-009** Implement robots.txt parser
  - [ ] Download and parse robots.txt
  - [ ] Check if crawling is allowed
  - [ ] Extract crawl-delay if specified
  - [ ] Respect disallow directives

- [ ] **FR-001b** Implement sitemap.xml parser
  - [ ] Discover sitemap.xml location
  - [ ] Parse XML sitemap format
  - [ ] Extract file URLs from sitemap
  - [ ] Handle sitemap index files
  - [ ] Respect lastmod and changefreq

- [ ] **FR-001c** Implement website crawler
  - [ ] Follow internal links within same domain
  - [ ] Implement BFS/DFS crawling strategy
  - [ ] Track visited URLs to avoid duplicates
  - [ ] Respect same-origin policy
  - [ ] Handle relative/absolute URLs

- [ ] **FR-001a** Implement file type detection
  - [ ] Detect PDF files (.pdf)
  - [ ] Detect Word documents (.doc, .docx)
  - [ ] Detect Excel files (.xls, .xlsx)
  - [ ] Detect PowerPoint files (.ppt, .pptx)
  - [ ] Detect HTML pages (.html, .htm)
  - [ ] Detect text files (.txt, .csv, .json)
  - [ ] Detect other scrapable formats

- [ ] **FR-001** Implement metadata extraction
  - [ ] Extract file name from URL
  - [ ] Get file size (via HEAD request)
  - [ ] Get last modified date
  - [ ] Extract content-type header
  - [ ] Calculate content hash for deduplication

- [ ] **NFR-010** Implement rate limiting
  - [ ] Configurable delay between requests
  - [ ] Respect crawl-delay from robots.txt
  - [ ] Implement exponential backoff on errors
  - [ ] Track request rate per domain

- [ ] **FR-001e** Implement authentication handling
  - [ ] Support basic authentication
  - [ ] Support session cookies
  - [ ] Store credentials securely
  - [ ] Handle 401/403 responses

- [ ] **Data Model** Create website crawling entities
  - [ ] Implement Website entity (FR-001)
  - [ ] Implement DiscoveredFile entity (FR-001)
  - [ ] Implement ScrapeSession entity (FR-001)
  - [ ] Create database migrations for new entities

- [ ] **API Endpoints** for website scraping
  - [ ] POST /api/v1/websites
  - [ ] GET /api/v1/websites
  - [ ] GET /api/v1/websites/{id}
  - [ ] POST /api/v1/websites/{id}/scrape
  - [ ] GET /api/v1/websites/{id}/scrape-status

#### FR-002: File Discovery & Presentation
- [ ] **FR-002a** Implement file list display
  - [ ] Design scrollable/browsable file list UI
  - [ ] Display filename, URL, type, size, last modified
  - [ ] Implement pagination for large file lists
  - [ ] Add sorting by name, type, date, size

- [ ] **FR-002b** Implement file categorization
  - [ ] Group files by type (PDFs, Documents, Spreadsheets, etc.)
  - [ ] Add category filters
  - [ ] Show count per category
  - [ ] Allow expanding/collapsing categories

- [ ] **FR-002c** Implement file preview
  - [ ] Extract first 500 characters for text files
  - [ ] Extract first page text for PDFs
  - [ ] Display metadata for binary files
  - [ ] Implement preview caching
  - [ ] Add preview loading indicator

- [ ] **FR-002d** Implement bulk selection controls
  - [ ] Add "Select All" checkbox
  - [ ] Add "Select by Type" filters
  - [ ] Add "Select by Date Range" filters
  - [ ] Implement individual file toggle
  - [ ] Display selected count (e.g., "12 of 45")

- [ ] **US-SCR-003** Implement search and filter
  - [ ] Add search bar for file list
  - [ ] Implement real-time search
  - [ ] Add filters for type, date, size
  - [ ] Combine multiple filters

- [ ] **US-SCR-004** Implement preview panel
  - [ ] Design preview modal/panel
  - [ ] Load preview on file click
  - [ ] Handle preview errors gracefully
  - [ ] Close preview on outside click

- [ ] **US-SCR-005** Implement selection confirmation
  - [ ] Design confirmation dialog
  - [ ] Show selection summary
  - [ ] Display estimated processing time
  - [ ] Add cancel option

- [ ] **API Endpoints** for file discovery
  - [ ] GET /api/v1/websites/{id}/files
  - [ ] GET /api/v1/files/{id}
  - [ ] GET /api/v1/files/{id}/preview
  - [ ] POST /api/v1/websites/{id}/files/select
  - [ ] POST /api/v1/websites/{id}/files/deselect

#### User Workflow Integration
- [ ] Connect website input to crawler trigger
- [ ] Connect crawler results to file list display
- [ ] Implement crawling progress indicator
- [ ] Connect file list to selection UI
- [ ] Implement selection state management
- [ ] Add error handling for crawling failures
- [ ] Display user-friendly error messages

### Medium Priority (Phase 1)
- [ ] Implement crawler configuration options
- [ ] Add max depth setting
- [ ] Add max pages limit
- [ ] Add excluded paths configuration
- [ ] Implement crawler pause/resume
- [ ] Add crawler speed controls
- [ ] Implement crawler statistics (pages crawled, files found)
- [ ] Add export file list (CSV, JSON)
- [ ] Implement bookmark/favorite websites
- [ ] Add recent websites history

### Testing (TDD - NFR-006)
- [ ] Write unit tests for URL validation
- [ ] Write unit tests for robots.txt parsing
- [ ] Write unit tests for sitemap.xml parsing
- [ ] Write unit tests for link following
- [ ] Write unit tests for file type detection
- [ ] Write unit tests for metadata extraction
- [ ] Write unit tests for rate limiting
- [ ] Write integration tests for crawler end-to-end
- [ ] Create test websites for validation

---

## 🔄 Phase 2: Automatic Ingestion & Processing

### High Priority (Automatic Ingestion Trigger - FR-003)

#### FR-003: Automatic Ingestion Trigger
- [ ] **FR-003a** Implement ingestion queue
  - [ ] Create queue data structure
  - [ ] Add files to queue in order
  - [ ] Implement queue priority (user-selected order)
  - [ ] Support queue persistence

- [ ] **FR-003b** Implement progress tracking
  - [ ] Track status per file (queued, downloading, parsing, complete, error)
  - [ ] Calculate overall progress percentage
  - [ ] Estimate time remaining
  - [ ] Display per-file progress

- [ ] **FR-003c** Implement error handling and retries
  - [ ] Catch and log all ingestion errors
  - [ ] Implement automatic retry (3 attempts)
  - [ ] Implement exponential backoff between retries
  - [ ] Notify user of permanent failures
  - [ ] Allow user to retry failed files

- [ ] **FR-003** Implement automatic trigger
  - [ ] Start ingestion on user confirmation
  - [ ] Validate selection before starting
  - [ ] Queue all selected files
  - [ ] Begin processing immediately
  - [ ] Return confirmation to user

- [ ] **Data Model** Create ingestion entities
  - [ ] Implement IngestionJob entity
  - [ ] Implement Document entity
  - [ ] Create relationships between entities

- [ ] **API Endpoints** for ingestion
  - [ ] POST /api/v1/websites/{id}/ingest
  - [ ] GET /api/v1/ingestion/jobs
  - [ ] GET /api/v1/ingestion/jobs/{id}
  - [ ] GET /api/v1/ingestion/status

#### Document Download & Processing
- [ ] Implement file downloader
  - [ ] Download files from URLs
  - [ ] Handle HTTP errors (404, 500, etc.)
  - [ ] Implement timeout handling
  - [ ] Store downloaded files temporarily
  - [ ] Track download metadata

- [ ] Implement retry with exponential backoff
  - [ ] Configurable retry count
  - [ ] Increasing delay between retries
  - [ ] Max delay cap
  - [ ] Give up after max retries

#### FR-004: Document Parsing Integration
- [ ] Integrate Docling parser
  - [ ] Set up Docling environment
  - [ ] Implement Docling API wrapper
  - [ ] Handle Docling errors
  - [ ] Extract text from PDFs, Word, HTML
  - [ ] Extract metadata (author, title, date)

- [ ] Integrate MinerU parser
  - [ ] Set up MinerU environment
  - [ ] Implement MinerU API wrapper
  - [ ] Handle MinerU errors
  - [ ] Extract text from complex layouts
  - [ ] Extract tables and structure

- [ ] Create unified parsing interface
  - [ ] Abstract parser differences
  - [ ] Implement fallback (Docling → MinerU)
  - [ ] Store which parser was used
  - [ ] Track parsing success/failure
  - [ ] Handle manual override option

- [ ] Store parsing results
  - [ ] Save extracted text
  - [ ] Save extracted metadata
  - [ ] Store parser confidence scores
  - [ ] Add provenance information

#### Graph Storage Foundation
- [ ] Set up Neo4j for v3.0 schema
  - [ ] Create indexes for Website
  - [ ] Create indexes for DiscoveredFile
  - [ ] Create indexes for Document
  - [ ] Create indexes for ScrapeSession
  - [ ] Create indexes for IngestionJob

- [ ] Implement CRUD operations
  - [ ] Create Website nodes
  - [ ] Create DiscoveredFile nodes
  - [ ] Create Document nodes
  - [ ] Create ScrapeSession nodes
  - [ ] Create IngestionJob nodes

- [ ] Implement relationships
  - [ ] Website → DiscoveredFile (DISCOVERED)
  - [ ] DiscoveredFile → Document (INGESTED)
  - [ ] ScrapeSession → Website (SCRAPED)
  - [ ] IngestionJob → DiscoveredFile (PROCESSED)

- [ ] Add provenance tracking
  - [ ] Track website URL for every document
  - [ ] Track file URL for every document
  - [ ] Track download date
  - [ ] Track extraction date
  - [ ] Track parsing tool used

### Success Criteria Tasks
- [ ] Verify ingestion starts within 5 seconds of confirmation
- [ ] Test processing 10 files simultaneously
- [ ] Validate average parsing time <10 seconds
- [ ] Verify graph storage operations <100ms
- [ ] End-to-end test: URL → Files → Selection → Ingestion

### Testing (TDD)
- [ ] Write unit tests for file queuing
- [ ] Write unit tests for download functionality
- [ ] Write unit tests for progress tracking
- [ ] Write unit tests for error handling
- [ ] Write unit tests for retry logic
- [ ] Write unit tests for Docling integration
- [ ] Write unit tests for MinerU integration
- [ ] Write unit tests for graph storage
- [ ] Write integration tests for ingestion pipeline

---

## 📚 Phase 3: Semantic Extraction & Knowledge Graph

### High Priority

#### FR-005: Semantic Triplet Extraction
- [ ] Design triplet schema
  - [ ] Define Subject, Predicate, Object structure
  - [ ] Add Qualifiers support
  - [ ] Define data types for each component
  - [ ] Design storage format

- [ ] **FR-006** Implement entity recognition for 8 domains
  - [ ] Geographic domain entities
  - [ ] Crisis domain entities
  - [ ] Demographics domain entities
  - [ ] Programming domain entities
  - [ ] Policy domain entities
  - [ ] Finance domain entities
  - [ ] Human Resources domain entities
  - [ ] Knowledge Assets domain entities

- [ ] Implement relationship extraction
  - [ ] Extract Subject-Predicate-Object relationships
  - [ ] Identify relationship types
  - [ ] Extract relationship metadata
  - [ ] Handle n-ary relationships

- [ ] Implement metadata extraction
  - [ ] Extract document metadata
  - [ ] Extract entity metadata
  - [ ] Extract relationship metadata
  - [ ] Extract confidence scores

- [ ] Add extraction confidence scoring
  - [ ] Calculate parser confidence
  - [ ] Calculate extraction method confidence
  - [ ] Combine into overall confidence
  - [ ] Store confidence with each triplet

- [ ] Validate triplet quality
  - [ ] Check for completeness
  - [ ] Check for validity
  - [ ] Check for duplicates
  - [ ] Validate against schema

- [ ] Validate triplet completeness (>90% target)

#### Knowledge Graph Construction
- [ ] Store triplets in Neo4j
  - [ ] Create nodes with appropriate labels
  - [ ] Create relationships with types
  - [ ] Add properties to nodes
  - [ ] Add properties to relationships

- [ ] Create relationships between entities
  - [ ] Implement relationship inference
  - [ ] Create explicit relationships
  - [ ] Handle relationship direction
  - [ ] Add relationship metadata

- [ ] Implement graph validation
  - [ ] Validate node constraints
  - [ ] Validate relationship constraints
  - [ ] Check for duplicate nodes
  - [ ] Verify graph integrity

- [ ] Create graph query interface
  - [ ] Implement basic CRUD queries
  - [ ] Implement complex traversal queries
  - [ ] Add query optimization
  - [ ] Implement query caching

#### FR-010: Provenance Tracking
- [ ] Track triplet to source website
- [ ] Track triplet to source file
- [ ] Track extraction date and tool
- [ ] Track confidence scores
- [ ] Implement provenance query API

### Testing (TDD)
- [ ] Write unit tests for triplet schema
- [ ] Write unit tests for entity recognition
- [ ] Write unit tests for relationship extraction
- [ ] Write unit tests for metadata extraction
- [ ] Write unit tests for confidence scoring
- [ ] Write unit tests for graph construction
- [ ] Write unit tests for provenance tracking
- [ ] Write integration tests for end-to-end extraction
- [ ] Validate with 100+ sample documents

---

## 🔄 Phase 4: Knowledge Reconciliation

### High Priority

#### FR-007: Delta Detection Engine
- [ ] Implement change detection algorithm
- [ ] Detect contradictions in quantitative values
- [ ] Detect contradictions in normative statements
- [ ] Detect contradictions in classifications
- [ ] Support temporal mismatch detection
- [ ] Add severity scoring for conflicts

#### FR-014: Trust Routing System
- [ ] Implement auto-accept logic
- [ ] Implement pending queue
- [ ] Implement escalation logic
- [ ] Route based on confidence
- [ ] Route based on sensitivity
- [ ] Route based on source reliability (including website domain)
- [ ] Route based on contradiction level

#### FR-015: Validation Card Workflow
- [ ] Create validation card data model
- [ ] Implement validation card generation
- [ ] Add diff display (current vs. proposed)
- [ ] Add evidence display with website/file provenance
- [ ] Add provenance display
- [ ] Add confidence score display
- [ ] Add sensitivity classification display
- [ ] Implement Approve action
- [ ] Implement Reject action
- [ ] Implement Merge/Edit action
- [ ] Implement Escalate action
- [ ] Implement Open Discussion action
- [ ] Implement Link to Existing Discussion
- [ ] Implement Mark as Duplicate action
- [ ] Implement Mark as No Consensus action

#### FR-016: Curation Interface (MVP)
- [ ] Design curator dashboard layout
- [ ] Implement validation card queue display
- [ ] Add card filtering by type, severity, age
- [ ] Add card sorting options
- [ ] Implement curator actions on cards
- [ ] Track verification state transitions

### Testing (TDD)
- [ ] Write unit tests for delta detection
- [ ] Write unit tests for trust routing
- [ ] Write integration tests for validation card workflow
- [ ] Validate with conflicting data scenarios
- [ ] Test all verification state transitions

---

## 📚 Phase 5: Knowledge Cards

### High Priority

#### FR-008: Knowledge Card Templates
- [ ] Design KC-1: Donor Intelligence template
- [ ] Design KC-2: Field Context template
- [ ] Design KC-3: Outcome Evidence template
- [ ] Design KC-4: Partner Capacity template
- [ ] Design KC-5: Institutional Track Record template
- [ ] Design KC-6: Crisis Political Economy template

#### FR-009: Card Workflow Engine
- [ ] Implement Draft state
- [ ] Implement Approved state
- [ ] Implement Expired state
- [ ] Implement state transitions
- [ ] Enforce validity periods
- [ ] Prevent use of expired cards
- [ ] Implement card versioning
- [ ] Implement card rollback

#### Card Generation
- [ ] Implement automated card generation from graph data
- [ ] Add card quality validation
- [ ] Add card provenance tracking (including source website)
- [ ] Implement card preview
- [ ] Implement card publishing

#### Card Management Interface
- [ ] Card library/browser
- [ ] Card search and filtering
- [ ] Card approval workflow
- [ ] Card expiry alerts

### Testing (TDD)
- [ ] Write unit tests for card templates
- [ ] Write unit tests for card workflow
- [ ] Write unit tests for card generation
- [ ] Write integration tests for card-proposal integration
- [ ] Validate with all six card types
- [ ] Test card expiry enforcement

---

## 🤖 Phase 6: Agentic Proposal Drafting & Deployment

### High Priority

#### FR-011: Agentic Drafting System
- [ ] Design proposal generation workflow
- [ ] Implement card assembly for proposals
- [ ] Add intervention scoring algorithm
- [ ] Implement draft proposal generation
- [ ] Add proposal review interface
- [ ] Implement proposal iteration

#### FR-013: Three Knowledge Surfaces
- [ ] **Curated Wiki Surface**
  - [ ] Design wiki page structure
  - [ ] Implement accepted knowledge display
  - [ ] Add provenance badges (showing website)
  - [ ] Add freshness indicators
  - [ ] Implement verification state badges
  - [ ] Add maintenance tag display
  - [ ] Link to discussion threads

- [ ] **Discussion & Review Surface**
  - [ ] Design discussion interface
  - [ ] Implement discussion thread creation
  - [ ] Add thread linking to topics/entities/blocks/claims
  - [ ] Implement thread status tracking
  - [ ] Add consensus model evaluation

- [ ] **Revision & Audit Surface**
  - [ ] Design immutable revision history display
  - [ ] Implement change diff viewing
  - [ ] Add audit event display
  - [ ] Implement state restoration

#### FR-012: API Layer
- [ ] Implement REST API endpoints
- [ ] Add authentication (JWT/OAuth2)
- [ ] Add authorization (RBAC)
- [ ] Add rate limiting
- [ ] Add API documentation (Swagger/OpenAPI)
- [ ] Implement all endpoints from spec section 10

#### Deployment
- [ ] Set up staging environment
- [ ] Implement CI/CD pipeline
- [ ] Configure monitoring and alerting
- [ ] Set up logging
- [ ] Configure backups
- [ ] Implement disaster recovery plan

### Testing (TDD)
- [ ] Write acceptance tests for proposal drafting
- [ ] Write acceptance tests for traceability (FR-010)
- [ ] Write acceptance tests for curation workflows
- [ ] Write regression tests
- [ ] Performance testing
- [ ] Security testing

---

## 🎯 Phase 7: Advanced Features & Production

### High Priority

#### FR-027: Website Scraping Scheduling
- [ ] Allow users to schedule regular re-scraping
- [ ] Implement daily, weekly, monthly schedules
- [ ] Implement incremental updates (FR-028)
- [ ] Only process new or changed files
- [ ] Detect file changes via last modified date or hash
- [ ] Notify user of new files found
- [ ] Allow user to review new files before ingestion
- [ ] Track scraping history per website

#### FR-023: Watchers and Notifications
- [ ] Implement watcher system for websites
- [ ] Implement watcher system for topics
- [ ] Implement watcher system for entities
- [ ] Implement watcher system for blocks
- [ ] Implement watcher system for claims
- [ ] Implement watcher system for discussions
- [ ] Implement watcher system for review queues
- [ ] Add notification triggers for all watchable events
- [ ] Configure notification preferences
- [ ] Add notification delivery (email, in-app)

#### FR-024: Community Trust
- [ ] Implement trusted user tracking
- [ ] Add view tracking for blocks
- [ ] Implement trust scoring algorithm
- [ ] Add trust score display

#### Production Deployment
- [ ] Deploy to production environment
- [ ] Migrate data from staging
- [ ] Configure production monitoring
- [ ] Set up production backups
- [ ] Implement production support processes

---

## 📊 Non-Functional Requirements Tasks

### High Priority
- [ ] **NFR-001** Human judgment is not optional - Design all workflows to require human approval for critical decisions
- [ ] **NFR-002** Every claim must be traceable - Implement provenance tracking (website URL, file URL, date, curator)
- [ ] **NFR-003** Honesty over presentation - Design UI to surface difficulties, risks, gaps
- [ ] **NFR-004** Expiry is a feature - Implement validity period enforcement
- [ ] **NFR-005** Support multi-model agentic workflows - Avoid model lock-in
- [ ] **NFR-006** Test-driven development - Write tests before implementation
- [ ] **NFR-007** Immutable audit trails - Implement audit logging for all changes
- [ ] **NFR-008** Separation of concerns - Keep curated knowledge separate from contested knowledge
- [ ] **NFR-009** Respectful scraping - Honor robots.txt, rate limits, website terms
- [ ] **NFR-010** Scalable crawling - Handle websites with thousands of pages efficiently

---

## 🎨 UI/UX Tasks

### Website Scraping UI
- [ ] Design website input interface
- [ ] Create crawling progress visualization
- [ ] Design file list layout
- [ ] Create file card component
- [ ] Design file preview modal
- [ ] Create selection controls
- [ ] Design confirmation dialog
- [ ] Create ingestion progress display

### Curation UI
- [ ] Design curator dashboard
- [ ] Design validation card display
- [ ] Create curation action buttons
- [ ] Design curation history view
- [ ] Create maintenance tag display

### Proposal Writer UI
- [ ] Design knowledge card browser
- [ ] Create proposal drafting interface
- [ ] Design card selection workflow
- [ ] Create proposal preview

### Admin UI
- [ ] Design website management interface
- [ ] Create user management interface
- [ ] Design system settings interface
- [ ] Create monitoring dashboard

---

## 🔧 Infrastructure Tasks

### Backend Infrastructure
- [ ] Set up Python environment
- [ ] Configure Neo4j database
- [ ] Set up Redis for caching
- [ ] Configure authentication/authorization
- [ ] Set up logging
- [ ] Configure monitoring
- [ ] Set up backup strategy

### Frontend Infrastructure
- [ ] Set up React environment
- [ ] Configure TypeScript
- [ ] Set up build tools
- [ ] Configure routing
- [ ] Set up state management
- [ ] Configure API client

### DevOps
- [ ] Set up Docker containers
- [ ] Configure Docker Compose
- [ ] Set up development environment
- [ ] Configure CI/CD pipeline
- [ ] Set up staging environment
- [ ] Set up production environment

---

## 📈 Analytics & Reporting Tasks

- [ ] Implement user activity tracking
- [ ] Add system performance metrics
- [ ] Create crawling statistics dashboard
- [ ] Implement ingestion metrics
- [ ] Create data quality reports
- [ ] Add curator productivity reports
- [ ] Create system health dashboard

---

## 🎓 Training & Onboarding Tasks

- [ ] Create website scraper training materials
- [ ] Develop curator training
- [ ] Create proposal writer training
- [ ] Develop administrator training
- [ ] Create user onboarding workflow
- [ ] Implement in-app help system

---

## Summary Statistics

| Phase | Total Tasks | High Priority | Medium Priority | Completed |
|-------|-------------|---------------|-----------------|-----------|
| Phase 1 | ~85 | 65 | 20 | 0 |
| Phase 2 | ~60 | 45 | 15 | 0 |
| Phase 3 | ~40 | 30 | 10 | 0 |
| Phase 4 | ~50 | 40 | 10 | 0 |
| Phase 5 | ~35 | 25 | 10 | 0 |
| Phase 6 | ~45 | 35 | 10 | 0 |
| Phase 7 | ~30 | 20 | 10 | 0 |
| **Total** | **~345** | **~260** | **~85** | **0** |

---

## Next Steps

1. **Start with Phase 1** - Website crawling and file discovery are the foundation of v3.0
2. **Follow TDD approach** - Write tests before implementation (NFR-006)
3. **Focus on new workflow** - Prioritize FR-001, FR-002, FR-003 for website-first approach
4. **Validate frequently** - Test with real humanitarian websites early
5. **Involve users early** - Get feedback on file discovery and selection UI
6. **Iterate on scraping** - Refine crawler based on real-world website structures

---

## Notes

- Tasks marked with **[FR-XXX]** correspond to Functional Requirements from spec.md
- Tasks marked with **[NFR-XXX]** correspond to Non-Functional Requirements from spec.md
- Tasks marked with **[US-XXX]** correspond to User Stories from spec.md
- All tasks should follow the Test-Driven Development approach (NFR-006)
- Refer to spec.md v3.0 for detailed requirements and the new website-first workflow
- Update this file as tasks are completed or new tasks are identified

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2026-05-12 | 3.0 | Major revision for website-first workflow. Reorganized all tasks to prioritize website crawling (Phase 1) and automatic ingestion (Phase 2). Added ~150 new tasks for website scraping, file discovery, and automatic ingestion. Total tasks increased from 188 to ~345. |
| 2026-04-12 | 1.0 | Initial task list with 188 tasks |
