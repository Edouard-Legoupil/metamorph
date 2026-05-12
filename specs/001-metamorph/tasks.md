# Metamorph Task List

**Spec ID:** 001-metamorph  
**Version:** 1.0  
**Status:** Draft  
**Date:** 2026-04-12

---

## Task Tracking

This document tracks all implementation tasks for the Metamorph project. Tasks are organized by phase and priority, with checkboxes for completion tracking.

---

## 🚀 Phase 1: Ingestion & Extraction

### High Priority
- [ ] **FR-001: Document Parsing Setup**
  - [ ] Install and configure Docling
  - [ ] Install and configure MinerU
  - [ ] Create document upload endpoint
  - [ ] Implement document type detection
  - [ ] Add error handling for unsupported formats

- [ ] **FR-002: Semantic Triplet Extraction**
  - [ ] Design triplet schema (Subject, Predicate, Object, Qualifiers)
  - [ ] Implement entity recognition (8 domains)
  - [ ] Implement relationship extraction
  - [ ] Implement metadata extraction
  - [ ] Add extraction confidence scoring

- [ ] **Graph Storage Foundation**
  - [ ] Set up Neo4j database
  - [ ] Design node labels (Document, Entity, Event, Intervention, Outcome)
  - [ ] Design relationship types
  - [ ] Implement node creation with provenance
  - [ ] Implement relationship creation with provenance
  - [ ] Add graph query interface

- [ ] **Testing: Phase 1**
  - [ ] Write unit tests for Docling integration
  - [ ] Write unit tests for MinerU integration
  - [ ] Write unit tests for triplet extraction
  - [ ] Write unit tests for graph storage operations
  - [ ] Create test dataset (100+ sample documents)
  - [ ] Run parsing accuracy validation (>95%)
  - [ ] Run extraction completeness validation (>90%)

### Medium Priority
- [ ] Implement document preprocessing (OCR, cleanup)
- [ ] Add support for additional document formats
- [ ] Implement batch processing
- [ ] Add document versioning
- [ ] Create document processing dashboard

---

## 🔄 Phase 2: Knowledge Reconciliation

### High Priority
- [ ] **FR-004: Delta Detection Engine**
  - [ ] Implement change detection algorithm
  - [ ] Detect contradictions in quantitative values
  - [ ] Detect contradictions in normative statements
  - [ ] Detect contradictions in classifications
  - [ ] Implement temporal mismatch detection
  - [ ] Add severity scoring for conflicts

- [ ] **Trust Routing System**
  - [ ] Implement auto-accept logic (FR-004 conditions)
  - [ ] Implement pending queue for moderate-confidence updates
  - [ ] Implement escalation logic for low-confidence/sensitive updates
  - [ ] Add source reliability classification
  - [ ] Add sensitivity classification
  - [ ] Add contradiction level detection

- [ ] **FR-012: Validation Card Workflow**
  - [ ] Create validation card data model
  - [ ] Implement validation card generation
  - [ ] Add diff display (current vs. proposed)
  - [ ] Add evidence display
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

- [ ] **FR-013: Curation Interface (MVP)**
  - [ ] Design curator dashboard layout
  - [ ] Implement validation card queue display
  - [ ] Add card filtering by type, severity, age
  - [ ] Add card sorting options
  - [ ] Implement curator actions on cards
  - [ ] Add action confirmation dialogs
  - [ ] Track verification state transitions

- [ ] **Testing: Phase 2**
  - [ ] Write unit tests for delta detection
  - [ ] Write unit tests for trust routing
  - [ ] Write integration tests for validation card workflow
  - [ ] Validate with conflicting data scenarios
  - [ ] Test all verification state transitions

### Medium Priority
- [ ] Implement validation card queue management
- [ ] Add bulk actions on validation cards
- [ ] Implement card assignment to curators
- [ ] Add curator productivity metrics
- [ ] Create validation card history/audit trail

---

## 📚 Phase 3: Knowledge Cards

