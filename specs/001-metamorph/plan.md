# Metamorph Implementation Plan (v3.0 - Website-First)

**Spec ID:** 001-metamorph  
**Version:** 3.0  
**Status:** Draft  
**Date:** 2026-05-12

---

## Overview

This implementation plan outlines the phased approach to building Metamorph v3.0, a **website-to-knowledge intelligence system**. The plan follows a Test-Driven Development (TDD) approach as specified in NFR-006.

**Key Change in v3.0:** The workflow now starts with **website URL input** rather than manual document upload. The system automatically explores the website, discovers all scrapable files, presents them to the user for selection, and automatically starts ingestion upon confirmation.

---

## Phase 1: Website Crawling & File Discovery (Weeks 1-3)

### Objectives
- Build website crawler that automatically discovers all files on user-specified websites
- Create file discovery and presentation UI
- Implement user selection workflow
- Validate crawling accuracy and completeness

### Deliverables

#### 1.1 Website Crawler Backend (FR-001)
- [ ] Implement URL validation and normalization
- [ ] Build website crawler with respect for robots.txt (NFR-009)
- [ ] Parse sitemap.xml for structured file discovery (FR-001b)
- [ ] Follow internal links within the same domain (FR-001c)
- [ ] Identify scrapable file types: PDF, Word, Excel, PowerPoint, HTML, text (FR-001a)
- [ ] Extract file metadata: name, URL, size, last modified date
- [ ] Implement rate limiting to avoid overwhelming servers (NFR-010)
- [ ] Handle basic authentication (FR-001e)
- [ ] Create Website entity model
- [ ] Create DiscoveredFile entity model
- [ ] Create ScrapeSession entity model

#### 1.2 File Discovery Frontend (FR-002)
- [ ] Design website input interface
- [ ] Display crawling progress indicator
- [ ] Build file list display with metadata (FR-002a)
- [ ] Group files by type (PDFs, Documents, Spreadsheets, Presentations, Web Pages) (FR-002b)
- [ ] Implement file preview functionality (FR-002c)
- [ ] Add "Select All" checkbox (FR-002d)
- [ ] Add "Select by Type" filters (FR-002d)
- [ ] Add "Select by Date Range" filters (FR-002d)
- [ ] Implement search/filter functionality
- [ ] Display selected count (e.g., "12 of 45 files selected")
- [ ] Add selection confirmation dialog

#### 1.3 User Workflow Integration
- [ ] Connect website input to crawler
- [ ] Connect file list to selection UI
- [ ] Implement selection state management
- [ ] Add confirmation workflow
- [ ] Store user preferences for scraping settings

### Success Criteria
- [ ] Crawl typical humanitarian website (100-500 pages) in <5 minutes
- [ ] Discover 95%+ of scrapable files on test websites
- [ ] File list loads in <2 seconds for 500 files
- [ ] Preview generates in <2 seconds per file
- [ ] All Phase 1 unit tests passing
- [ ] User can successfully select and confirm files for ingestion

### Testing (TDD - NFR-006)
- [ ] Write unit tests for URL validation
- [ ] Write unit tests for robots.txt parsing
- [ ] Write unit tests for sitemap.xml parsing
- [ ] Write unit tests for link following
- [ ] Write unit tests for file type detection
- [ ] Write unit tests for metadata extraction
- [ ] Write integration tests for crawler end-to-end
- [ ] Create test websites for validation

---

## Phase 2: Automatic Ingestion & Processing (Weeks 4-6)

### Objectives
- Implement automatic ingestion trigger when user confirms file selection
- Build ingestion pipeline for processing selected files
- Integrate Docling and MinerU for document parsing
- Store extracted knowledge in graph database

### Deliverables

#### 2.1 Automatic Ingestion Trigger (FR-003)
- [ ] Implement ingestion queue system
- [ ] Queue selected files for processing in order (FR-003a)
- [ ] Track ingestion progress per file (FR-003b)
- [ ] Display real-time progress indicators
- [ ] Implement error handling and retry logic (FR-003c)
- [ ] Notify user of completion or errors
- [ ] Create IngestionJob entity model
- [ ] Maintain ingestion history and logs

#### 2.2 Document Download & Processing
- [ ] Download files from URLs
- [ ] Store downloaded files temporarily
- [ ] Handle download errors (404, timeout, etc.)
- [ ] Implement retry with exponential backoff
- [ ] Create Document entity model
- [ ] Track download metadata (timestamp, duration, success/fail)

