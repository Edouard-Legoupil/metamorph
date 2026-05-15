# Metamorph: Website-to-Knowledge Intelligence System

**Spec ID:** 001-metamorph  
**Version:** 3.0  
**Author:** Edouard Legoupil   
**Date:** 2026-05-12  
**Status:** Draft

---

## 1. Executive Summary

Metamorph is a **website-to-knowledge intelligence system** for UN and international humanitarian organizations. Its goal is to transform websites and their documents into a living, queryable knowledge base, directly supporting the generation of high-quality project proposals.

**Core Objectives:**

- **Automatically explore websites** to discover and identify all scrapable files
- Ingest and extract structured knowledge from discovered documents
- Reconcile and update knowledge, surfacing contradictions and changes
- Provide human-curated knowledge cards as the primary output, ensuring traceability and validity
- Enable agentic systems to draft proposals based on curated, up-to-date knowledge
- Separate trusted knowledge presentation from contested knowledge negotiation

**Core Principle:**
> Metamorph separates the presentation of trusted knowledge from the negotiation of contested knowledge.

This is achieved through three distinct surfaces:
1. **Curated Wiki Surface** - The reader-facing knowledge layer (accepted, sourced, current knowledge)
2. **Discussion & Review Surface** - Where contested or uncertain information is evaluated
3. **Revision & Audit Surface** - Immutable record of all changes

**Agent Orchestration Principle:**
> Metamorph uses CrewAI for intelligent agent coordination and task delegation.

This enables:
- **Multi-Agent Collaboration** - Specialized agents work together on complex tasks
- **Hierarchical Task Delegation** - Agents can delegate subtasks to specialized agents
- **Autonomous Decision Making** - Agents make context-aware decisions
- **Memory and Learning** - Agents retain context across interactions

**New Workflow (v3.0):**
1. **Website Definition:** User provides a URL to scrape
2. **Automatic Exploration:** System crawls the website and identifies all scrapable files (PDFs, Word docs, HTML pages, etc.)
3. **File Selection:** User reviews discovered files and selects which ones to ingest (all or specific subset)
4. **Automatic Ingestion:** Selected files are automatically parsed and ingested into the knowledge graph
5. **Knowledge Processing:** Extracted knowledge goes through reconciliation, curation, and card generation workflows

---

## 1.1 Clarifications

### Session 2026-05-12

- **Q: What are the expected maximum website sizes (pages, files) that Metamorph should handle?**
  **A:** Enterprise scale: Unlimited with horizontal scaling

- **Q: How should crawling and ingestion errors be presented to users in the UI?**
  **A:** Dedicated error panel with detailed logs

- **Q: What are the target response times for website crawling and file ingestion operations?**
  **A:** Asynchronous: No hard limits, background processing only

- **Q: What API versioning strategy should be used for backward compatibility?**
  **A:** URL path versioning (/api/v1/, /api/v2/)

- **Q: Should the system comply with specific accessibility standards?**
  **A:** WCAG 2.1 AA compliance

---

## 2. Requirements

### 2.1 Functional Requirements

**Clarifications (2026-05-12):**
- **Scale & Performance:** Enterprise scale with unlimited horizontal scaling capability
- **Error Handling:** Dedicated error panel with detailed logs for crawling/ingestion errors
- **Performance Targets:** Asynchronous background processing with progress updates
- **API Versioning:** URL path versioning (/api/v1/, /api/v2/) for backward compatibility
- **Accessibility:** WCAG 2.1 AA compliance for all user interfaces

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| **FR-001** | **Website Crawling & Discovery** | **High** | Crawl user-defined websites to discover all accessible pages and files |
| **FR-001a** | Identify scrapable file types | High | Detect PDF, Word, Excel, PowerPoint, HTML, text files |
| **FR-001b** | Extract file URLs from sitemaps | High | Parse sitemap.xml for structured file discovery |
| **FR-001c** | Follow internal links | Medium | Discover files linked from pages within the same domain |
| **FR-001d** | Respect robots.txt | High | Honor website scraping policies and restrictions |
| **FR-001e** | Handle authentication | Medium | Support basic auth, session cookies for protected sites |
| **FR-002** | **File Discovery & Presentation** | **High** | Present discovered files to user for selection |
| **FR-002a** | Display file list with metadata | High | Show filename, URL, type, size, last modified date |
| **FR-002b** | Categorize files by type | Medium | Group by document type for easier selection |
| **FR-002c** | Preview file content | Medium | Extract and display preview text/snippets |
| **FR-002d** | Bulk selection controls | High | Select all, select by type, select by date range |
| **FR-003** | **Automatic Ingestion Trigger** | **High** | Start ingestion pipeline automatically when user confirms selection |
| **FR-003a** | Queue selected files for processing | High | Add files to ingestion queue in order of selection |
| **FR-003b** | Track ingestion progress | High | Show real-time progress for each file being processed |
| **FR-003c** | Handle ingestion errors | High | Retry failed files, log errors, notify user |
| **FR-004** | Ingest and parse documents using Docling and MinerU | High | Support standard and complex document layouts |
| **FR-005** | Extract semantic triplets (Subject → Predicate → Object) | High | Store in a Labeled Property Graph |
| **FR-006** | Map extracted knowledge to eight domains | High | Geographic, crisis, demographics, programming, policy, finance, HR, knowledge assets |
| **FR-007** | Detect and surface changes, contradictions, and confirmations | High | Delta alerting for human curators; include contradiction detection across quantitative values, normative statements, classifications, etc. |
| **FR-008** | Generate six types of Knowledge Cards (KC-1 to KC-6) | High | See section 4 for card details |
| **FR-009** | Enforce validity periods and draft/expiry workflows | High | Cards must be approved and not expired to be used in proposals |
| **FR-010** | Support traceability of every claim to source nodes | High | Provenance, website URL, file URL, date tracking for auditability |
| **FR-011** | Enable agentic proposal drafting | High | Assemble cards, score interventions, generate drafts |
| **FR-012** | Provide API and query interface for downstream use | Medium | Integration with other systems |
| **FR-013** | Maintain three knowledge surfaces | High | Curated Wiki, Discussion/Review, Revision/Audit surfaces must remain distinct |
| **FR-014** | Implement trust routing for incoming claims | High | Route claims based on confidence, sensitivity, source reliability, contradiction level |
| **FR-015** | Support validation cards for review workflows | High | Each conflict or claim presents a validation card with actions |
| **FR-016** | Enable in-wiki curation controls | High | Verify, flag, edit, revert, discuss, resolve, escalate, archive blocks |
| **FR-017** | Maintain verification states | High | accepted, auto_accepted, pending, disputed, under_review, rejected, merged, escalated, stale, superseded, no_consensus |
| **FR-018** | Support discussion threads with consensus model | High | Consensus based on evidence quality, policy compliance, reviewer expertise |
| **FR-019** | Implement conflict detection and queuing | High | Detect contradictions across values, statements, classifications, relationships |
| **FR-020** | Support maintenance tags and banners | Medium | citation_needed, source_review_needed, disputed, stale, etc. |
| **FR-021** | Implement review tiers and escalation | Medium | Tier 1 (Field/Local), Tier 2 (Regional), Tier 3 (HQ/Thematic) |
| **FR-022** | Maintain human retroaction feedback loop | High | Every curation action updates audit, revision, claim store, and graph state |
| **FR-023** | Support watchers and notifications | Medium | Notify users when watched items change |
| **FR-024** | Enable community trust scoring | Medium | Trusted users viewing without flagging increases confidence |
| **FR-025** | Support reverts and rollbacks | High | Revert curated objects to previous accepted revisions |
| **FR-026** | Provide audit and QA dashboards | Medium | Show live/historic decisions, unresolved conflicts, pending discussions |
| **FR-027** | **Website Scraping Scheduling** | **Medium** | Allow users to schedule regular re-scraping of websites |
| **FR-028** | **Incremental Updates** | **Medium** | Only process new or changed files on re-scrape |

