# Metamorph: Humanitarian Knowledge Pipeline

**Spec ID:** 001-metamorph  
**Version:** 1.0  
**Author:** Edouard Legoupil  
**Date:** 2026-04-12  
**Status:** Draft

---

## 1. Executive Summary

Metamorph is a document-to-knowledge intelligence system for UN and international humanitarian organizations. Its goal is to transform a passive document library into a living, queryable knowledge base, directly supporting the generation of high-quality project proposals.

**Core Objectives:**

- Ingest and extract structured knowledge from diverse humanitarian documents.
- Reconcile and update knowledge, surfacing contradictions and changes.
- Provide human-curated knowledge cards as the primary output, ensuring traceability and validity.
- Enable agentic systems to draft proposals based on curated, up-to-date knowledge.

---

## 2. Requirements

### 2.1 Functional Requirements


| ID     | Requirement                                                   | Priority | Notes                                                                                |
| ------ | ------------------------------------------------------------- | -------- | ------------------------------------------------------------------------------------ |
| FR-001 | Ingest and parse documents using Docling and MinerU           | High     | Support standard and complex document layouts                                        |
| FR-002 | Extract semantic triplets (Subject → Predicate → Object)      | High     | Store in a Labeled Property Graph                                                    |
| FR-003 | Map extracted knowledge to eight domains                      | High     | Geographic, crisis, demographics, programming, policy, finance, HR, knowledge assets |
| FR-004 | Detect and surface changes, contradictions, and confirmations | High     | Delta alerting for human curators                                                    |
| FR-005 | Generate six types of Knowledge Cards (KC-1 to KC-6)          | High     | See section 4 for card details                                                       |
| FR-006 | Enforce validity periods and draft/expiry workflows           | High     | Cards must be approved and not expired to be used in proposals                       |
| FR-007 | Support traceability of every claim to source nodes           | High     | Provenance and date tracking for auditability                                        |
| FR-008 | Enable agentic proposal drafting                              | High     | Assemble cards, score interventions, generate drafts                                 |
| FR-009 | Provide API and query interface for downstream use            | Medium   | Integration with other systems                                                       |


---

### 2.2 Non-Functional Requirements


| ID      | Requirement                           | Priority | Notes                                              |
| ------- | ------------------------------------- | -------- | -------------------------------------------------- |
| NFR-001 | Human judgment is not optional        | High     | System assists curators; does not replace judgment |
| NFR-002 | Every claim must be traceable         | High     | Provenance, document source, date, curator         |
| NFR-003 | Honesty over presentation             | High     | Surface difficulties, risks, and gaps              |
| NFR-004 | Expiry is a feature                   | High     | Validity periods enforced for all cards            |
| NFR-005 | Support multi-model agentic workflows | Medium   | Avoid model lock-in, enforce robustness            |
| NFR-006 | Test-driven development               | High     | Tests written before code for maintainability      |


---

## 3. User Stories

### 3.1 Curator

- **US-CUR-001:** As a curator, I want to ingest new documents and extract structured knowledge so that I can update the knowledge graph.
  - **Acceptance Criteria:**
    - Documents are parsed and decomposed into semantic triplets.
    - Triplets are stored in the graph with provenance.
    - Conflicts and changes are flagged for review.
- **US-CUR-002:** As a curator, I want to review and approve knowledge cards so that they can be used in proposals.
  - **Acceptance Criteria:**
    - Cards are pre-populated by the system.
    - Curators can edit, approve, or reject cards.
    - Approved cards are marked as valid for a set period.

### 3.2 Proposal Writer

- **US-PROP-001:** As a proposal writer, I want to query the knowledge base for relevant cards so that I can draft a proposal.
  - **Acceptance Criteria:**
    - Cards are retrievable by domain, validity, and relevance.
    - Proposals cannot be generated against expired or unapproved cards.
    - Every claim in the proposal is traceable to a source node.

### 3.3 Donor

- **US-DON-001:** As a donor, I want to see transparent, evidence-based proposals so that I can trust the funding request.
  - **Acceptance Criteria:**
    - Proposals include sourcing for every claim.
    - Difficulties and risks are acknowledged and mitigated.

---

## 4. Knowledge Cards