#### 2.3 Document Parsing Integration (FR-004)
- [ ] Integrate Docling for standard document formats (PDF, Word, HTML)
- [ ] Integrate MinerU for complex document layouts
- [ ] Create unified parsing interface
- [ ] Handle error cases and fallback mechanisms
- [ ] Store parsing results with provenance
- [ ] Track parsing tool used, success/failure, timestamps

#### 2.4 Graph Storage Foundation
- [ ] Set up Neo4j database with schema for v3.0
- [ ] Create indexes for Website, DiscoveredFile, Document, ScrapeSession, IngestionJob
- [ ] Implement CRUD operations for new entities
- [ ] Add provenance tracking: website URL, file URL, download date, extraction date
- [ ] Implement relationship creation between entities

### Success Criteria
- [ ] Ingestion starts within <5 seconds of user confirmation
- [ ] Process 10 files simultaneously without errors
- [ ] Average parsing time <10 seconds per document
- [ ] Graph storage operations complete in <100ms
- [ ] All Phase 2 unit tests passing
- [ ] End-to-end: URL → Discovered Files → Selected Files → Ingested Knowledge

### Testing (TDD)
- [ ] Write unit tests for file queuing
- [ ] Write unit tests for download functionality
- [ ] Write unit tests for progress tracking
- [ ] Write unit tests for error handling
- [ ] Write unit tests for Docling integration
- [ ] Write unit tests for MinerU integration
- [ ] Write unit tests for graph storage operations
- [ ] Write integration tests for ingestion pipeline

---

## Phase 3: Semantic Extraction & Knowledge Graph (Weeks 7-9)

### Objectives
- Extract semantic triplets from ingested documents
- Map knowledge to eight humanitarian domains
- Build initial knowledge graph
- Validate extraction quality

### Deliverables

#### 3.1 Semantic Triplet Extraction (FR-005)
- [ ] Design triplet schema: Subject, Predicate, Object, Qualifiers
- [ ] Implement entity recognition for 8 domains (FR-006)
  - Geographic
  - Crisis
  - Demographics
  - Programming
  - Policy
  - Finance
  - Human Resources
  - Knowledge Assets
- [ ] Implement relationship extraction
- [ ] Implement metadata extraction
- [ ] Add extraction confidence scoring
- [ ] Validate triplet quality and completeness

#### 3.2 Knowledge Graph Construction
- [ ] Store triplets in Neo4j with appropriate labels
- [ ] Create relationships between entities
- [ ] Add properties to nodes and edges
- [ ] Implement graph validation
- [ ] Create graph query interface

#### 3.3 Provenance Tracking (FR-010)
- [ ] Track every triplet to source website
- [ ] Track every triplet to source file
- [ ] Track extraction date and tool used
- [ ] Track confidence scores
- [ ] Implement provenance query API

### Success Criteria
- [ ] Extract triplets with >90% completeness from sample documents
- [ ] Graph queries return results in <200ms
- [ ] All provenance information accessible and accurate
- [ ] All Phase 3 unit tests passing

### Testing (TDD)
- [ ] Write unit tests for triplet extraction
- [ ] Write unit tests for entity recognition
- [ ] Write unit tests for relationship extraction
- [ ] Write unit tests for graph construction
- [ ] Write integration tests for end-to-end extraction
- [ ] Validate with 100+ sample humanitarian documents

---

## Phase 4: Knowledge Reconciliation (Weeks 10-12)

### Objectives
- Detect changes and contradictions in knowledge
- Implement delta alerting system
- Build reconciliation workflow
- Create curation interface foundation

### Deliverables

#### 4.1 Delta Detection Engine (FR-007)
- [ ] Implement change detection algorithm
- [ ] Detect contradictions across quantitative values
- [ ] Detect contradictions across normative statements
- [ ] Detect contradictions across classifications
- [ ] Support temporal mismatch detection
- [ ] Add severity scoring for conflicts

#### 4.2 Trust Routing System (FR-014)
- [ ] Implement auto-accept logic for high-confidence updates
- [ ] Implement pending queue for moderate-confidence updates
- [ ] Implement escalation logic for low-confidence or sensitive updates
- [ ] Route based on confidence, sensitivity, source reliability, contradiction level
- [ ] Consider website domain reputation in routing

#### 4.3 Validation Card Workflow (FR-015)
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