### 2.2 Non-Functional Requirements

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| NFR-001 | Human judgment is not optional | High | System assists curators; does not replace judgment |
| NFR-002 | Every claim must be traceable | High | Provenance, website URL, file URL, date, curator |
| NFR-003 | Honesty over presentation | High | Surface difficulties, risks, and gaps |
| NFR-004 | Expiry is a feature | High | Validity periods enforced for all cards |
| NFR-005 | Support multi-model agentic workflows | Medium | Avoid model lock-in, enforce robustness |
| NFR-006 | Test-driven development | High | Tests written before code for maintainability |
| NFR-007 | Immutable audit trails | High | All state transitions must be documented for accountability |
| NFR-008 | Separation of concerns | High | Curated knowledge presentation separate from contested knowledge negotiation |
| NFR-009 | **Respectful Scraping** | **High** | Honor robots.txt, rate limits, and website terms of service |
| NFR-010 | **Scalable Crawling** | **High** | Handle websites with thousands of pages efficiently, with enterprise-scale horizontal scaling capability |
| NFR-011 | **Accessibility Compliance** | **High** | All user interfaces must comply with WCAG 2.1 AA accessibility standards |
| NFR-012 | **Error Presentation** | **High** | Crawling and ingestion errors must be presented in a dedicated error panel with detailed logs |
| NFR-013 | **API Versioning** | **Medium** | Use URL path versioning (/api/v1/, /api/v2/) for backward compatibility |

---

## 3. User Stories

### 3.1 Website Scraper 

- **US-SCR-001:** As a user, I want to define a website URL to scrape so that I can start the knowledge extraction process.
  - **Acceptance Criteria:**
    - System provides a URL input field
    - System validates URL format
    - System checks if website is accessible
    - System displays website metadata (title, description if available)
    - System starts automatic exploration upon confirmation

- **US-SCR-002:** As a user, I want the system to automatically explore the website and identify all scrapable files so that I don't have to manually find documents.
  - **Acceptance Criteria:**
    - System crawls the website starting from the provided URL
    - System follows internal links within the same domain
    - System identifies all scrapable file types (PDF, Word, Excel, PowerPoint, HTML, text)
    - System respects robots.txt directives
    - System parses sitemap.xml if available
    - System completes exploration within reasonable time (<5 minutes for typical sites)

- **US-SCR-003:** As a user, I want to review and select which files to scrape from the discovered list so that I can control what gets ingested.
  - **Acceptance Criteria:**
    - System presents all discovered files in a scrollable/browsable list
    - Each file shows: filename, URL, file type, file size, last modified date
    - Files are grouped by type (PDFs, Documents, Spreadsheets, Presentations, Web Pages)
    - System provides "Select All" checkbox
    - System provides "Select by Type" filters
    - System provides "Select by Date Range" filters
    - System provides search/filter functionality
    - User can toggle individual file selection
    - Selected count is displayed (e.g., "12 of 45 files selected")

- **US-SCR-004:** As a user, I want to preview file content before selection so that I can make informed decisions.
  - **Acceptance Criteria:**
    - Clicking a file shows a preview panel
    - For text-based files: display first 500 characters
    - For PDFs: extract and display first page text
    - For binary files: display file metadata and type icon
    - Preview loads within <2 seconds