### High Priority
- [ ] **FR-005: Knowledge Card Templates**
  - [ ] Design KC-1: Donor Intelligence template
  - [ ] Design KC-2: Field Context template
  - [ ] Design KC-3: Outcome Evidence template
  - [ ] Design KC-4: Partner Capacity template
  - [ ] Design KC-5: Institutional Track Record template
  - [ ] Design KC-6: Crisis Political Economy template

- [ ] **FR-006: Card Workflow Engine**
  - [ ] Implement Draft state
  - [ ] Implement Approved state
  - [ ] Implement Expired state
  - [ ] Implement state transitions (Draft → Approved → Expired → Draft)
  - [ ] Enforce validity periods per card type
  - [ ] Prevent use of expired cards in proposals
  - [ ] Implement card versioning
  - [ ] Implement card rollback

- [ ] **Card Generation**
  - [ ] Implement automated card generation from graph data
  - [ ] Add card quality validation
  - [ ] Add card provenance tracking
  - [ ] Implement card preview
  - [ ] Implement card publishing

- [ ] **FR-010: Three Knowledge Surfaces**
  - [ ] **Curated Wiki Surface**
    - [ ] Design wiki page structure
    - [ ] Implement accepted knowledge display
    - [ ] Add provenance badges
    - [ ] Add freshness indicators
    - [ ] Implement verification state badges
    - [ ] Add maintenance tag display
    - [ ] Link to discussion threads
  - [ ] **Discussion & Review Surface**
    - [ ] Design discussion interface (Wikipedia Talk tab equivalent)
    - [ ] Implement discussion thread creation
    - [ ] Add thread linking to topics/entities/blocks/claims
    - [ ] Implement thread status tracking
    - [ ] Add consensus model evaluation
  - [ ] **Revision & Audit Surface**
    - [ ] Design immutable revision history display
    - [ ] Implement change diff viewing
    - [ ] Add audit event display
    - [ ] Implement state restoration

- [ ] **Testing: Phase 3**
  - [ ] Write unit tests for card generation
  - [ ] Write unit tests for card workflow
  - [ ] Write integration tests for card-proposal integration
  - [ ] Validate with all six card types
  - [ ] Test card expiry enforcement

### Medium Priority
- [ ] Implement card search and filtering
- [ ] Add card export (PDF, CSV)
- [ ] Implement card watchers/notifications
- [ ] Add card analytics and usage tracking
- [ ] Create card library/browser interface

---

## 🤖 Phase 4: Agentic Proposal Drafting & Deployment

### High Priority
- [ ] **FR-008: Agentic Drafting System**
  - [ ] Design proposal generation workflow
  - [ ] Implement card assembly for proposals
  - [ ] Add intervention scoring algorithm
  - [ ] Implement draft proposal generation
  - [ ] Add proposal review interface
  - [ ] Implement proposal iteration

- [ ] **FR-009: API Layer**
  - [ ] Design REST API endpoints
  - [ ] Design GraphQL schema (optional)
  - [ ] Implement API authentication
  - [ ] Implement API authorization
  - [ ] Add rate limiting
  - [ ] Add API documentation

- [ ] **Minimum API Endpoints for Curation**
  - [ ] GET /topics/{id}
  - [ ] GET /topics/{id}/curated
  - [ ] GET /topics/{id}/discussion
  - [ ] GET /topics/{id}/history
  - [ ] POST /topics/{id}/blocks/{block_id}/edit
  - [ ] POST /topics/{id}/blocks/{block_id}/verify
  - [ ] POST /topics/{id}/blocks/{block_id}/flag
  - [ ] POST /topics/{id}/blocks/{block_id}/revert
  - [ ] POST /claims/{id}/validate
  - [ ] POST /claims/{id}/reject
  - [ ] POST /claims/{id}/merge
  - [ ] POST /claims/{id}/escalate
  - [ ] GET /conflicts
  - [ ] GET /conflicts/{id}
  - [ ] POST /conflicts/{id}/review
  - [ ] POST /conflicts/{id}/resolve
  - [ ] POST /conflicts/{id}/dismiss
  - [ ] POST /conflicts/{id}/escalate
  - [ ] POST /discussion/threads
  - [ ] GET /discussion/threads/{id}
  - [ ] POST /discussion/threads/{id}/comments
  - [ ] POST /discussion/threads/{id}/close
  - [ ] POST /discussion/threads/{id}/apply-consensus
  - [ ] POST /tags
  - [ ] DELETE /tags/{id}
  - [ ] GET /audit/events
  - [ ] GET /revisions/{target_type}/{target_id}
  - [ ] GET /validation/cards
  - [ ] GET /validation/cards/{id}
  - [ ] POST /validation/cards/{id}/approve
  - [ ] POST /validation/cards/{id}/reject
  - [ ] POST /validation/cards/{id}/merge
  - [ ] POST /validation/cards/{id}/escalate
  - [ ] GET /api/v1/enumerate-cards
  - [ ] GET /api/v1/cards/{card_id}
  - [ ] GET /api/v1/blocks/card/{card_id}