| ID   | Card Type                  | Purpose                                          | Validity  | Scope             |
| ---- | -------------------------- | ------------------------------------------------ | --------- | ----------------- |
| KC-1 | Donor Intelligence         | Understand funder priorities and requirements    | 12 months | Per donor         |
| KC-2 | Field Context              | Describe situation, needs, risks                 | 6 months  | Per field context |
| KC-3 | Outcome Evidence           | Summarize effective interventions and costs      | 12 months | Per outcome       |
| KC-4 | Partner Capacity           | Assess partner ability to deliver                | 6 months  | Per partner       |
| KC-5 | Institutional Track Record | Highlight UNHCR credibility and past performance | 24 months | Per operation     |
| KC-6 | Crisis Political Economy   | Explain why a crisis is strategic at this time   | 6 months  | Per crisis        |


**Card Workflow:**

- Draft → Approved → Expired → Draft
- Expired cards cannot be used in proposals.

---

## 5. Technical Constraints and Architecture

### 5.1 Architecture Overview

```
Ingestion Layer
    ↓ (Docling, MinerU)
Extraction & Graph Storage (Labeled Property Graph)
    ↓
Knowledge Reconciliation & Delta Alerting
    ↓
Human-Curated Knowledge Cards (KC-1 to KC-6)
    ↓
Agentic Proposal Drafting System
```

### 5.2 Data Model

- **Nodes:** Documents, entities (people, orgs, locations), events, interventions, outcomes.
- **Edges:** Relationships (e.g., "funded by", "affected by", "implemented by").
- **Properties:** Provenance (source document, extraction date), validity period, curator, status.

### 5.3 Technology Stack


| Component        | Technology                          | Notes                        |
| ---------------- | ----------------------------------- | ---------------------------- |
| Document Parsing | Docling, MinerU                     | Standard and complex layouts |
| Graph Storage    | Neo4j (or similar)                  | Labeled Property Graph       |
| API              | FastAPI/GraphQL                     | For downstream use           |
| Agentic System   | Mistral Vibe CLI, Claude Code, etc. | Multi-model support          |
| Testing          | pytest, custom test harness         | Test-driven development      |


---

## 6. Workflow and Phases


| Phase             | Description                                       | Output                     |
| ----------------- | ------------------------------------------------- | -------------------------- |
| Ingestion         | Parse and extract knowledge from documents        | Semantic triplets in graph |
| Reconciliation    | Detect changes, contradictions, and confirmations | Delta alerts for curators  |
| Curation          | Review and approve knowledge cards                | Validated cards            |
| Proposal Drafting | Assemble relevant cards, generate draft           | Structured proposal        |


---

## 7. Security and Compliance

- **Data Handling:** All documents and extracted knowledge must comply with UN data policies and GDPR where applicable.
- **Access Control:** Curators and proposal writers have role-based access.
- **Audit Trail:** Every change to the graph or cards is logged with timestamp and user.

---

## 8. Testing Strategy

- **Unit Tests:** Validate parsing, extraction, and graph storage.
- **Integration Tests:** Ensure delta alerts and card generation work as expected.
- **Acceptance Tests:** Verify proposal drafting and traceability.
- **Regression Tests:** Maintainability across future evolutions.

---

## 9. Deployment Plan

- **Phase 1:** Ingest and extract knowledge from a sample set of documents.
- **Phase 2:** Implement delta alerting and curation workflows.
- **Phase 3:** Deploy card generation and proposal drafting.
- **Phase 4:** Full integration with UN systems and APIs.

---

## 10. Risks and Mitigations


| Risk                            | Mitigation                                |
| ------------------------------- | ----------------------------------------- |
| Inaccurate knowledge extraction | Use multiple models and human review      |
| Stale knowledge cards           | Automated expiry and recuration reminders |
| Model lock-in                   | Multi-model agentic workflows             |
| Data privacy issues             | Compliance checks and access controls     |


---

## 11. Glossary

- **Semantic Triple:** A structured representation of knowledge as Subject → Predicate → Object.
- **Knowledge Card:** A structured document summarizing key knowledge for a specific domain.
- **Delta Alert:** Notification of changes or contradictions in the knowledge graph.
- **Agentic System:** An AI-driven system that automates proposal drafting based on curated knowledge.

---

## 12. Next Steps

1. Validate and refine this spec with stakeholders.
2. Initialize the `.specify/` directory in the repository.
3. Use `/specify` to generate the corresponding plan and tasks files.
4. Begin implementation with test-driven development.

---

**Reviewers:**

- Project Lead
- Technical Lead
- Curator Representative