- **US-SCR-005:** As a user, I want ingestion to start automatically after I confirm my file selection so that I don't have to manually trigger processing.
  - **Acceptance Criteria:**
    - After clicking "Start Ingestion", system immediately begins processing
    - Progress indicator shows overall completion percentage
    - Individual file progress is visible (queue, processing, complete, error)
    - User receives confirmation when ingestion starts
    - User can navigate away and return later to check progress
    - **Error Handling:** Errors are displayed in a dedicated error panel with detailed logs (NFR-012)
    - Error panel shows: failed file name, error type, timestamp, retry option
    - Users can download full error logs for support purposes

- **US-SCR-006:** As a user, I want to schedule regular re-scraping of websites so that I can keep knowledge up to date.
  - **Acceptance Criteria:**
    - System allows setting a scraping schedule (daily, weekly, monthly)
    - System only processes new or modified files (based on last modified date or hash)
    - System notifies user of new files found on re-scrape
    - System allows user to review new files before ingestion

### 3.2 Curator

- **US-CUR-001:** As a curator, I want to ingest documents from websites and extract structured knowledge so that I can update the knowledge graph.
  - **Acceptance Criteria:**
    - Documents from selected website files are parsed and decomposed into semantic triplets
    - Triplets are stored in the graph with provenance including website URL and file URL
    - Conflicts and changes are flagged for review
    - Conflicts are queued by type (factual accuracy, source reliability, temporal mismatch, etc.)

- **US-CUR-002:** As a curator, I want to review and approve knowledge cards so that they can be used in proposals.
  - **Acceptance Criteria:**
    - Cards are pre-populated by the system from ingested website content
    - Curators can edit, approve, or reject cards
    - Approved cards are marked as valid for a set period
    - Verification state transitions are properly managed

- **US-CUR-003:** As a curator, I want to see validation cards for conflicts so that I can efficiently review and resolve them.
  - **Acceptance Criteria:**
    - Each validation card shows current accepted value vs. incoming/proposed update from website
    - Cards display diff, evidence, provenance (including source website and file), confidence score, sensitivity classification
    - Available actions: Approve, Reject, Merge/Edit, Escalate, Open Discussion, Mark as Duplicate, Mark as No Consensus

- **US-CUR-004:** As a curator, I want in-wiki curation controls so that I can verify, flag, or edit blocks directly.
  - **Acceptance Criteria:**
    - Each wiki block has inline actions: verify, flag, edit, discuss, view_history, view_provenance, resolve_conflict, escalate
    - Each block displays verification badge, freshness indicator, provenance modal (showing source website), conflict banner if disputed
    - Actions trigger backend workflow updates, UI refresh, audit logging, claim store updates, graph updates

- **US-CUR-005:** As a curator, I want to escalate sensitive or high-impact changes to appropriate review tiers.
  - **Acceptance Criteria:**
    - Changes are automatically routed to Tier 1 (Field), Tier 2 (Regional), or Tier 3 (HQ/Thematic) based on sensitivity and scope
    - Each tier has defined review queues, permissions, decision SLAs, and audit policies

### 3.3 Agentic Proposal Writer

- **US-PROP-001:** As a proposal writer, I want to query the knowledge base for relevant cards so that I can draft a proposal.
  - **Acceptance Criteria:**
    - Cards are retrievable by domain, validity, and relevance
    - Cards include source website information in provenance
    - Proposals cannot be generated against expired or unapproved cards
    - Every claim in the proposal is traceable to a source website and file

- **US-PROP-002:** As a proposal writer, I want to see maintenance tags on knowledge so that I can assess confidence and completeness.
  - **Acceptance Criteria:**
    - Tags like citation_needed, stale, disputed, low_confidence are visible on affected blocks
    - Each tag links to relevant discussion threads or conflicts
    - Tags indicate if source website may have newer information

- **US-PROP-003:** As a proposal writer, I want to generate proposal drafts using the knowledge base so that the funding request is supported by evidence.
  - **Acceptance Criteria:**
    - Proposals include sourcing for every claim with website references
    - Difficulties and risks are acknowledged and mitigated
    - Source websites are listed for verification

### 3.4 Knowledge Reviewer

- **US-REV-001:** As a reviewer, I want to participate in discussion threads so that I can help resolve contested knowledge.
  - **Acceptance Criteria:**
    - Can create and comment on discussion threads linked to topics, entities, blocks, claims, or conflicts
    - Can propose patches, cite sources (including website URLs), mention other reviewers
    - Can mark threads as open, under_review, consensus_reached, no_consensus, rejected, escalated, resolved, archived

- **US-REV-002:** As a reviewer, I want to watch topics and receive notifications so that I can stay informed about changes.
  - **Acceptance Criteria:**
    - Can watch topics, entities, blocks, claims, discussions, or review queues
    - Receive notifications when watched items are edited, disputed, or have discussions opened

---

## 4. Knowledge Cards

| ID | Card Type | Purpose | Validity | Scope |
|----|-----------|---------|----------|-------|
| KC-1 | Donor Intelligence | Understand funder priorities and requirements | 12 months | Per donor |
| KC-2 | Field Context | Describe situation, needs, risks | 6 months | Per field context |
| KC-3 | Outcome Evidence | Summarize effective interventions and costs | 12 months | Per outcome |
| KC-4 | Partner Capacity | Assess partner ability to deliver | 6 months | Per partner |
| KC-5 | Institutional Track Record | Highlight UNHCR credibility and past performance | 24 months | Per operation |
| KC-6 | Crisis Political Economy | Explain why a crisis is strategic at this time | 6 months | Per crisis |

**Card Workflow:**
- Draft → Approved → Expired → Draft
- Expired cards cannot be used in proposals

**Card Structure:**
Each card contains sections with blocks that have:
- Unique block_id
- Section name
- Word limit
- Block type
- Template/query for extraction
- Verification status
- Provenance tracking (including source website URL and file URL)
- Linked discussion threads (if disputed)