- [ ] **Deployment**
  - [ ] Set up staging environment
  - [ ] Set up production environment
  - [ ] Implement CI/CD pipeline
  - [ ] Configure monitoring and alerting
  - [ ] Set up logging
  - [ ] Configure backups
  - [ ] Implement disaster recovery plan

- [ ] **Testing: Phase 4**
  - [ ] Write acceptance tests for proposal drafting
  - [ ] Write acceptance tests for traceability (FR-007)
  - [ ] Write acceptance tests for curation workflows
  - [ ] Write regression tests
  - [ ] Run performance testing
  - [ ] Run security testing

### Medium Priority
- [ ] Implement API versioning
- [ ] Add API rate limiting by user/tier
- [ ] Implement API caching
- [ ] Add comprehensive API error handling
- [ ] Create API client libraries

---

## 🎯 Phase 5: Integration & Enhancement

### High Priority
- [ ] **UN System Integration**
  - [ ] Integrate with UN authentication systems (SSO)
  - [ ] Synchronize data with existing UN systems
  - [ ] Implement role-based access control

- [ ] **FR-018: Review Tiers and Escalation**
  - [ ] Implement Tier 1 (Field/Local) review queue
  - [ ] Implement Tier 2 (Regional) review queue
  - [ ] Implement Tier 3 (HQ/Thematic) review queue
  - [ ] Add automatic tier assignment logic
  - [ ] Implement escalation workflow
  - [ ] Add decision SLAs per tier

- [ ] **FR-019: Human Retroaction Feedback Loop**
  - [ ] Implement action recording for all curation actions
  - [ ] Create audit log entries for all actions
  - [ ] Implement revision entries for state changes
  - [ ] Update curation table on actions
  - [ ] Update claim/fact/entity records on actions
  - [ ] Update graph state on accepted changes
  - [ ] Implement UI refresh events
  - [ ] Implement notification events

- [ ] **FR-015: Discussion Thread Workflow**
  - [ ] Implement thread creation
  - [ ] Add thread status tracking (open, under_review, consensus_reached, no_consensus, rejected, escalated, resolved, archived)
  - [ ] Implement consensus model (evidence quality, policy compliance, reviewer expertise, etc.)
  - [ ] Add consensus result tracking (accept, reject, merge, no_consensus, escalate, defer_until_more_evidence)

- [ ] **FR-023: Audit and QA Dashboards**
  - [ ] Design audit dashboard layout
  - [ ] Implement live/historic decision display
  - [ ] Add unresolved conflicts display
  - [ ] Add pending discussions display
  - [ ] Implement dashboard filtering and sorting

### Medium Priority
- [ ] **FR-016: Conflict Handling Workflow**
  - [ ] Implement conflict detection across all types
  - [ ] Create conflict queue
  - [ ] Implement conflict validation card creation
  - [ ] Add conflict discussion opening
  - [ ] Implement evidence review process
  - [ ] Add consensus/escalation/no consensus handling

- [ ] **FR-017: Maintenance Tags**
  - [ ] Implement citation_needed tag
  - [ ] Implement source_review_needed tag
  - [ ] Implement disputed tag
  - [ ] Implement stale tag
  - [ ] Implement freshness_review_needed tag
  - [ ] Implement conflicting_values tag
  - [ ] Implement low_confidence tag
  - [ ] Implement policy_review_needed tag
  - [ ] Implement regional_validation_needed tag
  - [ ] Implement neutrality_or_framing_issue tag
  - [ ] Implement duplicate_possible tag
  - [ ] Implement graph_conflict tag