#### 4.4 Curation Interface (MVP) (FR-016)
- [ ] Design curator dashboard layout
- [ ] Implement validation card queue display
- [ ] Add card filtering by type, severity, age
- [ ] Add card sorting options
- [ ] Implement curator actions on cards
- [ ] Track verification state transitions

### Success Criteria
- [ ] Detect changes with >95% accuracy
- [ ] Route 100% of incoming claims appropriately
- [ ] Process validation cards in <5 minutes average
- [ ] All Phase 4 unit and integration tests passing

### Testing (TDD)
- [ ] Write unit tests for delta detection
- [ ] Write unit tests for trust routing
- [ ] Write integration tests for validation card workflow
- [ ] Validate with conflicting data scenarios
- [ ] Test all verification state transitions

---

## Phase 5: Knowledge Cards (Weeks 13-15)

### Objectives
- Define and implement all six Knowledge Card types
- Create card generation, approval, and expiry workflows
- Build card management interface

### Deliverables

#### 5.1 Knowledge Card Templates (FR-008)
- [ ] Design KC-1: Donor Intelligence template (Validity: 12 months)
  - Understand funder priorities and requirements
- [ ] Design KC-2: Field Context template (Validity: 6 months)
  - Describe situation, needs, risks
- [ ] Design KC-3: Outcome Evidence template (Validity: 12 months)
  - Summarize effective interventions and costs
- [ ] Design KC-4: Partner Capacity template (Validity: 6 months)
  - Assess partner ability to deliver
- [ ] Design KC-5: Institutional Track Record template (Validity: 24 months)
  - Highlight UNHCR credibility and past performance
- [ ] Design KC-6: Crisis Political Economy template (Validity: 6 months)
  - Explain why a crisis is strategic at this time

#### 5.2 Card Workflow Engine (FR-009)
- [ ] Implement Draft → Approved → Expired → Draft lifecycle
- [ ] Enforce validity periods per card type
- [ ] Prevent use of expired cards in proposals
- [ ] Support card versioning and rollback

#### 5.3 Card Generation
- [ ] Implement automated card generation from graph data
- [ ] Add card quality validation
- [ ] Add card provenance tracking (including source website)
- [ ] Implement card preview
- [ ] Implement card publishing

#### 5.4 Card Management Interface
- [ ] Card library/browser
- [ ] Card search and filtering
- [ ] Card approval workflow
- [ ] Card expiry alerts

### Success Criteria
- [ ] Generate all six card types automatically
- [ ] Approve/reject cards in <10 minutes average
- [ ] Maintain 100% traceability to source documents and websites
- [ ] All Phase 5 unit and integration tests passing

### Testing (TDD)
- [ ] Write unit tests for card generation
- [ ] Write unit tests for card workflow
- [ ] Write integration tests for card-proposal integration
- [ ] Validate with all six card types
- [ ] Test card expiry enforcement

---

## Phase 6: Agentic Proposal Drafting & Deployment (Weeks 16-18)

### Objectives
- Implement agentic proposal drafting
- Deploy system to staging
- Establish monitoring and maintenance

### Deliverables

#### 6.1 Agentic Drafting System (FR-011)
- [ ] Design proposal generation workflow
- [ ] Implement card assembly for proposals
- [ ] Add intervention scoring algorithm
- [ ] Implement draft proposal generation
- [ ] Add proposal review interface
- [ ] Implement proposal iteration

#### 6.2 Three Knowledge Surfaces (FR-013)
- [ ] **Curated Wiki Surface:** Reader-facing accepted knowledge
- [ ] **Discussion & Review Surface:** Contested knowledge evaluation
- [ ] **Revision & Audit Surface:** Immutable change history

#### 6.3 API Layer (FR-012)
- [ ] Implement REST API endpoints
- [ ] Add authentication and authorization
- [ ] Add rate limiting
- [ ] Add API documentation (Swagger/OpenAPI)
- [ ] Implement all API endpoints from spec section 10

#### 6.4 Deployment
- [ ] Set up staging environment
- [ ] Implement CI/CD pipeline
- [ ] Configure monitoring and alerting
- [ ] Set up logging
- [ ] Configure backups
- [ ] Implement disaster recovery plan

### Success Criteria
- [ ] Draft first proposal using agentic system
- [ ] Deploy to staging with <1 hour downtime
- [ ] All acceptance tests passing
- [ ] System handles 100+ concurrent users in staging