---

## 5. Technical Constraints and Architecture

### 5.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        METAMORPH SYSTEM (v3.0)                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────┐   │
│  │   Website         │    │   File          │    │     Ingestion Layer       │   │
│  │   Crawler         │    │   Selector      │    │  (Docling, MinerU)        │   │
│  │                   │    │                 │    │                            │   │
│  │  - URL Input     │───▶│  - Auto-explore │───▶│  - Document Parsing       │   │
│  │  - Crawl Site     │    │  - File List    │    │  - Semantic Extraction    │   │
│  │  - Respect       │    │  - Selection UI │    │  - Graph Storage         │   │
│  │    robots.txt    │    │  - Confirm      │    │                            │   │
│  └────────┬────────┘    └────────┬────────┘    └────────────┬──────────────┘   │
│            │                     │                         │                   │
│            └─────────────────────┼─────────────────────────┘                   │
│                                      ↓                                          │
│                    ┌─────────────────────────────────────────────────┐        │
│                    │          Knowledge Reconciliation               │        │
│                    │  - Delta Detection                                 │        │
│                    │  - Contradiction Detection                        │        │
│                    │  - Change Tracking                                 │        │
│                    └──────────────────┬─────────────────────────────┘        │
│                                       ↓                                         │
│              ┌─────────────────────────────────────────────────────────┐   │
│              │                  CURATION LAYERS                          │   │
│              ├─────────────────┬─────────────────┬──────────────────────┤   │
│              │  Curated Wiki    │  Discussion/     │  Revision/            │   │
│              │  Surface         │  Review Surface  │  Audit Surface        │   │
│              │  (Accepted)      │  (Contested)     │  (Immutable)          │   │
│              └────────┬────────┴──────────┬──────┴───────────────────┘   │
│                       │                     │                                  │
│          ┌────────────┴────────┐ ┌─────────┴──────┐                        │
│          ↓                       ↓ ↓                ↓                        │
│  ┌─────────────────┐   ┌─────────────┐  ┌─────────────┐                │
│  │  Knowledge Cards  │   │ Validation   │  │ Conflict     │                │
│  │  (KC-1 to KC-6)  │   │ Cards/Queue  │  │ Queues       │                │
│  └─────────────────┘   └─────────────┘  └─────────────┘                │
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │              AGENTIC PROPOSAL DRAFTING                           │   │
│  │  - Card Assembly     - Intervention Scoring  - Draft Generation   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Core Components

#### 5.2.1 Website Crawler (NEW)
- **Purpose:** Automatically discover all files on a user-specified website
- **Capabilities:**
  - Crawl websites respecting robots.txt
  - Parse sitemap.xml for structured file discovery
  - Follow internal links within the same domain
  - Identify scrapable file types (PDF, DOCX, XLSX, PPTX, HTML, TXT)
  - Extract file metadata (name, URL, size, last modified date)
  - Handle authentication (basic auth, session cookies)
  - Rate limiting to avoid overwhelming servers
  - **Enterprise Scale:** Horizontal scaling capability for unlimited website sizes
  - Distributed crawling with worker pools
  - Automatic load balancing and failover
- **Output:** List of discovered files with metadata

#### 5.2.2 File Selector UI (NEW)
- **Purpose:** Allow users to review and select files for ingestion
- **Capabilities:**
  - Display discovered files in a browsable list
  - Group files by type, date, or size
  - Preview file content (text extraction for first page/section)
  - Bulk selection (select all, select by type, select by date range)
  - Search and filter functionality
  - Selection confirmation with summary
  - **Accessibility:** WCAG 2.1 AA compliant interface with keyboard navigation, screen reader support, and proper contrast ratios
  - Responsive design for various screen sizes
  - Internationalization-ready UI components
- **Output:** List of selected file URLs to ingest

#### 5.2.3 Automatic Ingestion Trigger (NEW)
- **Purpose:** Start ingestion pipeline when user confirms selection
- **Capabilities:**
  - Queue selected files for processing
  - Track ingestion progress per file
  - Handle errors and retries
  - Notify user of completion or issues
  - Maintain ingestion history and logs

#### 5.2.4 Ingestion Layer
- **Purpose:** Parse and extract knowledge from selected files
- **Capabilities:**
  - Download files from URLs
  - Parse using Docling (standard documents) and MinerU (complex layouts)
  - Extract semantic triplets (Subject → Predicate → Object)
  - Store in Neo4j graph database
  - Add provenance tracking (website URL, file URL, download date, extraction date)

#### 5.2.5 Knowledge Reconciliation
- **Purpose:** Detect changes, contradictions, and confirmations
- **Capabilities:**
  - Delta detection for updates to existing knowledge
  - Contradiction detection across multiple dimensions
  - Change tracking and versioning
  - Trust routing based on confidence and sensitivity

#### 5.2.6 Curation Layers (Three Surfaces)
- **Purpose:** Use an agentic system to draft knowledge article based on the ingested knowledge and according to predefined templates - Surface automatically content that requires review and curation.
- **Curated Wiki Surface:** Reader-facing accepted knowledge
- **Discussion & Review Surface:** Contested knowledge evaluation
- **Revision & Audit Surface:** Immutable change history

#### 5.2.7 Knowledge Cards
- Six card types (KC-1 to KC-6) as defined in Section 4
- Automatic generation from graph data
- Approval and expiry workflows



### 5.3 Data Model

#### 5.3.1 Core Entities (Updated for v3.0)

