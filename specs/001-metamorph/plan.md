# Metamorph Implementation Plan

**Spec ID:** 001-metamorph  
**Version:** 1.0  
**Status:** Draft  
**Date:** 2026-04-12

---

## Overview

This implementation plan outlines the phased approach to building Metamorph, a document-to-knowledge intelligence system for UN and international humanitarian organizations. The plan follows a Test-Driven Development (TDD) approach as specified in NFR-006.

---

## Phase 1: Ingestion & Extraction (Weeks 1-4)

### Objectives
- Establish document parsing pipeline
- Implement semantic triplet extraction
- Create graph storage foundation
- Validate parsing accuracy

### Deliverables
1. **Document Parser Integration**
   - Integrate Docling for standard document formats (PDF, Word, HTML)
   - Integrate MinerU for complex document layouts
   - Create unified parsing interface
   - Handle error cases and fallback mechanisms

2. **Semantic Triplet Extraction**
   - Implement Subject-Predicate-Object extraction
   - Support eight knowledge domains:
     - Geographic
     - Crisis
     - Demographics
     - Programming
     - Policy
     - Finance
     - Human Resources
     - Knowledge Assets
   - Extract entities, relationships, and metadata
   - Validate triplet quality and completeness

3. **Graph Storage**
   - Set up Neo4j (or alternative Labeled Property Graph database)
   - Design node schema (Documents, Entities, Events, Interventions, Outcomes)
   - Design edge schema (Relationships: funded_by, affected_by, implemented_by, operates_in, covers)
   - Implement CRUD operations for graph data
   - Add provenance tracking to all nodes and edges

4. **Testing & Validation**
   - Write unit tests for parsing accuracy (FR-001)
   - Write unit tests for extraction quality (FR-002)
   - Write unit tests for graph storage operations
   - Test with sample humanitarian documents
   - Validate graph integrity and query performance

### Success Criteria
- [ ] Parse 100+ sample documents with >95% accuracy
- [ ] Extract triplets from documents with >90% completeness
- [ ] Store and query graph data with <100ms response time
- [ ] All Phase 1 unit tests passing

---

## Phase 2: Knowledge Reconciliation (Weeks 5-8)

### Objectives
- Detect changes and contradictions in knowledge
- Implement delta alerting system
- Build reconciliation workflow
- Create curation interface foundation

### Deliverables
1. **Delta Detection Engine**
   - Implement change detection algorithm
   - Detect contradictions across quantitative values
   - Detect contradictions across normative statements
   - Detect contradictions across classifications
   - Support temporal mismatch detection (FR-004)

2. **Trust Routing System**
   - Implement auto-accept logic for high-confidence updates
   - Implement pending queue for moderate-confidence updates
   - Implement escalation logic for low-confidence or sensitive updates
   - Route based on confidence, sensitivity, source reliability, contradiction level

3. **Validation Card Workflow**
   - Create validation card interface
   - Display current vs. proposed values with diff
   - Show evidence, provenance, confidence scores
   - Support actions: Approve, Reject, Merge/Edit, Escalate, Open Discussion
   - Link to discussion threads (FR-012)

4. **Curation Interface (MVP)**
   - Basic web interface for curators
   - Display validation card queue
   - Allow curator actions on cards
   - Track verification state transitions

5. **Testing & Validation**
   - Write unit tests for delta detection (FR-004)
   - Write unit tests for trust routing logic
   - Write integration tests for validation card workflow
   - Validate with real-world conflicting data scenarios

### Success Criteria
- [ ] Detect changes with >95% accuracy
- [ ] Route 100% of incoming claims appropriately
- [ ] Process validation cards in <5 minutes average
- [ ] All Phase 2 unit and integration tests passing

---

## Phase 3: Knowledge Cards (Weeks 9-12)

### Objectives
- Define and implement all six Knowledge Card types
- Create card generation, approval, and expiry workflows
- Build card management interface

### Deliverables
1. **Knowledge Card Templates**
   - **KC-1: Donor Intelligence** (Validity: 12 months)
     - Understand funder priorities and requirements
   - **KC-2: Field Context** (Validity: 6 months)
     - Describe situation, needs, risks
   - **KC-3: Outcome Evidence** (Validity: 12 months)
     - Summarize effective interventions and costs
   - **KC-4: Partner Capacity** (Validity: 6 months)
     - Assess partner ability to deliver
   - **KC-5: Institutional Track Record** (Validity: 24 months)
     - Highlight UNHCR credibility and past performance
   - **KC-6: Crisis Political Economy** (Validity: 6 months)
     - Explain why a crisis is strategic at this time

2. **Card Workflow Engine**
   - Implement Draft → Approved → Expired → Draft lifecycle
   - Enforce validity periods (FR-006)
   - Prevent use of expired cards in proposals
   - Support card versioning and rollback

3. **Card Generation**
   - Automated card generation from graph data
   - Manual card editing interface
   - Card quality validation
   - Card provenance tracking

4. **Card Management Interface**
   - Card library/browser
   - Card search and filtering
   - Card approval workflow
   - Card expiry alerts

5. **Testing & Validation**
   - Write unit tests for card generation (FR-005)
   - Write unit tests for card workflow
   - Write integration tests for card-proposal integration
   - Validate with all six card types