### Testing (TDD)
- [ ] Write acceptance tests for proposal drafting
- [ ] Write acceptance tests for traceability (FR-010)
- [ ] Write acceptance tests for curation workflows
- [ ] Write regression tests
- [ ] Performance testing
- [ ] Security testing

---

## Phase 7: Advanced Features & Production (Weeks 19-20)

### Objectives
- Full production deployment
- Deploy advanced features (scheduling, watchers, notifications)
- Continuous improvement

### Deliverables

#### 7.1 Website Scraping Scheduling (FR-027)
- [ ] Allow users to schedule regular re-scraping (daily, weekly, monthly)
- [ ] Implement incremental updates: only process new or changed files (FR-028)
- [ ] Notify user of new files found on re-scrape
- [ ] Allow user to review new files before ingestion
- [ ] Track scraping history per website

#### 7.2 Watchers and Notifications (FR-023)
- [ ] Implement watcher system for websites
- [ ] Implement watcher system for topics, entities, blocks, claims
- [ ] Add notification triggers for all watchable events
- [ ] Configure notification preferences
- [ ] Add notification delivery (email, in-app)

#### 7.3 Community Trust (FR-024)
- [ ] Implement trusted user tracking
- [ ] Add view tracking for blocks
- [ ] Implement trust scoring algorithm
- [ ] Add trust score display

#### 7.4 Production Deployment
- [ ] Deploy to production environment
- [ ] Migrate data from staging
- [ ] Configure production monitoring
- [ ] Set up production backups
- [ ] Implement production support processes

### Success Criteria
- [ ] Production deployment with zero downtime
- [ ] All features working in production
- [ ] System handles production load (1000+ websites, 100K+ documents)
- [ ] All production acceptance tests passing

---

## Milestone Summary

| Milestone | Phase | Duration | Key Deliverable | Status |
|-----------|-------|----------|-----------------|--------|
| M1 | Phase 1 Complete | Week 3 | Website crawler & file discovery | Pending |
| M2 | Phase 2 Complete | Week 6 | Automatic ingestion pipeline | Pending |
| M3 | Phase 3 Complete | Week 9 | Semantic extraction & knowledge graph | Pending |
| M4 | Phase 4 Complete | Week 12 | Knowledge reconciliation | Pending |
| M5 | Phase 5 Complete | Week 15 | Knowledge cards system | Pending |
| M6 | Phase 6 Complete | Week 18 | Agentic proposal drafting & staging | Pending |
| M7 | Phase 7 Complete | Week 20 | Production deployment with advanced features | Pending |

---

## Resource Requirements

### Human Resources
- 1 Technical Lead (Full-time)
- 2 Backend Developers (Full-time)
- 1 Frontend Developer (Full-time)
- 1 QA Engineer (Part-time)
- 1-2 Domain Experts (UN/Humanitarian) (Part-time)
- 1 DevOps Engineer (Part-time for deployment phases)

### Technology Stack
- **Website Crawling:** Python (requests, BeautifulSoup, Scrapy), or Node.js (Puppeteer, Playwright)
- **Document Parsing:** Docling, MinerU
- **Graph Storage:** Neo4j
- **API:** FastAPI
- **Frontend:** React with TypeScript
- **Agentic System:** Mistral Vibe CLI, Claude Code, etc.
- **Testing:** pytest, custom test harness
- **Infrastructure:** Docker, Kubernetes (optional), Nginx
- **Database:** Neo4j, PostgreSQL (for metadata)
- **Caching:** Redis

---

## Risk Management

### Technical Risks
| Risk | Mitigation |
|------|------------|
| Website blocking crawlers | Respect robots.txt, implement rate limiting, use delays between requests |
| Complex website structures | Support sitemap.xml, implement smart crawling strategies |
| Large file downloads | Implement size limits, chunked downloads, timeout handling |
| Document parsing accuracy | Use multiple parsers (Docling + MinerU), implement validation, allow manual override |
| Graph query performance | Optimize indexes, implement caching, use query batching |
| Data consistency | Implement transactions, add validation, use database constraints |

### Operational Risks
| Risk | Mitigation |
|------|------------|
| User adoption | Involve curators early, provide training, create demo videos |
| Data quality | Implement comprehensive validation, trust routing, curator review workflows |
| Security vulnerabilities | Regular security audits, penetration testing, respect robots.txt |
| Compliance issues | Work with UN legal/compliance teams, implement audit trails |
| Website rate limiting | Implement exponential backoff, respect rate limits, cache results |