```
Entity Website {
  id
  url  // The root URL provided by user
  domain
  title
  description
  discovered_at
  last_scraped_at
  scrape_frequency  // manual, daily, weekly, monthly
  status  // active, paused, error
  robots_txt_url
  sitemap_url
  total_files_discovered
  total_files_ingested
  last_successful_scrape
}

Entity DiscoveredFile {
  id
  website_id
  url
  file_type  // pdf, docx, xlsx, pptx, html, txt, other
  file_name
  file_size
  last_modified_date
  content_hash  // For detecting changes on re-scrape
  discovered_at
  status  // pending, selected, processing, ingested, error
  error_message  // If status is error
  metadata  // Extracted metadata (author, title, etc.)
}

Entity ScrapeSession {
  id
  website_id
  started_at
  completed_at
  status  // running, completed, failed
  files_discovered
  files_selected
  files_ingested
  files_failed
  error_summary
}

Entity IngestionJob {
  id
  discovered_file_id
  scrape_session_id
  status  // queued, processing, completed, failed
  started_at
  completed_at
  error_message
  document_id  // Reference to parsed document in graph
}

Entity Document {
  id
  ingestion_job_id
  discovered_file_id
  website_id
  original_url
  file_type
  file_name
  file_size
  download_date
  parse_date
  parsing_tool  // docling, mineru, manual
  parse_success
  parse_error
  content_hash
  extracted_text  // Full text if available
  metadata  // Author, title, date, etc.
}
```

Existing entities (from v2.0) remain unchanged:
- Entity Topic
- Entity CuratedPage
- Entity WikiBlock
- Entity DiscussionPage
- Entity DiscussionThread
- Entity DiscussionComment
- Entity Claim
- Entity Conflict
- Entity ValidationCard
- Entity Revision
- Entity MaintenanceTag
- Entity AuditEvent
- Entity RetroactionEvent
- Entity Watcher
- Entity Curator

#### 5.3.2 Knowledge Domains
- Geographic
- Crisis
- Demographics
- Programming
- Policy
- Finance
- Human Resources
- Knowledge Assets

#### 5.3.3 Nodes and Edges (Graph Storage)
- **Nodes:** Documents, Websites, DiscoveredFiles, Entities (people, orgs, locations), Events, Interventions, Outcomes, Knowledge Cards
- **Edges:** Relationships (e.g., "discovered_from", "ingested_from", "funded_by", "affected_by", "implemented_by", "operates_in", "covers")
- **Properties:** Provenance (source website URL, source file URL, download date, extraction date), validity period, curator, status, verification_state

---

## 6. Workflow and Phases

### 6.1 Website Scraping Workflow (NEW - v3.0)

```
┌─────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   User       │     │   Website       │     │   File          │
│   Input      │────▶│   Crawler        │────▶│   Discovery      │
└─────────────┘     └────────┬────────┘     └────────┬────────┘
                              │                        │
                              │                        ↓
                              │              ┌─────────────────┐
                              │              │   File List     │
                              │              │   (with preview) │
                              │              └────────┬────────┘
                              │                       │
                              │         ┌─────────────┼─────────────┐
                              │         │             │             │
                              │         ↓             ↓             ↓
                              │   ┌──────────┐   ┌──────────┐   ┌──────────┐
                              │   │ Select   │   │ Deselect │   │ Modify   │
                              │   │ All      │   │ Some     │   │ Selection│
                              │   └────┬─────┘   └────┬─────┘   └────┬─────┘
                              │        └──────────┬────────────┘
                              │                       │
                              │              ┌────────▼────────┐
                              │              │   User          │
                              │              │   Confirmation   │
                              │              └────────┬────────┘
                              │                       │
                              │     ┌─────────────────▼─────────────────┐
                              │     │                                   │
                              │     │    Automatic Ingestion Trigger      │
                              │     │                                   │
                              │     └─────────────────┬─────────────────┘
                              │                       │
                              │              ┌────────▼────────┐
                              │              │   Ingestion      │
                              │              │   Pipeline       │
                              │              │  (Docling/MinerU)│
                              │              └────────┬────────┘
                              │                       │
                              │              ┌────────▼────────┐
                              │              │   Knowledge      │
                              │              │   Graph          │
                              │              └─────────────────┘
```

### 6.2 Trust Routing

Incoming claims, extracted facts, proposed edits, and graph updates must be routed based on:
- Confidence level
- Sensitivity classification
- Source reliability (including website domain reputation)
- Contradiction level
- Policy rules

**Routing States:**

1. **Auto-Accept:** High-confidence, low-risk updates from trusted sources with no contradictions
   - Non-controversial metadata correction
   - Low-risk stale field refresh
   - Trusted source update (known reliable website)
   - High-confidence duplicate confirmation

2. **Shadow / Pending:** Moderate-confidence updates
   - Stored but not fully accepted
   - May appear with pending badges
   - Visible only to reviewers
   - Enqueued for review

3. **Escalation:** Low-confidence, contradictory, sensitive, high-impact, or policy-relevant updates
   - Require human review
   - Routing determined by sensitivity and scope

**Routing Logic:**
```
if confidence >= auto_accept_threshold 
   and source_reliability == "trusted" 
   and sensitivity == "low" 
   and contradiction_detected == false:
    autoAccept()
    updateCuratedWiki()
    updateCanonicalClaimStore()
    updateGraph()
elif confidence is moderate 
   or source_reliability is uncertain 
   or freshness_requires_confirmation:
    markPending()
    enqueueForReview()
    createValidationCard()
elif confidence is low 
   or contradiction_detected == true 
   or sensitivity in ["legal", "policy", "protection", "security", "high-impact"]:
    escalateToReviewTier()
    createValidationCard()
```

### 6.3 Verification State Transitions