- [ ] **FR-020: Watchers and Notifications**
  - [ ] Implement watcher system for topics
  - [ ] Implement watcher system for entities
  - [ ] Implement watcher system for blocks
  - [ ] Implement watcher system for claims
  - [ ] Implement watcher system for discussions
  - [ ] Implement watcher system for review queues
  - [ ] Add notification triggers for all watchable events

- [ ] **FR-021: Community Trust**
  - [ ] Implement trusted user tracking
  - [ ] Add view tracking for blocks
  - [ ] Implement trust scoring algorithm
  - [ ] Add trust score display

- [ ] **Documentation**
  - [ ] Write user documentation
  - [ ] Write API documentation
  - [ ] Write administrator documentation
  - [ ] Create getting started guide
  - [ ] Create troubleshooting guide

---

## 📊 Non-Functional Requirements Tasks

### High Priority
- [ ] **NFR-001: Human judgment is not optional** - Design all workflows to require human approval for critical decisions
- [ ] **NFR-002: Every claim must be traceable** - Implement provenance tracking for all data
- [ ] **NFR-003: Honesty over presentation** - Design UI to surface difficulties, risks, gaps
- [ ] **NFR-004: Expiry is a feature** - Implement validity period enforcement
- [ ] **NFR-005: Support multi-model agentic workflows** - Avoid model lock-in
- [ ] **NFR-006: Test-driven development** - Write tests before implementation
- [ ] **NFR-007: Immutable audit trails** - Implement audit logging for all changes
- [ ] **NFR-008: Separation of concerns** - Keep curated knowledge separate from contested knowledge

---

## 🎨 UI/UX Tasks

- [ ] Design curator dashboard
- [ ] Design proposal writer interface
- [ ] Design donor interface
- [ ] Design reviewer interface
- [ ] Implement responsive design
- [ ] Add accessibility features
- [ ] Create style guide
- [ ] Implement design system

---

## 🔧 Infrastructure Tasks

- [ ] Set up development environment
- [ ] Configure database
- [ ] Set up authentication/authorization
- [ ] Configure monitoring
- [ ] Set up logging
- [ ] Configure backups
- [ ] Implement security measures
- [ ] Set up CI/CD pipeline

---

## 📈 Analytics & Reporting Tasks

- [ ] Implement user activity tracking
- [ ] Add system performance metrics
- [ ] Create data quality reports
- [ ] Implement curator productivity reports
- [ ] Add system health dashboards
- [ ] Create custom report builder

---

## 🎓 Training & Onboarding Tasks

- [ ] Create curator training materials
- [ ] Develop proposal writer training
- [ ] Create reviewer training
- [ ] Develop administrator training
- [ ] Create user onboarding workflow
- [ ] Implement in-app help system

---

## Summary Statistics

| Phase | Total Tasks | Completed | In Progress | Pending |
|-------|-------------|-----------|------------|---------|
| Phase 1 | 28 | 0 | 0 | 28 |
| Phase 2 | 42 | 0 | 0 | 42 |
| Phase 3 | 38 | 0 | 0 | 38 |
| Phase 4 | 45 | 0 | 0 | 45 |
| Phase 5 | 35 | 0 | 0 | 35 |
| **Total** | **188** | **0** | **0** | **188** |

---

## Next Steps

1. **Start with Phase 1** - Document parsing and graph storage are foundational
2. **Follow TDD approach** - Write tests before implementation (NFR-006)
3. **Focus on core workflows** - Prioritize FR-001, FR-002, FR-004, FR-005
4. **Validate frequently** - Test with real humanitarian documents early
5. **Involve curators early** - Get feedback on workflows and interfaces

---

## Notes

- Tasks marked with **[FR-XXX]** correspond to Functional Requirements from spec.md
- Tasks marked with **[NFR-XXX]** correspond to Non-Functional Requirements from spec.md
- All tasks should follow the Test-Driven Development approach (NFR-006)
- Refer to spec.md for detailed requirements and specifications
- Update this file as tasks are completed or new tasks are identified