### Legal/Compliance Risks
| Risk | Mitigation |
|------|------------|
| Copyright infringement | Respect robots.txt, honor copyright headers, allow opt-out |
| Data privacy violations | Anonymize personal data, comply with GDPR, implement access controls |
| Terms of service violations | Review website terms, respect all restrictions, provide compliance checks |

---

## Quality Assurance

### Testing Approach (NFR-006 - TDD)
- **Unit Tests:** All functions and components (write before implementation)
- **Integration Tests:** Component interactions
- **Acceptance Tests:** User workflows and requirements
- **Regression Tests:** Prevent regressions during evolution
- **Performance Tests:** Ensure system meets performance targets
- **Security Tests:** Identify and fix vulnerabilities
- **Scraping Tests:** Verify crawling, discovery, selection, ingestion workflows

### Quality Gates
- All unit tests must pass before merging
- All integration tests must pass before staging deployment
- All acceptance tests must pass before production deployment
- Code review required for all changes
- Security review for sensitive changes
- Performance benchmarks must be met

---

## Monitoring & Maintenance

### Monitoring
- System health metrics (uptime, response times)
- Crawling metrics (pages crawled, files discovered, errors)
- Ingestion metrics (files processed, success rate, errors)
- Performance metrics (query times, extraction times)
- User activity metrics (logins, actions, time spent)
- Data quality metrics (confidence scores, validation rates)

### Maintenance
- Regular backups of databases and configurations
- Security patch management
- Performance optimization
- User feedback collection
- Continuous improvement based on usage analytics
- Website crawler maintenance (update for new file types, handle new anti-scraping techniques)

---

## Workflow Summary (v3.0)

```
┌─────────────────────────────────────────────────────────────────┐
│                    METAMORPH v3.0 WORKFLOW                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. WEBSITE DEFINITION                                           │
│     User enters URL ─────────────────────────────────────────────┤
│                                                                   │
│  2. AUTOMATIC EXPLORATION (Phase 1)                               │
│     System crawls website ──────► Discovers all files             │
│     - Respects robots.txt                                         │
│     - Parses sitemap.xml                                          │
│     - Follows internal links                                      │
│     - Identifies scrapable types                                  │
│                                                                   │
│  3. FILE SELECTION (Phase 1)                                     │
│     User reviews files ────────► Selects files to ingest          │
│     - View file list with metadata                               │
│     - Preview file content                                        │
│     - Select all, by type, by date range                          │
│     - Confirm selection                                           │
│                                                                   │
│  4. AUTOMATIC INGESTION (Phase 2)                                │
│     User confirms ──────────────► Ingestion starts automatically   │
│     - Files queued for processing                                 │
│     - Download from URLs                                          │
│     - Parse with Docling/MinerU                                  │
│     - Store in knowledge graph with provenance                     │
│                                                                   │
│  5. KNOWLEDGE PROCESSING (Phases 3-4)                            │
│     Extracted knowledge ─────────► Reconciliation & curation     │
│     - Delta detection                                             │
│     - Contradiction detection                                    │
│     - Trust routing                                              │
│     - Validation cards                                            │
│                                                                   │
│  6. KNOWLEDGE CARDS (Phase 5)                                     │
│     Processed knowledge ────────► Knowledge cards generated       │
│     - 6 card types (KC-1 to KC-6)                                 │
│     - Approval workflows                                         │
│     - Expiry management                                           │
│                                                                   │
│  7. PROPOSAL DRAFTING (Phase 6)                                  │
│     Knowledge cards ─────────────► Agentic proposal drafting      │
│     - Card assembly                                               │
│     - Intervention scoring                                        │
│     - Draft generation                                            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Next Steps

1. **Start with Phase 1** - Website crawling and file discovery are the foundation
2. **Follow TDD approach** - Write tests before implementation (NFR-006)
3. **Focus on the new workflow** - Prioritize FR-001, FR-002, FR-003 for website-first approach
4. **Validate frequently** - Test with real humanitarian websites early
5. **Involve curators early** - Get feedback on file selection and ingestion workflows
6. **Iterate on UI** - Refine file discovery and selection interface based on user feedback

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2026-05-12 | 3.0 | Major revision for website-first workflow. Reorganized phases to prioritize website crawling (Phase 1) and automatic ingestion (Phase 2). Added new deliverables for website crawler, file selector, and automatic ingestion trigger. Updated milestone summary to reflect new approach. |
| 2026-04-12 | 1.0 | Initial implementation plan |
