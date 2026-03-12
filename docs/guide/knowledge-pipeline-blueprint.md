
# Knowledge Pipeline Blueprint
## From Document-Centric Storage to a Living, Evidence-Backed Knowledge System

**Version:** 1.0 — Technical Specification  
**Purpose:** Build specification for an open-source, cloud-agnostic, agent-ready knowledge platform  
**Architecture:** Layered pipeline — Source Registration → Normalization → Claims & Evidence → Reconciliation → Knowledge Graph → Wiki/Cards → Hybrid Retrieval → Agent Context Assembly

---

## Table of Contents
1. [System Overview](#1-system-overview)
2. [Architecture Principles](#2-architecture-principles)
3. [End-to-End Pipeline](#3-end-to-end-pipeline)
4. [Component A: Source Registration & Document Normalization](#4-component-a-source-registration--document-normalization)
5. [Component B: Claims, Evidence, and Entity Resolution](#5-component-b-claims-evidence-and-entity-resolution)
6. [Component C: Reconciliation, Contradictions, and Trust Routing](#6-component-c-reconciliation-contradictions-and-trust-routing)
7. [Component D: Knowledge Graph and Canonical Facts](#7-component-d-knowledge-graph-and-canonical-facts)
8. [Component E: Wiki, Knowledge Cards, and Human Curation](#8-component-e-wiki-knowledge-cards-and-human-curation)
9. [Component F: Search, Retrieval, and Agent Interfaces](#9-component-f-search-retrieval-and-agent-interfaces)
10. [Data Models & Schemas](#10-data-models--schemas)
11. [Interfaces & UX Requirements](#11-interfaces--ux-requirements)
12. [Trust, Verification, and Governance Logic](#12-trust-verification-and-governance-logic)
13. [Open-Source & Cloud-Agnostic Deployment Constraints](#13-open-source--cloud-agnostic-deployment-constraints)
14. [Success Criteria](#14-success-criteria)

---

## 1. System Overview

### 1.1 Core Transformation
The platform evolves knowledge through **seven successive operational layers**:

| Layer | Representation | Description | Primary Mode |
|---|---|---|---|
| **Layer 0** | Source of Record | Original documents, immutable metadata, file lineage | Controlled storage |
| **Layer 1** | Normalized Documents | Markdown, sections, chunks, tables, layout metadata | Structured parsing |
| **Layer 2** | Claims & Evidence | Atomic claims linked to exact evidence spans and provenance | Auditable extraction |
| **Layer 3** | Reconciled Knowledge | Accepted, disputed, shadow, and superseded facts | Controlled reconciliation |
| **Layer 4** | Knowledge Graph | Canonical entities, relations, events, timelines, conflict links | Active linking |
| **Layer 5** | Wiki / Knowledge Cards | Human-friendly pages generated from graph + claims + evidence | Active synthesis |
| **Layer 6** | Retrieval & Agent Context | Hybrid retrieval and compact context packs for humans and agents | Query-aware reasoning |

### 1.2 Operating Principle
The system operates as a **listener and continuously updating curator**: as soon as a new document is published or uploaded, the pipeline triggers automatically, processes the document into normalized artifacts, extracts evidence-backed claims, reconciles them against accepted knowledge, and updates the relevant wiki pages, knowledge cards, search indexes, and agent interfaces according to trust-routing rules.

### 1.3 Key Design Challenge
The knowledge graph alone is not the single source of truth, nor the wiki a canonical store. Instead, the platform distinguishes clearly between:

- **Raw source documents**
- **Normalized Markdown and chunk structure**
- **Atomic claims with evidence and provenance**
- **Canonical facts and graph materialization**
- **Wiki pages and knowledge cards as curated views**
- **Hybrid retrieval artifacts for downstream agents**

### 1.4 Design Thesis
The goal is **not** to build a large PDF vector store. The goal is to build a **reliable, maintainable, explainable, evidence-backed knowledge layer** that is easier for people to curate and safer for agentic systems to consume.

### 1.5 Downstream Outputs
- **Curated wiki and knowledge-card layer:** the primary operational interface for humans
- **Hybrid retrieval layer:** graph + lexical + vector + wiki-block retrieval
- **Agent context endpoint:** compact, cited context packs for downstream agents
- **MCP endpoint:** Model Context Protocol server exposing trusted knowledge resources and tools
- **Evaluation artifacts:** datasets for measuring extraction, resolution, contradiction detection, and retrieval quality
- **Optional model training datasets:** only from validated or curator-approved knowledge artifacts

---

## 2. Architecture Principles

### 2.1 Claims, Not Raw Triplets, Are the Critical Unit
Triplets remain useful, but **triplets alone are insufficient** for a high-trust knowledge system. The critical operational unit is the **claim**, which must include:

- subject / predicate / object or typed value
- qualifiers
- temporal scope
- evidence span(s)
- document provenance
- extraction metadata
- confidence scores
- resolution state
- review / verification state

### 2.2 Provenance Is Mandatory
Every claim, fact, wiki block, and agent response must be traceable to:

- original source document
- document version / checksum
- page / section / chunk / span reference
- extraction method and version
- extraction timestamp
- confidence scores
- verification status
- curator decision history where applicable

### 2.3 Time Is a First-Class Concept
Many apparent contradictions are actually temporal updates. The data model must support:

- `observed_at`
- `valid_from`
- `valid_to`
- `asserted_at`
- `supersedes`
- explicit fact and claim status values

### 2.4 The Wiki Is a Curated View, Not the Canonical Store
Wiki pages and knowledge cards are **generated and curated projections** over the graph, claims, and evidence layers. They must never become the only storage location for accepted knowledge.

### 2.5 The Graph Is a Backbone, Not the Entire Truth Layer
The graph stores canonicalized, traversable knowledge. However, the **auditable basis** for that knowledge remains the claims and evidence layers.

### 2.6 Retrieval Must Remain Hybrid
The system must combine:

- **Lexical retrieval** for exact recall and identifiers
- **Vector retrieval** for semantic recall
- **Graph retrieval** for entity-centric and multi-hop reasoning
- **Wiki-block retrieval** for concise, curated summaries

### 2.7 Contradiction Handling Is a Workflow, Not a Boolean
Contradictions cannot be detected reliably with a single rule. The system must combine:

- entity resolution quality
- normalization of values and units
- temporal scoping
- source weighting
- ontology-aware rules
- human review for ambiguous or high-impact cases

### 2.8 Curation Must Happen in Context
The system should avoid pushing users into a separate ingestion-only admin console for routine decisions. Curation should happen primarily:

- inside wiki pages
- inside knowledge cards
- inside lightweight validation queues
- with evidence and provenance available inline or one click away

---

## 3. End-to-End Pipeline

```text
Source Document
  → file registration + checksum + version lineage
  → layout analysis + parser routing
  → Markdown normalization + structure extraction
  → semantic / structure-aware chunking
  → claim extraction + evidence linking
  → entity resolution + canonicalization
  → reconciliation against accepted facts
      ├─ confirmation
      ├─ expansion
      ├─ update / supersession
      ├─ contradiction
      └─ insufficient evidence
  → trust routing
      ├─ auto-accept
      ├─ shadow / pending
      └─ human escalation
  → graph materialization of accepted facts
  → wiki / knowledge-card block regeneration
  → lexical / vector / graph retrieval refresh
  → agent context assembly and MCP exposure
```

---

## 4. Component A: Source Registration & Document Normalization

### 4.1 Purpose
Transform heterogeneous source files into **normalized, evidence-ready Markdown artifacts** while preserving traceability to the original source.

### 4.2 Source-of-Record Model
The source-of-record layer stores:

- original files (PDF, DOCX, HTML, Markdown, optionally spreadsheets or email exports)
- immutable metadata
- checksums
- lineage between versions
- source URI where applicable
- access controls and storage location

### 4.3 Parsing Strategy
All downstream extraction must be **Markdown-first**.

#### 4.3.1 Routing Logic
```text
IF document layout is standard (prose, headings, simple tables)
  → route to Docling
ELSE IF document has high table density, multi-column layout, or high layout complexity
  → route to MinerU or equivalent escalation parser
ELSE IF text extraction is poor or scan-heavy
  → OCR fallback + normalization pipeline
```

#### 4.3.2 Parser Specifications

| Parser | Use Case | Output |
|---|---|---|
| **Docling** | Standard reports, policies, briefs, situation updates | Markdown preserving heading hierarchy and tables |
| **MinerU** | Complex layouts, dense tables, multi-column pages, embedded charts | Markdown with structural annotations |
| **OCR fallback** | Scan-heavy or image-first documents | Recoverable text plus confidence and layout flags |

### 4.4 Layout Analysis Signals
Before routing, the system evaluates:

- page count
- text density
- scanned-page ratio
- table density
- multi-column probability
- image / figure density
- estimated parsing complexity score

### 4.5 Quality Checks
A parser is **not considered successful** if the resulting Markdown suffers catastrophic loss. Quality checks must flag:

- empty or near-empty sections
- broken reading order
- repeated OCR noise
- suspiciously low text yield
- missing tables where layout suggests tables exist
- page/section mismatches

### 4.6 Output Artifacts
Each processed document produces:

- normalized Markdown
- section tree
- chunk set
- table artifacts where relevant
- layout metadata
- OCR metadata where used
- parsing quality report

---

## 5. Component B: Claims, Evidence, and Entity Resolution

### 5.1 Purpose
Convert normalized Markdown into **atomic claims** linked to evidence spans and candidate canonical entities.

### 5.2 Atomic Extraction Model
Each parsed document is decomposed into **claims**, which may later be rendered as triplets or attributes in the graph.

#### 5.2.1 Claim Categories
Claims may represent:

- entity typing or existence
- relation assertions
- quantitative values
- qualitative classifications
- events
- policy / normative statements
- summary statements (explicitly marked as summaries)

#### 5.2.2 Claim Schema (Conceptual)
```json
{
  "claim_id": "uuid",
  "claim_type": "relation|attribute|event|classification|summary_statement",
  "subject": { "label": "NodeType", "id": "string|null", "name": "string" },
  "predicate": "EDGE_TYPE_OR_ATTRIBUTE",
  "object": { "label": "NodeType", "id": "string|null", "name": "string|null" },
  "value": null,
  "qualifiers": {},
  "temporal": {
    "observed_at": null,
    "valid_from": null,
    "valid_to": null
  },
  "provenance": {
    "source_document_id": "string",
    "source_document_title": "string",
    "document_version": "sha256-or-version-id",
    "page_reference": 0,
    "section_path": ["Heading 1", "Heading 2"],
    "chunk_id": "string",
    "span_start": 0,
    "span_end": 0,
    "raw_text_snippet": "string",
    "extracted_at": "ISO8601 timestamp",
    "extractor_name": "string",
    "extractor_version": "string"
  },
  "confidence": {
    "claim_confidence": 0.0,
    "entity_resolution_confidence": 0.0,
    "temporal_confidence": 0.0
  },
  "status": "PROPOSED"
}
```

### 5.3 Evidence Layer
Claims must link to one or more **evidence spans**. The evidence layer stores:

- exact or approximate text span
- document and chunk references
- page number
- capture method
- evidence confidence if approximate

### 5.4 Entity Resolution
Use **GLinker or equivalent entity disambiguation/resolution tooling** to:

- map mentions to canonical entities
- score candidate matches
- register new entities when confidence is sufficient and policy allows
- preserve unresolved or ambiguous mentions when confidence is insufficient

### 5.5 Resolution Rules
- Do **not** force canonicalization when ambiguity remains high
- Preserve aliases and language variants
- Maintain merge / split history for canonical entities
- Record the confidence and features used for resolution

---

## 6. Component C: Reconciliation, Contradictions, and Trust Routing

### 6.1 Purpose
Transform a growing collection of claims into a **controlled and explainable source of truth** by comparing incoming claims against accepted facts and routing differences appropriately.

### 6.2 Delta Engine Outcomes
When a new claim arrives, the reconciliation engine resolves it to one of the following outcomes:

```text
NEW CLAIM, NO RELEVANT FACT → EXPANSION
Action: Candidate for new fact creation

MATCHING CLAIM, SAME MEANING / VALUE → CONFIRMATION
Action: Increase support/source count. No visible content change required

MATCHING CLAIM, NEWER OR TIME-SCOPED DIFFERENCE → UPDATE / SUPERSESSION
Action: Create supersession candidate, do not silently overwrite

MATCHING CLAIM, DIFFERENT VALUE / MEANING → CONTRADICTION
Action: Create ConflictRecord and route by severity

LOW EVIDENCE OR LOW RESOLUTION QUALITY → INSUFFICIENT_EVIDENCE
Action: Queue for review without materializing as accepted knowledge
```

### 6.3 Contradiction Detection Stack
Contradictions are detected using a combination of:

- subject / predicate / object matching
- entity resolution confidence
- value normalization (units, dates, currencies, identifiers)
- temporal reasoning
- source trust weighting
- ontology-aware conflict rules
- semantic similarity / entailment checks where appropriate

### 6.4 Conflict Types
| Conflict Type | Description |
|---|---|
| **QUANTITATIVE** | Numeric or metric disagreement |
| **NORMATIVE** | Policy, legal, or obligation disagreement |
| **CONTACT** | Named person / contact detail disagreement |
| **STRUCTURAL** | Hierarchy, ownership, governance, or supersession mismatch |
| **TEMPORAL** | Conflicts that may be explainable as time-bounded changes |
| **CLASSIFICATION** | Category or typing disagreement |

### 6.5 ConflictRecord Schema
```json
{
  "conflict_id": "uuid",
  "subject": "entity_id",
  "predicate": "EDGE_TYPE_OR_ATTRIBUTE",
  "existing_value": { "object": "...", "source": "document_id", "date": "..." },
  "incoming_value": { "object": "...", "source": "document_id", "date": "..." },
  "conflict_type": "QUANTITATIVE|NORMATIVE|CONTACT|STRUCTURAL|TEMPORAL|CLASSIFICATION",
  "severity": "CRITICAL|MINOR",
  "status": "UNRESOLVED|UNDER_REVIEW|RESOLVED|ACKNOWLEDGED|DISMISSED",
  "assigned_to_tier": 1,
  "rationale": "string",
  "candidate_resolution": "string|null"
}
```

### 6.6 Trust Routing Outcomes
The routing decision depends on:

- extraction confidence
- entity resolution confidence
- contradiction type and severity
- source trust class
- ontology/domain policy

#### 6.6.1 Routing Tiers
| Tier | Label | Trigger Condition | Action |
|---|---|---|---|
| 🟢 **Auto-Accept** | Green | High confidence, no contradiction, eligible schema/domain | Materialize accepted fact, regenerate graph/wiki, mark machine-accepted |
| 🟡 **Shadow Update** | Yellow | Moderate confidence, low-risk delta, soft contradiction, or ambiguous but plausible update | Show pending or shadow state where policy allows, queue for review |
| 🔴 **Human Escalation** | Red | Low confidence, strong contradiction, new sensitive entity, policy/legal/protection impact | Block automated materialization, open review task |

### 6.7 Important Rule
The system must **never silently overwrite accepted knowledge**. All updates to accepted knowledge must pass through reconciliation and, where needed, review.

---

## 7. Component D: Knowledge Graph and Canonical Facts

### 7.1 Purpose
Represent reconciled knowledge in a **versioned, ontology-guided graph** suitable for traversal, synthesis, and downstream agentic reasoning.

### 7.2 Data Model — Labeled Property Graph (LPG)
The graph stores:

- canonical entities
- aliases
- accepted facts
- typed relations
- events
- document references
- contradiction links
- supersession links
- knowledge-card anchors where useful

### 7.3 Canonical Fact Model
A **canonical fact** is the accepted, graph-materialized form of one or more supporting claims. It must retain:

- canonical subject and object or value
- predicate / attribute
- qualifiers
- temporal scope
- source count
- review state
- link back to supporting claims and source documents

### 7.4 Graph Materialization Rules
- Only **accepted** or explicitly **shadow-visible** knowledge may be rendered into graph-backed user surfaces
- Keep links to supporting claims and documents
- Preserve `SUPERSEDES` edges where applicable
- Preserve unresolved contradictions separately instead of collapsing them

### 7.5 Graph Use Cases
The graph is used for:

- entity neighborhood retrieval
- multi-hop reasoning
- timeline synthesis
- graph-backed card sections
- community or thematic summarization
- contradiction neighborhood exploration

---

## 8. Component E: Wiki, Knowledge Cards, and Human Curation

### 8.1 Purpose
Convert graph-backed knowledge into **human-readable, evidence-backed, maintainable wiki pages and knowledge cards**.

### 8.2 Wiki Structure
The wiki is the human-readable projection of the knowledge system and is composed of three functional layers.

#### 8.2.1 Living Knowledge Layer
- Wiki pages are assembled from **Blocks**, where each block is a projection over graph facts, claims, evidence, or a combination of these
- Blocks are refreshed from the latest accepted state and may display pending or disputed content when policy allows
- Users should rarely need to consult raw PDFs first; they should be able to start from the wiki and drill down into evidence only when needed

**Page assembly rule:** Each block declares one or more source queries (graph, claim, evidence, retrieval), and the wiki engine uses these at render time or refresh time.

#### 8.2.2 Conflict Resolution Layer
When an unresolved `ConflictRecord` exists, the wiki must **display both positions with context**, not silently hide one. For example:

```text
⚠️ CONFLICT DETECTED
Global Policy (HQ SOP 2024) states: Shelter Ratio = 1:20
Regional Guidance (Field Report Q3 2025) states: Shelter Ratio = 1:15
Scope note: Regional guidance applies to Cox's Bazar operations only
Status: Pending human review — assigned to Regional Focal Point
```

#### 8.2.3 Deep Reference Trace
Every wiki paragraph or block must support a **View Original / Show Evidence** affordance:

- exact Markdown snippet from the normalized source
- direct link to original PDF or source file
- document title and version
- page number and section path
- claim/fact identifiers
- confidence score and extraction date

### 8.3 Knowledge Cards
Knowledge cards are structured page types built from templates. Each card section:

- declares a retrieval or graph query
- can mix machine-refreshable and editor-curated content
- must preserve provenance and freshness information
- may include contradiction banners and pending badges

### 8.4 Curation Interface Design
Curation is broken into **micro-tasks** delivered through two channels.

#### 8.4.1 Atomic Validation Cards
```text
📋 VALIDATION REQUIRED
The 2026 Emergency Report states:
  Shelter Ratio in Camp X = 1:15
Current accepted value:
  Shelter Ratio in Camp X = 1:20 [source: 2024 Field Assessment]
[ ✅ Approve Update ] [ ❌ Reject ] [ ✏️ Merge/Edit ] [ ⬆ Escalate ]
```

#### 8.4.2 In-Wiki Curation
Do not rely only on a separate curation dashboard. Embed curation into reading:

- each machine-generated or pending block can expose **[Verify]**, **[Reject]**, **[Edit]**, or **[Resolve Conflict]** actions
- verification should clear or update machine/pending markers according to policy
- this transforms routine reading into lightweight quality control

### 8.5 Hierarchy of Trust — Tiered Curation
```text
Tier 0 — AI
 Scope: Bulk ingestion, auto-accept decisions, shadow updates under policy

Tier 1 — Field Data / Domain Focal Point
 Scope: Operational data, local entities, field statistics, contact updates

Tier 2 — Regional Focal Point
 Scope: Regional SOPs, strategy documents, regional contradictions, sensitive cross-country issues

Tier 3 — Thematic / HQ Authority
 Scope: Global policy, legal/normative conflicts, high-impact governance decisions
```

---

## 9. Component F: Search, Retrieval, and Agent Interfaces

### 9.1 Purpose
Expose curated knowledge to both humans and agents without forcing them to reason over raw PDFs by default.

### 9.2 Retrieval Modes
The platform must support:

- **Document search**
- **Chunk search**
- **Claim search**
- **Entity search**
- **Wiki-block search**
- **Conflict search**
- **Timeline / temporal retrieval**
- **Graph neighborhood retrieval**

### 9.3 Hybrid Retrieval Strategy
The retrieval layer must combine:

- lexical search over chunks, claims, wiki blocks, and entity names
- vector search over chunks, claims, wiki blocks, and optionally entities
- graph traversal for entity-centric and multi-hop tasks
- wiki-block retrieval for concise, curated context
- reranking / score fusion

### 9.4 Context Assembly for Agents
For downstream agentic use, the system must:

1. classify the task or query intent
2. choose the relevant retrieval mode(s)
3. retrieve candidate evidence, claims, graph neighborhoods, and wiki sections
4. rerank results by relevance, trust, and freshness
5. assemble a compact context pack with citations and verification metadata

### 9.5 MCP Endpoint (Agentic Access)
The knowledge platform must be exposed as a **Model Context Protocol (MCP) server** with at minimum the following tools or equivalent capabilities:

| Tool Name | Description |
|---|---|
| `get_entity` | Retrieve an entity profile with facts, edges, and verification state |
| `search_knowledge` | Hybrid search over verified and pending knowledge artifacts |
| `get_conflicts` | Retrieve unresolved or filtered ConflictRecords |
| `get_document_claims` | Return all claims extracted from a given document |
| `get_wiki_page` | Return rendered Markdown for a wiki page by ID or slug |
| `get_evidence_bundle` | Return supporting evidence for a claim, fact, or wiki block |
| `get_context_pack` | Build compact, cited context for a downstream task |

---

## 10. Data Models & Schemas

### 10.1 Document Record
```json
{
  "document_id": "uuid",
  "title": "string",
  "source_url": "string",
  "published_date": "ISO8601",
  "ingested_at": "ISO8601",
  "document_version": "sha256-or-version-id",
  "parser_used": "docling|mineru|ocr_fallback",
  "markdown_path": "string",
  "status": "REGISTERED|INGESTED|NORMALIZED|EXTRACTED|RECONCILED|ARCHIVED",
  "claim_count": 0,
  "conflict_count": 0,
  "quality_report": {}
}
```

### 10.2 Canonical Entity
```json
{
  "entity_id": "uuid",
  "label": "Operation|Policy|Sector|PopulationGroup|Location|Document|Organization|Person|Event",
  "name": "string",
  "aliases": ["string"],
  "created_at": "ISO8601",
  "last_updated": "ISO8601",
  "source_documents": ["document_id"],
  "verification_status": "AUTO_ACCEPTED|PENDING|HUMAN_VERIFIED|COMMUNITY_VERIFIED|DISPUTED",
  "community_trust_score": 0,
  "merge_history": []
}
```

### 10.3 Canonical Fact
```json
{
  "canonical_fact_id": "uuid",
  "subject_entity_id": "uuid",
  "predicate": "EDGE_TYPE_OR_ATTRIBUTE",
  "object_entity_id": "uuid|null",
  "value": null,
  "qualifiers": {},
  "temporal": {
    "valid_from": null,
    "valid_to": null,
    "observed_at": null
  },
  "verification_status": "AUTO_ACCEPTED|PENDING|HUMAN_VERIFIED|COMMUNITY_VERIFIED|DISPUTED",
  "source_claim_ids": ["claim_id"],
  "source_count": 0,
  "supersedes_fact_id": null
}
```

### 10.4 Wiki Block
```json
{
  "block_id": "uuid",
  "page_id": "uuid",
  "block_type": "FACT|STATISTIC|POLICY_SUMMARY|CONTACT|PROCEDURE|TIMELINE|ALERT",
  "source_queries": ["Cypher or equivalent query string"],
  "rendered_content": "string (Markdown)",
  "source_claim_ids": ["claim_id"],
  "source_fact_ids": ["canonical_fact_id"],
  "verification_status": "AUTO|PENDING|VERIFIED|DISPUTED",
  "last_rendered": "ISO8601",
  "freshness": {"state": "fresh|stale|aging"},
  "active_conflict_ids": ["conflict_id"]
}
```

---

## 11. Interfaces & UX Requirements

### 11.1 Wiki Page — Required UI Elements
| Element | Behaviour |
|---|---|
| Block content | Rendered from graph / claims / evidence queries |
| 🤖 icon | Present on auto-accepted, unverified blocks |
| ⚠️ Conflict banner | Displayed when active conflicts exist |
| ⚠️ Pending badge | Displayed on shadow/pending content |
| [Verify] button | Available to authorized users to validate content |
| [Resolve Conflict] button | Opens conflict review workflow |
| [View Original] / [Show Evidence] | Opens normalized snippet + PDF/source link + metadata |
| Freshness indicator | Shows stale/aging/fresh state |

### 11.2 Curation Queue — Required Columns
| Column | Description |
|---|---|
| Conflict ID | Unique identifier |
| Type | QUANTITATIVE / NORMATIVE / CONTACT / STRUCTURAL / TEMPORAL / CLASSIFICATION |
| Severity | CRITICAL / MINOR |
| Current Value | Existing accepted value + source |
| Proposed Value | Incoming value + source |
| Assigned Tier | 1 / 2 / 3 |
| Scope / Context | Temporal, geographic, or policy scope note |
| Actions | Approve / Reject / Edit / Merge / Escalate |

### 11.3 Agent Response Contract
Any agent-facing response must include:

- answer or retrieved context
- source references
- confidence and verification state
- timestamps / freshness metadata
- retrieval summary
- truncation or summarization indicators where applicable

---

## 12. Trust, Verification, and Governance Logic

### 12.1 Full Routing Decision Tree
```text
NEW CLAIM ARRIVES
│
├── Is the subject/object resolved with sufficient confidence?
│   ├── NO → 🔴 HUMAN ESCALATION or unresolved-entity queue
│   └── YES
│
├── Does it map to an existing canonical fact candidate?
│   ├── NO → evaluate as EXPANSION
│   │   ├── confidence ≥ 0.95 and policy allows → 🟢 AUTO-ACCEPT
│   │   ├── confidence 0.70–0.95 → 🟡 SHADOW / PENDING
│   │   └── confidence < 0.70 → 🔴 HUMAN ESCALATION
│   │
│   └── YES → Are value / meaning / qualifiers / time equivalent?
│       ├── YES → CONFIRMATION (increment support/source count)
│       └── NO → classify update vs contradiction
│           ├── time-bounded or newer valid fact → UPDATE / SUPERSESSION workflow
│           ├── minor low-risk contradiction → 🟡 SHADOW / PENDING
│           └── critical or sensitive contradiction → 🔴 HUMAN ESCALATION
```

### 12.2 Verification State Machine
```text
[EXTRACTED]
  → (high confidence + policy eligible) → [AUTO_ACCEPTED 🤖]
  → (moderate confidence) → [SHADOW_PENDING ⚠️]
  → (low confidence / sensitive domain) → [ESCALATED 🔴]

[AUTO_ACCEPTED 🤖]
  → (community trust threshold met) → [COMMUNITY_VERIFIED ✅]
  → (human verifies) → [HUMAN_VERIFIED ✅]
  → (contradiction emerges) → [DISPUTED ⚠️]

[SHADOW_PENDING ⚠️]
  → (curator approves) → [HUMAN_VERIFIED ✅]
  → (curator rejects) → [REJECTED]
  → (new evidence strengthens confidence) → [AUTO_ACCEPTED 🤖] or [HUMAN_VERIFIED ✅]

[ESCALATED 🔴]
  → (tier resolves) → [HUMAN_VERIFIED ✅]
  → (tier rejects) → [REJECTED]
```

### 12.3 Community Trust Score
The platform may support **implicit verification** with caution:

```text
IF an authenticated user with appropriate role reads a block
AND does not flag it within a configurable review window
THEN increment CommunityTrustScore
IF CommunityTrustScore ≥ threshold AND no open conflicts exist
THEN content may be promoted from AUTO_ACCEPTED to COMMUNITY_VERIFIED
```

This mechanism must be optional, transparent, and policy-governed.

---

## 13. Open-Source & Cloud-Agnostic Deployment Constraints

### 13.1 Required Design Constraint
The entire platform must be deployable with **open-source software** and remain **cloud agnostic**.

### 13.2 Preferred Stack Constraints
- **Backend API:** FastAPI
- **Relational store:** PostgreSQL
- **Graph DB:** Neo4j Community or equivalent pluggable graph backend
- **Vector store:** pgvector or Qdrant
- **Lexical search:** PostgreSQL FTS or OpenSearch
- **Object storage:** MinIO or any S3-compatible storage
- **Task queue:** Celery + Redis or equivalent open-source worker stack
- **Wiki layer:** Wiki.js or custom React-based wiki workspace
- **Identity:** Keycloak or any OIDC-compatible IdP
- **Model serving:** self-hosted open-source model serving (e.g. Ollama, vLLM, TGI)

### 13.3 Anti-Lock-In Rules
- no mandatory dependence on proprietary cloud services
- no mandatory dependence on proprietary model APIs
- infrastructure must remain replaceable by adapters
- all core knowledge and provenance data must remain exportable

---

## 14. Success Criteria

The system is successful when:

### 14.1 Knowledge Quality
- accepted knowledge remains evidence-backed and auditable
- contradictions are surfaced instead of silently overwritten
- entity duplication decreases over time
- stale or superseded knowledge is clearly marked

### 14.2 Human Workflow Quality
- curators work primarily in the wiki / card experience
- reviewers can inspect evidence without hunting through raw PDFs first
- staff can understand which content is auto-accepted, pending, verified, or disputed

### 14.3 Agent Workflow Quality
- agents receive compact, cited context rather than raw document dumps
- responses expose verification and freshness metadata
- downstream drafting and synthesis become faster and safer

### 14.4 Operational Quality
- pipeline failures are observable and recoverable
- reprocessing is version-aware and deterministic
- stack runs fully on self-managed or any-cloud infrastructure

---

## Final Principle

> The platform is successful when people trust the curated knowledge layer, every accepted statement can be traced to evidence, and agents can consume concise, verified context without relying on brittle raw-document retrieval alone.