```
                    ┌─────────────────┐
                    │     incoming     │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          ↓                  ↓                  ↓
   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
   │  auto_accepted│   │    pending    │   │  escalated   │
   └──────┬───────┘   └──────┬───────┘   └──────┬───────┘
           │                  │                  │
           └──────────┬───────┴───────┬─────────┘
                      ↓               ↓
               ┌──────────────┐   ┌──────────────┐
               │   accepted    │   │   rejected    │
               └──────┬───────┘   └──────┬───────┘
                      │                  │
           ┌──────────┴──────────┬───────┴──────────┐
           ↓                     ↓                  ↓
    ┌──────────────┐      ┌──────────────┐   ┌──────────────┐
    │  superseded  │      │    merged     │   │no_consensus  │
    └──────────────┘      └──────────────┘   └──────────────┘
```

### 6.4 Curation Workflows

#### 6.4.1 Validation Card Workflow
Each conflict, claim, or proposed edit presents a validation card with:
- Current accepted value
- Incoming or proposed update
- Diff between current and proposed value
- Evidence
- Provenance (including source website URL and file URL)
- Extraction metadata
- Source reliability indicators
- Confidence score
- Sensitivity classification
- Linked wiki block
- Linked discussion thread (if any)
- Linked audit history
- Reviewer tier assignment
- Freshness status
- Contradiction status

**Available Actions:**
- Approve - Accept the proposed change
- Reject - Discard the proposed change
- Merge/Edit - Modify and accept
- Escalate - Send to higher review tier
- Open Discussion - Create discussion thread
- Link to Existing Discussion - Connect to ongoing discussion
- Request Source Review - Flag for source verification
- Mark as Duplicate - Identify as redundant
- Mark as No Consensus - Unable to reach agreement
- Revert to Previous Accepted State - Rollback

#### 6.4.2 In-Wiki Curation
Every wiki block can be:
- Verified
- Flagged
- Edited
- Reverted
- Discussed
- Resolved
- Escalated
- Archived

Each block exposes inline curation controls and displays:
- Verification badge
- Freshness indicator
- Provenance modal (showing source website and file)
- Conflict banner (if disputed)
- Maintenance tags
- Linked discussion threads
- Last accepted revision
- Latest pending proposals

Reviewer actions trigger:
1. Backend workflow update
2. Immediate wiki/card/graph refresh
3. Audit logging
4. Claim store update (if accepted)
5. Graph database update (if accepted)
6. Discussion update (if linked)
7. Notification to watchers or responsible review tier

#### 6.4.3 Discussion Thread Workflow

**Thread Creation:** When information is contested, unclear, sensitive, or requires collective judgment

**Thread Statuses:**
- open
- under_review
- consensus_reached
- no_consensus
- rejected
- escalated
- resolved
- archived

**Consensus Model:** Based on:
- Quality of evidence
- Policy compliance
- Source reliability
- Freshness
- Operational relevance
- Regional applicability
- Reviewer authority and domain expertise
- Absence or presence of unresolved objections
- Sensitivity level
- Strength of reasoning

**Consensus Results:**
- accept
- reject
- merge
- no_consensus
- escalate
- defer_until_more_evidence

### 6.5 Review Tiers and Escalation

**Tier 1 — Field / Local:**
- Operational data
- Local entities
- Local contact points
- Field-level observations
- Low-to-medium impact updates

**Tier 2 — Regional:**
- Regional SOPs
- Regional strategy
- Cross-country conflicts
- Regional operating context
- Regional coordination issues

**Tier 3 — HQ / Thematic:**
- Global policy
- Legal concerns
- Protection-sensitive content
- High-impact decisions
- Global taxonomy
- Authoritative thematic guidance

Each tier has:
- Review queues
- Escalation rules
- Permissions
- Decision SLAs
- Audit policies
- Notification policies
- Consensus requirements

**Assignment Logic:**
```
if sensitivity == "high":
    return "tier_3"
elif scope == "regional":
    return "tier_2"
elif scope == "local":
    return "tier_1"
else:
    return defaultTierByDomain(domain)
```

### 6.6 Human Retroaction Feedback Loop

When any curator, reviewer, analyst, or trusted contributor performs an action, the system records it immediately.

**Actions:**
- Approving
- Editing
- Merging
- Escalating
- Rejecting
- Reverting
- Tagging
- Opening a discussion
- Closing a discussion
- Marking no consensus
- Applying consensus
- Archiving a thread

**Each action creates:**
1. An audit log entry
2. A revision entry (if state changed)
3. An update to the curation table
4. An update to the relevant claim/fact/entity record
5. An update to graph state (if applicable)
6. A UI refresh event
7. A notification event (if watchers or reviewers are subscribed)

**Bidirectional Traceability:**
```
Website → DiscoveredFile → Document → Claim → Source → Discussion → Decision → Audit event → Graph update

Graph node → Accepted claim → Wiki block → Revision → Reviewer action → Discussion
```

### 6.7 Reverts and Rollbacks

Reverts are required when:
- An accepted update is later found incorrect
- A source is invalidated
- An edit was premature
- A policy violation is detected
- An automated acceptance was wrong
- An editor applied the wrong patch
- A conflict was unresolved but content was applied

**Revert Process:**
```
1. Create new revision from previous accepted revision
2. Create audit event with rationale
3. Notify watchers
4. Refresh affected surfaces
5. Automatically open or update discussion thread if change was substantive
```

### 6.8 Watchers and Notifications

Users may watch:
- Topics
- Entities
- Blocks
- Claims
- Discussions
- Review queues
- Websites (NEW - for re-scraping notifications)

**Notification triggers:**
- A watched block is edited
- A claim is disputed
- A discussion is opened
- A consensus decision is applied
- A conflict is escalated
- A source is rejected
- A tag is added or removed
- A watched claim becomes stale
- A website scraping completes with new files
- A scraping error occurs

### 6.9 Community Trust

