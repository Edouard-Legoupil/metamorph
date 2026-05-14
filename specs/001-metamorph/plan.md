# Implementation Plan: Metamorph Website-to-Knowledge System

**Branch**: `001-metamorph` | **Date**: 2026-05-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-metamorph/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

**Primary Requirement**: Implement website-to-knowledge intelligence system for UN and humanitarian organizations that automatically explores websites, discovers scrapable files, allows user selection, and ingests knowledge into a curated knowledge graph.

**Technical Approach**: 
- **Website Crawling**: Python-based crawler with requests/BeautifulSoup and Playwright fallback for JavaScript sites
- **File Discovery**: Automatic exploration with sitemap.xml parsing and internal link following
- **User Interface**: React/TypeScript frontend with file selection, preview, and bulk operations
- **Document Parsing**: Docling for standard documents, MinerU for complex layouts
- **Knowledge Storage**: Neo4j Labeled Property Graph with provenance tracking
- **Processing**: Asynchronous background ingestion with progress tracking and error handling
- **API**: FastAPI REST endpoints with URL path versioning (/api/v1/)
- **Accessibility**: WCAG 2.1 AA compliant interfaces
- **Scale**: Enterprise-grade horizontal scaling for unlimited website sizes

**Key Features**: Website crawler, file selector UI, automatic ingestion trigger, knowledge reconciliation, three-surface curation model (Curated Wiki, Discussion/Review, Revision/Audit), six knowledge card types, and agentic proposal drafting.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.0+ (frontend)
**Primary Dependencies**: FastAPI, React, Neo4j, Docling, MinerU, Playwright, BeautifulSoup, requests
**Storage**: Neo4j (Labeled Property Graph) for knowledge graph, with potential file storage for documents
**Testing**: pytest (backend), Jest/React Testing Library (frontend)
**Target Platform**: Linux server (backend), Modern web browsers (Chrome, Firefox, Safari, Edge)
**Project Type**: Web service with frontend application (Full-stack web application)
**Performance Goals**: Enterprise scale with horizontal scaling capability, asynchronous background processing for crawling and ingestion
**Constraints**: WCAG 2.1 AA compliance for all user interfaces, respectful web scraping (robots.txt compliance, rate limiting), traceability of all knowledge to source websites
**Scale/Scope**: Unlimited website sizes with horizontal scaling, designed to handle UN and humanitarian organization websites with thousands to millions of pages

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Post-Design Constitution Compliance (Phase 1 Re-evaluation)

✅ **Human judgment is not optional**: 
- Validation card system requires human review for all contested knowledge
- Three-tier review system (Field/Local, Regional, HQ/Thematic) implemented
- No auto-approval for sensitive or high-impact changes

✅ **Every claim must be traceable**:
- Complete provenance chain: Website → DiscoveredFile → Document → Entity → KnowledgeCard → WikiBlock
- Source website URL, file URL, extraction date, curator, and validator tracked for every claim
- Audit trail for all state transitions and curation actions

✅ **Honesty over presentation**:
- Maintenance tags system (citation_needed, source_review_needed, disputed, stale)
- Discussion surfaces for contested knowledge with full transparency
- Conflict detection and surfacing across all knowledge dimensions
- Error panel for ingestion failures with detailed logs

✅ **Expiry is a feature**:
- Validity periods enforced for all knowledge cards
- Automatic expiration workflow (approved → expired)
- Expiry reasons documented and tracked
- Prevention of expired card usage in proposals

✅ **Website-first workflow**:
- User journey starts with website URL definition
- Automatic exploration before any manual document handling
- File selection from discovered files, not manual uploads
- Website scraping as primary knowledge source

### Enhanced Technical Compliance

✅ **Comprehensive Data Model**:
- All 5 core entities (Website, DiscoveredFile, ScrapeSession, IngestionJob, Document)
- Complete knowledge graph schema with 8 entity types
- 6 knowledge card types with full lifecycle management
- State machines for all workflows (cards, validation, discussions)

✅ **API Contracts**:
- 50+ REST endpoints documented with OpenAPI specification
- JWT authentication with role-based access control
- Comprehensive error handling and rate limiting
- Webhook support for real-time notifications

✅ **Research-Based Decisions**:
- Testing framework: pytest (backend) + Jest (frontend)
- CI/CD: GitHub Actions with multi-stage workflows
- Monitoring: Prometheus + Grafana + OpenTelemetry
- Deployment: Docker + Kubernetes with horizontal scaling
- Security: Defense-in-depth approach with encryption and audit logging

### Workflow Enhancements

✅ **Complete Website-to-Knowledge Pipeline**:
```text
Website Definition → Automatic Crawling → File Discovery → User Selection →
Automatic Ingestion → Document Parsing → Knowledge Extraction → Graph Storage →
Reconciliation → Curation → Validation → Card Generation → Proposal Drafting
```

✅ **Three-Surface Curation Model**:
- **Curated Wiki Surface**: Reader-facing accepted knowledge
- **Discussion/Review Surface**: Contested knowledge evaluation
- **Revision/Audit Surface**: Immutable change history

✅ **Trust Routing Implementation**:
- Auto-accept for high-confidence, low-risk updates
- Pending queue for moderate-confidence updates
- Escalation for low-confidence, sensitive, or contradictory updates
- Tier-based review assignment (Tier 1, 2, 3)

### Gate Status: ✅ PASS (Post-Design)

**All constitution principles satisfied with enhanced implementation details.**

The Phase 1 design has successfully:
1. Resolved all NEEDS CLARIFICATION items from Technical Context
2. Maintained all constitutional principles
3. Added comprehensive data model and API contracts
4. Ensured traceability, honesty, and human judgment throughout
5. Preserved the website-first approach and expiry features

**Ready to proceed to Phase 2: Task Generation**

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
# Metamorph Web Application Structure
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── crawler_settings.py
│   │       │   ├── team_members.py
│   │       │   ├── topics.py
│   │       │   ├── users.py
│   │       │   ├── website_topics.py
│   │       │   └── websites.py
│   │       └── ...
│   ├── core/
│   │   └── config.py
│   ├── database.py
│   ├── main.py
│   └── models/
│       ├── __init__.py
│       └── sql/
│           └── [SQL models]
├── tests/
│   ├── unit/
│   └── integration/
└── requirements.txt

frontend/
├── public/
├── src/
│   ├── components/
│   │   ├── NavBar.tsx
│   │   └── [UI components]
│   ├── pages/
│   │   ├── TeamManagement.tsx
│   │   ├── TopicManagement.tsx
│   │   ├── UserManagement.tsx
│   │   ├── WebsiteManagement.tsx
│   │   └── [other pages]
│   ├── services/
│   │   └── [API services]
│   ├── App.tsx
│   └── main.tsx
└── tests/

specs/
└── 001-metamorph/
    ├── plan.md              # This file
    ├── research.md          # Phase 0 output
    ├── data-model.md        # Phase 1 output
    ├── quickstart.md        # Phase 1 output
    ├── contracts/           # Phase 1 output
    └── tasks.md             # Phase 2 output

.specify/
└── [Speckit configuration and memory]
```

**Structure Decision**: Web application structure (Option 2) selected due to the full-stack nature of Metamorph with separate backend (FastAPI) and frontend (React/TypeScript) components. The structure follows standard patterns for each technology stack while maintaining clear separation of concerns between API, business logic, and presentation layers.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