### Success Criteria
- [ ] Generate all six card types automatically
- [ ] Approve/reject cards in <10 minutes average
- [ ] Maintain 100% traceability to source documents
- [ ] All Phase 3 unit and integration tests passing

---

## Phase 4: Agentic Proposal Drafting & Deployment (Weeks 13-16)

### Objectives
- Implement agentic proposal drafting
- Deploy system to production
- Establish monitoring and maintenance

### Deliverables
1. **Agentic Drafting System**
   - Assemble relevant knowledge cards for proposals
   - Score interventions based on context
   - Generate draft proposals (FR-008)
   - Support multi-model agentic workflows (NFR-005)

2. **Three Knowledge Surfaces**
   - **Curated Wiki Surface**: Reader-facing accepted knowledge (FR-010)
   - **Discussion & Review Surface**: Contested knowledge evaluation
   - **Revision & Audit Surface**: Immutable change history

3. **Curation Controls**
   - In-wiki verification, flagging, editing (FR-013)
   - Reverts and rollbacks (FR-022)
   - Watchers and notifications (FR-020)
   - Maintenance tags (FR-017)

4. **Community Trust Features**
   - Trust scoring based on user behavior (FR-021)
   - Community verification indicators

5. **API Layer**
   - REST/GraphQL API for downstream use (FR-009)
   - Minimum API endpoints for curation
   - Authentication and authorization

6. **Deployment**
   - Staging environment deployment
   - Production environment deployment
   - CI/CD pipeline setup
   - Monitoring and alerting

7. **Testing & Validation**
   - Write acceptance tests for proposal drafting
   - Write acceptance tests for traceability
   - Write acceptance tests for curation workflows
   - Write regression tests
   - Performance testing
   - Security testing

### Success Criteria
- [ ] Draft first proposal using agentic system
- [ ] Deploy to production with <1 hour downtime
- [ ] All acceptance tests passing
- [ ] System handles 100+ concurrent users

---

## Phase 5: Integration & Enhancement (Weeks 17-20)

### Objectives
- Full integration with UN systems
- Deploy watchers, notifications
- Continuous improvement

### Deliverables
1. **UN System Integration**
   - API integration with existing UN systems
   - Single Sign-On (SSO) integration
   - Data synchronization

2. **Advanced Features**
   - Review tiers and escalation (FR-018)
   - Human retroaction feedback loop (FR-019)
   - Conflict detection queuing (FR-016)
   - Consensus model implementation (FR-015)

3. **Dashboards**
   - Audit and QA dashboards (FR-023)
   - Curator productivity dashboard
   - System health dashboard

4. **Documentation**
   - User documentation
   - API documentation
   - Administrator documentation

---

## Milestone Summary

| Milestone | Phase | Duration | Key Deliverable |
|-----------|-------|----------|-----------------|
| M1 | Phase 1 Complete | Week 4 | Document parsing & graph storage |
| M2 | Phase 2 Complete | Week 8 | Knowledge reconciliation system |
| M3 | Phase 3 Complete | Week 12 | Knowledge card system |
| M4 | Phase 4 Complete | Week 16 | Agentic proposal drafting |
| M5 | Phase 5 Complete | Week 20 | Full production deployment |

---

## Resource Requirements

### Human Resources
- 1 Technical Lead (Full-time)
- 2 Backend Developers (Full-time)
- 1 Frontend Developer (Full-time)
- 1 QA Engineer (Part-time)
- 1-2 Domain Experts (UN/Humanitarian) (Part-time)

### Technology Stack
- **Document Parsing:** Docling, MinerU
- **Graph Storage:** Neo4j
- **API:** FastAPI/GraphQL
- **Frontend:** React/Vue.js
- **Agentic System:** Mistral Vibe CLI, Claude Code, etc.
- **Testing:** pytest, custom test harness
- **Infrastructure:** Docker, Kubernetes (optional)

---

## Risk Management

### Technical Risks
| Risk | Mitigation |
|------|------------|
| Document parsing accuracy | Use multiple parsers, implement validation |
| Graph query performance | Optimize indexes, implement caching |
| Data consistency | Implement transactions, add validation |
| System scalability | Design for horizontal scaling from start |

### Operational Risks
| Risk | Mitigation |
|------|------------|
| User adoption | Involve curators early, provide training |
| Data quality | Implement comprehensive validation, trust routing |
| Security vulnerabilities | Regular security audits, penetration testing |
| Compliance issues | Work with UN legal/compliance teams, implement audit trails |

---

## Quality Assurance

### Testing Approach
- **Unit Tests:** All functions and components (NFR-006)
- **Integration Tests:** Component interactions
- **Acceptance Tests:** User workflows and requirements
- **Regression Tests:** Prevent regressions during evolution
- **Performance Tests:** Ensure system meets performance targets
- **Security Tests:** Identify and fix vulnerabilities

### Quality Gates
- All unit tests must pass before merging
- All integration tests must pass before staging deployment
- All acceptance tests must pass before production deployment
- Code review required for all changes
- Security review for sensitive changes

---

## Monitoring & Maintenance

### Monitoring
- System health metrics
- Performance metrics
- Error rates and types
- User activity metrics
- Data quality metrics

### Maintenance
- Regular backups
- Security patch management
- Performance optimization
- User feedback collection
- Continuous improvement