Community verification increases confidence when trusted users read, use, or verify a block without flagging it.

**Trust Scoring Logic:**
```
if trustedUsersViewedWithoutFlag(block) 
   and noActiveConflict(block) 
   and freshnessWindowValid(block):
    increaseTrustScore(block)
```

**Rule:** Silent reads do NOT override explicit contradictions, high-risk changes, or unresolved disputes.

### 6.10 Knowledge Card Generation

**Phases:**
1. **Website Scraping:** Crawl website and discover files → List of discovered files
2. **File Selection:** User selects files → Queue of files to ingest
3. **Ingestion:** Parse and extract knowledge from documents → Semantic triplets in graph
4. **Reconciliation:** Detect changes, contradictions, confirmations → Delta alerts for curators
5. **Curation:** Review and approve knowledge cards → Validated cards
6. **Proposal Drafting:** Assemble relevant cards, generate draft → Structured proposal

---

## 7. Security and Compliance

- **Data Handling:** All documents and extracted knowledge must comply with UN data policies and GDPR where applicable
- **Access Control:** Curators and proposal writers have role-based access. Tier-based permissions for review actions
- **Audit Trail:** Every change to the graph, cards, claims, discussions, or tags is logged with timestamp, user, and rationale
- **Sensitivity Classification:** Content is classified by sensitivity level (low, medium, high) for appropriate routing and access control
- **Respectful Scraping:** All website scraping must respect robots.txt, rate limits, and website terms of service (NFR-009)
- **Data Provenance:** All extracted knowledge must maintain traceability to source website and file (NFR-002)
- **Accessibility Compliance:** All user interfaces must comply with WCAG 2.1 AA standards (NFR-011)

---

## 8. Testing Strategy

- **Unit Tests:** Validate parsing, extraction, graph storage, trust routing, state transitions, website crawling, file discovery
- **Integration Tests:** Ensure delta alerts, card generation, validation card workflows, scraping pipeline work as expected
- **Acceptance Tests:** Verify proposal drafting, traceability, curation workflows, website-to-knowledge pipeline
- **Regression Tests:** Maintainability across future evolutions
- **Curation-Specific Tests:** Verify verification state transitions, conflict detection, consensus evaluation, revert functionality
- **Scraping Tests:** Verify website crawling, file discovery, selection workflow, automatic ingestion trigger

---

## 9. Deployment Plan

- **Phase 1:** Website crawler and file discovery (Weeks 1-2)
- **Phase 2:** File selector UI and automatic ingestion trigger (Weeks 3-4)
- **Phase 3:** Ingest and extract knowledge from sample websites (Weeks 5-6)
- **Phase 4:** Implement delta detection, contradiction detection, and basic trust routing (Weeks 7-8)
- **Phase 5:** Deploy curation surfaces and validation card workflows (Weeks 9-10)
- **Phase 6:** Implement review tiers, escalation, and maintenance tagging (Weeks 11-12)
- **Phase 7:** Deploy agentic proposal drafting with curated knowledge cards (Weeks 13-14)
- **Phase 8:** Full integration with UN systems and APIs (Weeks 15-16)
- **Phase 9:** Deploy watchers, notifications, community trust, and scheduling (Weeks 17-20)

---

## 10. API Capabilities

### 10.1 Minimum API Endpoints for Curation

**API Versioning Strategy:** All endpoints use URL path versioning (e.g., `/api/v1/`) for backward compatibility. Major version changes will increment the version number.

```http
# Website Scraping (NEW)
POST /api/v1/websites                         # Create website scraping job
GET  /api/v1/websites                        # List all websites
GET  /api/v1/websites/{id}                   # Get website details
POST /api/v1/websites/{id}/scrape            # Trigger scraping
GET  /api/v1/websites/{id}/files             # List discovered files
POST /api/v1/websites/{id}/files/select       # Select files for ingestion
POST /api/v1/websites/{id}/files/deselect     # Deselect files
POST /api/v1/websites/{id}/ingest             # Trigger ingestion of selected files
GET  /api/v1/websites/{id}/scrape-status      # Get scraping status

# Discovered Files (NEW)
GET  /api/v1/files                           # List all discovered files
GET  /api/v1/files/{id}                       # Get file details
GET  /api/v1/files/{id}/preview               # Get file preview
PATCH /api/v1/files/{id}                      # Update file metadata

# Ingestion (NEW)
GET  /api/v1/ingestion/jobs                   # List ingestion jobs
GET  /api/v1/ingestion/jobs/{id}              # Get job details
GET  /api/v1/ingestion/status                 # Get ingestion pipeline status

# Topics and Curated Content
GET /topics/{id}
GET /topics/{id}/curated
GET /topics/{id}/discussion
GET /topics/{id}/history

# Wiki Blocks
POST /topics/{id}/blocks/{block_id}/edit
POST /topics/{id}/blocks/{block_id}/verify
POST /topics/{id}/blocks/{block_id}/flag
POST /topics/{id}/blocks/{block_id}/revert

# Claims
POST /claims/{id}/validate
POST /claims/{id}/reject
POST /claims/{id}/merge
POST /claims/{id}/escalate

# Conflicts
GET /conflicts
GET /conflicts/{id}
POST /conflicts/{id}/review
POST /conflicts/{id}/resolve
POST /conflicts/{id}/dismiss
POST /conflicts/{id}/escalate

# Discussion
POST /discussion/threads
GET /discussion/threads/{id}
POST /discussion/threads/{id}/comments
POST /discussion/threads/{id}/close
POST /discussion/threads/{id}/apply-consensus

# Maintenance Tags
POST /tags
DELETE /tags/{id}

# Audit and Revision
GET /audit/events
GET /revisions/{target_type}/{target_id}

# Validation Cards
GET /validation/cards
GET /validation/cards/{id}
POST /validation/cards/{id}/approve
POST /validation/cards/{id}/reject
POST /validation/cards/{id}/merge
POST /validation/cards/{id}/escalate

# Knowledge Cards
GET /api/v1/enumerate-cards
GET /api/v1/cards/{card_id}
GET /api/v1/blocks/card/{card_id}
```

---

## 11. Coding-Agent Decision Rules

A coding agent implementing Metamorph should use these rules to determine how to handle incoming knowledge.

### 11.1 Add Directly to Curated Wiki When

```
if information_is_factual
and source_is_reliable
and confidence_is_high
and sensitivity_is_low
and no_conflict_detected
and policy_allows_auto_accept:
    updateCuratedWiki()
    updateCanonicalClaimStore()
    updateGraph()
    createRevision()
    createAuditEvent()
```

### 11.2 Route to Review Queue When

```
if confidence_is_moderate
or source_reliability_is_uncertain
or freshness_requires_confirmation
or claim_changes_existing_value:
    createValidationCard()
    enqueueForReview()
    markAsPending()
```

### 11.3 Open Discussion When

```
if information_is_contested
or multiple_valid_sources_disagree
or proposed_change_affects_interpretation
or reviewer_disagreement_exists
or prior_revert_exists
or change_is_substantial:
    createDiscussionThread()
    linkToTarget()
    markTargetAsDisputed()
```

### 11.4 Escalate When

```
if sensitivity_is_high
or policy_risk_exists
or legal_risk_exists
or protection_risk_exists
or cross_regional_impact_exists
or tier_1_or_2_cannot_resolve:
    escalateToHigherTier()
    createAuditEvent()
```

### 11.5 Preserve Current State When No Consensus

```
if discussion_result == "no_consensus":
    keepCurrentAcceptedRevision()
    markIncomingProposalAsNotAccepted()
    recordNoConsensus()
    linkDiscussionToTarget()
    notifyWatchers()
```

---

## 12. Glossary

- **Semantic Triple:** A structured representation of knowledge as Subject → Predicate → Object
- **Knowledge Card:** A structured document summarizing key knowledge for a specific domain (KC-1 to KC-6)
- **Delta Alert:** Notification of changes or contradictions in the knowledge graph
- **Agentic System:** An AI-driven system that automates proposal drafting based on curated knowledge
- **Curated Wiki Surface:** The reader-facing layer displaying accepted, sourced, current knowledge
- **Discussion Surface:** The layer where contested or uncertain information is evaluated (equivalent to Wikipedia's Talk tab)
- **Revision Surface:** The immutable record of all changes, equivalent to Wikipedia's Revision History extended with structured audit metadata
- **Validation Card:** Interface presenting a conflict, claim, or proposed edit for curator review with all relevant context
- **Trust Routing:** The process of routing incoming claims to appropriate handling paths (auto-accept, pending, escalation) based on confidence, sensitivity, and other factors
- **Verification State:** The status of a claim or block within the curation workflow (accepted, pending, disputed, etc.)
- **Conflict Record:** A structured record of a detected contradiction or disagreement requiring resolution
- **Maintenance Tag:** A visible marker on curated content indicating quality issues or review needs
- **Review Tier:** Level of review authority (Field/Local, Regional, HQ/Thematic) for handling conflicts and sensitive changes
- **Retroaction Loop:** The bidirectional feedback mechanism where curation actions update all relevant system states and records
- **Community Trust:** Confidence scoring based on trusted users viewing content without flagging issues
- **Canonical Graph:** The trusted machine-readable knowledge state stored as a Labeled Property Graph
- **Website Crawler:** Component that automatically discovers files on user-specified websites
- **File Selector:** UI component that allows users to review and select files for ingestion
- **Discovered File:** A file found during website crawling, available for selection and ingestion
- **Scrape Session:** A single run of the website crawler, tracking all discovered and processed files
- **Enterprise Scale:** Horizontal scaling capability to handle unlimited website sizes and file volumes
- **Error Panel:** Dedicated UI component displaying crawling and ingestion errors with detailed logs
- **WCAG 2.1 AA:** Web Content Accessibility Guidelines 2.1 Level AA compliance standard
- **URL Path Versioning:** API versioning strategy using version numbers in URL paths (e.g., /api/v1/)

---

## 13. Next Steps

1. Validate and refine this spec with stakeholders
2. Initialize the `.specify/` directory in the repository
3. Use `/specify` to generate the corresponding plan and tasks files
4. Begin implementation with test-driven development
5. **Priority:** Start with website crawler and file discovery (Phase 1)
6. Implement file selector UI and automatic ingestion trigger (Phase 2)
7. Implement core surfaces (Curated Wiki, Discussion, Revision/Audit) and trust routing
8. Implement validation card workflows and verification state management
9. Test with real humanitarian websites

---

## 14. Revision History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2026-05-12 | 3.0 | Edouard Legoupil | Major revision: Added website scraping workflow as starting point. User defines website URL, system auto-explores and identifies files, user selects, ingestion starts automatically. Added new entities: Website, DiscoveredFile, ScrapeSession, IngestionJob. Added new functional requirements FR-001 through FR-003 for crawling. Added new non-functional requirements NFR-009 and NFR-010. Added new user stories for Website Scraper role. Updated architecture diagram and workflow. |
| 2026-04-12 | 2.0 | Edouard Legoupil | Initial comprehensive spec with 23 FRs, 8 NFRs, 8 user stories, 6 knowledge card types |

---

**Reviewers:**

- Project Lead
- Technical Lead
- Curator Representative
- Review Tier Representatives (Field, Regional, HQ)
- Website Scraping Expert (NEW)
