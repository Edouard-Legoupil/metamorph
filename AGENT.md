# AGENT.md — Metamorph: Open-Source, Cloud-Agnostic Knowledge Graph + Wiki Platform

## 🎯 Mission

You are building **Metamorph**: an **open-source, cloud-agnostic knowledge operating system** that converts document collections (PDF, DOCX, HTML, email exports, spreadsheets where relevant) into a **curated, evidence-backed knowledge layer** for human and agentic workflows.

The goal is **not** to build a giant PDF vector tomb. The goal is to create a **reliable, maintainable, explainable knowledge base** composed of:

1. **Canonical source assets** (original documents + normalized Markdown)
2. **Atomic claims and evidence spans** with provenance
3. **An ontology-guided knowledge graph** with temporal and confidence-aware facts
4. **Auto-generated wiki pages / knowledge cards** as the primary curation interface
5. **Hybrid retrieval** (graph + lexical + vector) for downstream assistants and agents
6. **A trusted context assembly layer** for proposal drafting, reporting, policy analysis, and operational support

This platform is intended for **high-trust knowledge environments** such as humanitarian operations, policy, protection, operations planning, research synthesis, donor intelligence, and knowledge management.

The system must support both:

- **Human workflows**: curators, analysts, field staff, reviewers
- **Agentic workflows**: retrieval, reasoning, drafting, monitoring, contradiction surfacing, and card refresh

The platform must be:

- **Fully open source**
- **Cloud agnostic**
- **Deployable on-prem or in any cloud**
- **Model-provider agnostic**
- **Auditable and source-traceable by design**

---

## 🧠 Core Design Thesis

### Metamorph is a knowledge curation system first, and a retrieval system second.

A pure vector store is useful for recall, but insufficient as a long-term source of truth for domains where users need:

- explainability
- provenance
- stable entity definitions
- conflict resolution
- temporal validity
- reusable summaries
- multi-hop reasoning across documents

Therefore, Metamorph uses a **layered architecture**:

```text
Raw documents
  ↓
Structured Markdown + layout metadata
  ↓
Atomic claims + evidence spans + provenance
  ↓
Ontology-guided knowledge graph + entity resolution + conflict detection
  ↓
Auto-generated wiki pages / knowledge cards for curation
  ↓
Hybrid retrieval + query planning + context assembly
  ↓
Human workflows and agentic workflows
```

The **wiki / knowledge card layer** is the primary human interface.
The **graph + evidence layer** is the canonical machine-readable backbone.
The **retrieval layer** is hybrid and query-aware.

---

## 📚 Reference Inputs

All prompts, designs, and code must align with these documents when present:

1. `docs/guide/knowledge-pipeline-blueprint.md`
   - pipeline architecture
   - ingestion, reconciliation, orchestration
   - trust routing
2. `docs/ontology/unhcr-knowledge-ontology.ttl`
   - ontology / schema definition
   - node, edge, and property semantics
3. `docs/guide/knowledge-card.yaml`
   - knowledge card definitions
   - section structure
   - section-level query requirements
4. `AGENT.md` (this document)
   - implementation philosophy
   - system architecture
   - feature scope
   - engineering constraints

If these documents disagree, treat this order of precedence as default unless explicitly instructed otherwise:

1. domain ontology / governance constraints
2. knowledge-card specifications
3. architecture principles in this file
4. local implementation convenience

---

## ✅ Architectural Principles

### 1. Do not treat wiki pages as the canonical store

Wiki pages are **generated and curated views** over the evidence and graph layers.
The canonical store is:

- the original source document
- normalized Markdown / extracted structure
- evidence spans
- atomic claims
- graph entities / relations / facts
- curator decisions / approvals

### 2. Atomic claims are the critical unit of knowledge

A graph triplet alone is not enough.
Every asserted fact must be representable as a **claim with evidence and provenance**.

### 3. Provenance is mandatory

Every knowledge element shown to a user or passed to an agent must be traceable to:

- original source document
- document version / checksum
- page / section / chunk / span reference
- extraction timestamp
- extraction method / model version
- confidence score
- validation status
- curator action history where applicable

### 4. Time is a first-class dimension

Many apparent contradictions are not contradictions but temporal change.
The data model must support:

- `observed_at`
- `valid_from`
- `valid_to`
- `asserted_at`
- `supersedes`
- `status` (proposed, accepted, deprecated, disputed, shadow)

### 5. Hybrid retrieval is required

Do **not** replace all retrieval with graph traversal or all retrieval with embeddings.
Use a **hybrid retrieval stack**:

- lexical / keyword search for exact recall
- vector search for semantic recall
- graph traversal for entity-centric and multi-hop reasoning
- wiki/knowledge-card section retrieval for compact high-trust summaries

### 6. Curation must happen in context

Do not force users to curate raw ingestion artifacts in a separate ops-only dashboard.
The preferred experience is:

- curator works inside wiki / card views
- evidence is visible inline or one click away
- contradictions are shown near affected knowledge blocks
- approvals / edits / merges happen in the reading experience

### 7. Contradiction handling is a workflow, not a boolean

Contradiction detection must include:

- entity resolution
- normalization
- temporal scoping
- source reliability signals
- claim conflict rules
- human resolution queue

### 8. Keep the ontology minimal, versioned, and extensible

Use a strict ontology for high-value stable concepts, but preserve escape hatches for:

- weakly typed claims
- unknown relation candidates
- schema evolution
- ontology review proposals

---

## 🏗 System Layers

## Layer 0 — Source of Record Layer

Stores immutable source assets and source metadata.

### Inputs
- PDF
- DOCX
- HTML
- TXT / Markdown
- CSV / XLSX where relevant
- email exports / archives where relevant
- manually curated notes where governance permits

### Responsibilities
- upload and version source files
- compute checksums
- store MIME metadata
- preserve original filenames / origin
- classify document type
- manage retention and version lineage

### Requirements
- object storage must be open-source and S3-compatible where possible
- files are never stored in the graph database
- document versioning is explicit

---

## Layer 1 — Document Normalization Layer

Transforms source files into structured, evidence-ready textual representations.

### Objective
Convert documents into **normalized Markdown + structural metadata** while preserving layout-aware references.

### Outputs
- normalized Markdown
- section tree
- chunk boundaries
- page references
- table extraction artifacts
- OCR confidence where relevant
- layout metadata
- image / figure references if needed

### Principles
- Markdown is the primary human-readable normalized format
- structure-aware chunking is preferred over naive fixed chunking
- chunks should preserve section titles and semantic boundaries
- original layout references must remain addressable

---

## Layer 2 — Evidence and Claim Layer

This is one of the most important layers in the system.

### Objective
Transform normalized content into **atomic claims** anchored to evidence spans.

### Why this layer exists
A knowledge graph without claim-level evidence becomes hard to audit and curate.
A wiki without evidence becomes fragile.
A contradiction system without atomic claims is noisy.

### Claim model (conceptual)

```json
{
  "claim_id": "uuid",
  "claim_type": "relation|attribute|event|classification|summary_statement",
  "subject": {
    "label": "Donor",
    "id": "uuid-or-null",
    "name": "USAID"
  },
  "predicate": "FUNDS",
  "object": {
    "label": "FundingInstrument",
    "id": "uuid-or-null",
    "name": "2024 Humanitarian Implementation Plan"
  },
  "qualifiers": {
    "amount": "10000000",
    "currency": "USD",
    "country": "Sudan"
  },
  "temporal": {
    "observed_at": "2025-02-01",
    "valid_from": "2025-01-01",
    "valid_to": null
  },
  "provenance": {
    "document_id": "uuid",
    "document_version": "sha256:...",
    "page": 14,
    "section_path": ["Funding", "Donor Commitments"],
    "chunk_id": "uuid",
    "span_start": 802,
    "span_end": 948,
    "raw_text": "USAID will fund the 2024 Humanitarian Implementation Plan...",
    "extractor": "claim-extractor-v3",
    "extractor_model": "local-llm-name",
    "extracted_at": "2026-03-11T10:00:00Z"
  },
  "confidence": {
    "claim_confidence": 0.97,
    "entity_link_confidence": 0.91,
    "temporal_confidence": 0.82
  },
  "status": "proposed"
}
```

### Important rule
Triplets are useful, but **claims must remain richer than triplets**.
Claims may later materialize into graph facts, wiki summaries, alerts, or card blocks.

---

## Layer 3 — Knowledge Graph Layer

### Objective
Represent normalized, reconciled knowledge as a graph over a versioned ontology.

### Graph contents
- canonical entities
- aliases
- relations
- typed attributes
- events
- document references
- evidence nodes / references
- contradiction records
- curator decisions
- temporal edges and status markers

### Graph principles
- ontology-guided extraction where possible
- property graph model is acceptable
- store both canonicalized facts and unresolved candidates
- preserve links back to claims / evidence
- support graph traversal, neighborhood expansion, and community summarization

### Critical distinction
The graph is **not** the only truth layer.
The graph stores structured knowledge, but the evidence / claim layer preserves the auditable basis for that knowledge.

---

## Layer 4 — Curation and Wiki Layer

### Objective
Generate **human-friendly entity- and concept-centric pages** from the graph and evidence layers.

### Main outputs
- entity wiki pages
- topic wiki pages
- event timeline pages
- operational dashboards / knowledge cards
- contradiction views
- stale knowledge alerts

### Design philosophy
The wiki is where knowledge becomes usable.
It is the preferred interface for:

- reviewing summaries
- editing accepted narratives
- validating pending facts
- inspecting evidence
- resolving contradictions
- maintaining card quality

### Every wiki block should support
- block provenance
- confidence / verification badge
- “show evidence” action
- “show graph context” action
- “propose edit” action
- “resolve contradiction” action when relevant

---

## Layer 5 — Retrieval Layer

### Objective
Provide query-aware retrieval for both users and agents.

### Retrieval modalities
1. **Lexical retrieval**
   - exact phrase recall
   - acronym / code recall
   - policy identifiers
2. **Vector retrieval**
   - semantic recall over chunks, evidence, and wiki sections
3. **Graph retrieval**
   - entity neighborhood traversal
   - relation paths
   - event and timeline exploration
4. **Wiki-section retrieval**
   - concise, curated, high-value summaries
5. **Hybrid reranking**
   - score fusion across modalities

### Mandatory principle
Do not rely on a single retrieval mode.
Different query classes require different retrieval plans.

---

## Layer 6 — Context Assembly Layer

### Objective
Assemble the minimum high-quality context required for an agentic task.

### Example task types
- proposal drafting
- country brief generation
- policy change detection
- stakeholder mapping
- contradiction review support
- knowledge-card refresh
- entity profile generation
- answer generation with citations

### Context assembly strategy
1. classify task / question intent
2. determine retrieval mode(s)
3. retrieve candidate evidence, graph neighborhoods, and curated sections
4. rerank for relevance and trust
5. assemble compact context with provenance
6. expose citations and confidence to the generation layer

### Rule
Do **not** dump whole wiki pages or large document chunks into prompts unless explicitly necessary.
Retrieve **targeted sections, claims, and evidence**.

---

## 🌐 Open-Source, Cloud-Agnostic Technology Stack

Use fully open-source components wherever possible and avoid hard dependencies on proprietary APIs or vendor-managed services.

### Backend API
- **FastAPI (Python 3.11+)**
  - async support
  - OpenAPI generation
  - Pydantic v2 validation

### Workflow / Task Orchestration
- **Celery + Redis** for asynchronous jobs
- keep orchestration replaceable

### Graph Database
- **Neo4j Community Edition** 
  - use property graph semantics
  - choose one via adapter abstraction
- all graph operations must go through a repository/service layer
- avoid hard-coding vendor-specific procedures where possible

### Relational Store / Metadata Store
- **PostgreSQL 15+**
  - document metadata
  - claims table(s)
  - curation state
  - audit logs
  - background job metadata

### Vector Search
- **pgvector** (default as simplicity matters)

### Full-Text / Hybrid Search
- PostgreSQL FTS for simpler deployments

### Object Storage
- **MinIO** in development and self-hosted production by default
- must remain compatible with any S3-compatible object store

### Wiki / Curation UI
Preferred default:
- **Wiki.js** for lightweight wiki publishing

Alternative if tighter custom control is required:
- custom React wiki workspace backed by the Metamorph API

### Frontend
- **React 18 + TypeScript**
- **Vite**
- **TailwindCSS**
- **shadcn/ui**
- **TanStack Query**
- **Zustand** for light UI state

### Model Serving / AI Gateway (fully open source)

- **LiteLLM**  used only as an internal abstraction layer iallowing to configure both cloud and self-hosted open models.

### Embeddings / Reranking
- **sentence-transformers** for embeddings
- **bge / e5 / multilingual-e5 / jina embeddings** where appropriate
- **cross-encoder rerankers** or **bge-reranker** for reranking

### NLP / Information Extraction
- **spaCy**
- **GLiNER** for NER or mention detection where relevant
- **sentence-transformers** / local LLMs for extraction assistance
- optional **Apache Tika** for broad file ingestion fallback

### Entity Resolution
- use a pluggable entity resolution service
- preferred approach: a local resolution pipeline combining aliases, lexical similarity, embedding similarity, graph context, and deterministic domain rules
- if `GLinker` or another component is used, keep it optional and abstracted

### PDF / Document Processing
Primary tools:
- **Docling** for structured document conversion
- **PyMuPDF** for lightweight layout analysis
- **pytesseract** and/or **EasyOCR** for OCR fallback
- **pdfplumber** / **camelot** / **tabula-py** for tables where needed
- **pandoc / pypandoc** for broad document conversion fallback

Optional escalation parser:
- **MinerU** may be used if it is available under acceptable open-source terms and operationally suitable
- if not, implement escalation via Docling + OCR/table/layout fallback stack

### Containerization / Deployment
- **Docker + Docker Compose** for development
- **Kubernetes + Helm** for production
- **Terraform** modules may be provided for multiple clouds, but the application must run fully on self-managed infrastructure

### Observability
- **Prometheus**
- **Grafana**
- **OpenTelemetry**
- **Loki** or ELK/OpenSearch for logs

### Auth / Access Control
- OpenID Connect compatible identity layer
- self-hosted IdP preferred (e.g. **Keycloak**)

---

## 📄 Ingestion and Parsing Strategy

## Objective
Convert source documents into high-quality normalized Markdown and extraction artifacts with maximum traceability and minimum silent failure.

### Parsing pipeline

```text
Source Document
  → file registration + checksum + metadata extraction
  → lightweight layout analysis
  → parser routing
  → OCR fallback when needed
  → Markdown normalization
  → section tree + chunks + tables + references
  → quality checks
  → evidence-ready chunk package
```

### Parser strategy

#### Tier 1: Structure-aware primary parser
- Docling by default
- used for most reports, updates, policies, concept notes, briefs

#### Tier 2: Fallback / escalation stack
- OCR fallback for scanned or low-text pages
- table extraction fallback
- alternative markdown conversion path
- optional MinerU if operationally validated and license-compatible

### Layout analysis routing signals
- page count
- text density
- scanned-page ratio
- table density
- multi-column likelihood
- image / figure density
- extraction confidence from prior runs

### Hard rule
No parser may silently “succeed” if the resulting document has catastrophic quality loss.
Quality checks must detect:
- empty sections
- broken reading order
- missing tables where expected
- repeated OCR noise
- extremely low text yield

### Result package
Each processed document must produce a package such as:

```json
{
  "document_id": "uuid",
  "document_version": "sha256:...",
  "markdown_path": "...",
  "sections": [...],
  "chunks": [...],
  "tables": [...],
  "layout_metadata": {...},
  "ocr_metadata": {...},
  "quality_report": {...}
}
```

---

## 🧩 Chunking Strategy

### Principle
Use **semantic and structure-aware chunking**, not arbitrary fixed-length chunking alone.

### Preferred chunk characteristics
- retains section title / heading path
- keeps paragraphs semantically coherent
- preserves table references
- includes parent context in metadata
- remains small enough for embedding / extraction efficiency

### Chunk metadata must include
- `chunk_id`
- `document_id`
- `document_version`
- `page_start`, `page_end`
- `section_path`
- `char_start`, `char_end`
- `content_type` (paragraph, table, caption, list, title)
- `parent_heading`
- extraction quality flags

---

## 🧠 Claim Extraction Strategy

### Goal
Produce **high-precision claims** suitable for downstream reconciliation, not just maximal recall.

### Extraction modes
1. deterministic extraction where possible
2. local-LLM-assisted extraction for relations / events / summaries
3. schema-guided extraction aligned with ontology
4. fallback weak extraction for unknown concepts

### Claim categories
- entity existence / typing
- attribute assertions
- relation assertions
- event assertions
- temporal assertions
- quantitative assertions
- policy / obligation assertions
- summary statements (explicitly marked as summaries, not raw facts)

### Extraction safeguards
- retain raw evidence
- store extractor prompt / template version where relevant
- separate extraction confidence from truth confidence
- do not collapse uncertain claims into accepted graph facts automatically

---

## 🔗 Entity Resolution and Canonicalization

### Objective
Resolve mentions into canonical entities while preserving ambiguity where unresolved.

### Resolution stages
1. string normalization and alias matching
2. ontology/type constraints
3. geographic / organizational / domain-specific rules
4. embedding similarity
5. graph-context-assisted disambiguation
6. human escalation for ambiguous cases

### Important rule
If confidence is insufficient, keep the mention unresolved or shadow-linked.
Do not force canonicalization.

### Canonical entity record should support
- canonical name
- aliases
- language variants
- external IDs
- type history / confidence
- merge / split history
- provenance count

---

## ⚖️ Reconciliation and Contradiction Detection

### Objective
Decide how incoming claims relate to existing accepted knowledge.

### Possible outcomes
- **confirmation**: supports existing accepted knowledge
- **expansion**: adds new compatible knowledge
- **update**: supersedes an older fact
- **contradiction**: conflicts with accepted or pending knowledge
- **duplicate**: semantically identical claim already exists
- **insufficient evidence**: cannot be safely integrated

### Contradiction detection stack
Contradiction detection is not a single classifier.
It must combine:

1. **entity resolution quality**
2. **value normalization**
   - currencies
   - units
   - dates
   - naming conventions
3. **temporal scoping**
4. **source ranking / trust weighting**
5. **schema-aware conflict rules**
6. **claim similarity / entailment checks**
7. **human review**

### Examples of conflict classes
- direct numeric contradiction
- temporal supersession
- classification mismatch
- geographic scope mismatch
- duplicate with differing source granularity
- relation polarity conflict
- summary-level inconsistency

### Conflict record fields
- conflict ID
- affected claim IDs
- affected graph entities
- severity
- conflict class
- rationale
- candidate resolution suggestions
- reviewer state
- audit log

---

## 🚦 Trust Routing and Review Workflow

### Objective
Route new knowledge to the appropriate level of automation and review.

### Suggested routing tiers

#### 🟢 Auto-Accept
Criteria:
- very high extraction confidence
- high entity-link confidence
- no contradiction
- trusted source class
- relation type eligible for auto-accept

Action:
- materialize claim into accepted graph fact
- regenerate impacted wiki blocks
- mark as machine-accepted

#### 🟡 Shadow / Pending
Criteria:
- moderate confidence
- ambiguous canonicalization
- low-risk relation class
- soft contradiction or stale fact concern

Action:
- show in wiki with pending badge or shadow state where governance allows
- queue for curator verification
- do not overwrite accepted fact silently

#### 🔴 Human Escalation
Criteria:
- strong contradiction
- low confidence
- high-impact domain
- ontology ambiguity
- policy / legal / protection sensitivity

Action:
- block automated materialization
- open review task
- notify responsible curation lane

### Note
Shadow knowledge must be clearly distinguishable from accepted knowledge.

---

## 📚 Wiki / Knowledge Card Design

### Objective
Turn graph-backed knowledge into maintainable, user-friendly, evidence-backed pages.

### Page families
- Key entity pages based on knowledge-card templates (KC-1..KC-6)

### Page construction principles
- generated from templates and block definitions
- blocks query graph + claim + evidence layers
- narrative sections can be curated
- structured sections should remain machine-refreshable
- each block must expose freshness and provenance

### Block types
- canonical fact block
- metric / trend block
- timeline block
- relationship map block
- summary block
- contradiction banner block
- evidence table block
- stale knowledge alert block

### Curation actions
- accept pending claim
- reject pending claim
- merge conflicting claims into curated statement
- mark accepted summary as stale
- create editorial note
- split entity
- merge entity
- propose ontology extension

### Hard rule
Do not treat generated narrative as self-authenticating truth.
Generated narrative must remain linked to evidence and curator status.

---

## 🔍 Search and Retrieval Features

### Search modes
- document search
- chunk search
- claim search
- entity search
- wiki search
- contradiction search
- temporal search
- neighborhood search

### Hybrid retrieval flow

```text
User / agent query
  → query classification
  → retrieval plan
     ├─ lexical search
     ├─ vector search
     ├─ graph traversal
     └─ wiki-section retrieval
  → score fusion / reranking
  → context assembly
  → response / downstream task
```

### Retrieval objects that may be returned
- source documents
- markdown chunks
- atomic claims
- graph subgraphs
- wiki sections
- contradiction records
- evidence bundles

---

## 🤖 Agentic Interfaces

### Objective
Expose curated knowledge to agents without forcing them to reason over raw PDFs by default.

### Interfaces
- REST API
- optional GraphQL API
- MCP-compatible server for agent tooling
- bulk export for offline pipelines

### Agent-facing capabilities
- retrieve entity profile with accepted facts + pending flags
- retrieve evidence bundle for a claim
- retrieve timeline of changes
- retrieve contradiction set for an entity
- generate compact context pack for a task
- retrieve knowledge card sections by template ID

### Required response metadata
Every agent-facing answer bundle should include:
- source references
- confidence
- validation status
- timestamps
- retrieval method summary
- truncation / summarization indicators if applicable

---

## 🏷 Data Model Concepts

## Core records

### Document
- immutable source metadata
- storage path
- checksum
- version lineage
- processing status

### Chunk
- normalized text fragment with structure and offsets

### EvidenceSpan
- exact or near-exact segment supporting a claim

### Claim
- atomic proposition with provenance and confidence

### CanonicalFact
- accepted / curated graph-materialized fact

### Entity
- canonical node with alias and provenance history

### ConflictRecord
- structured representation of contradiction or supersession concern

### WikiBlock
- renderable knowledge unit tied to queries and evidence

### CuratorDecision
- acceptance / rejection / edit / merge / deprecate action with audit trail

---

## 📁 Suggested Project Structure

```text
metamorph/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── documents.py
│   │   │   │   │   ├── claims.py
│   │   │   │   │   ├── entities.py
│   │   │   │   │   ├── facts.py
│   │   │   │   │   ├── conflicts.py
│   │   │   │   │   ├── cards.py
│   │   │   │   │   ├── wiki.py
│   │   │   │   │   ├── search.py
│   │   │   │   │   ├── retrieval.py
│   │   │   │   │   └── mcp.py
│   │   │   │   └── dependencies.py
│   │   │   └── __init__.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   ├── logging.py
│   │   │   ├── exceptions.py
│   │   │   └── telemetry.py
│   │   ├── models/
│   │   │   ├── documents.py
│   │   │   ├── chunks.py
│   │   │   ├── evidence.py
│   │   │   ├── claims.py
│   │   │   ├── entities.py
│   │   │   ├── facts.py
│   │   │   ├── conflicts.py
│   │   │   ├── cards.py
│   │   │   └── wiki.py
│   │   ├── services/
│   │   │   ├── ingestion/
│   │   │   │   ├── file_registry.py
│   │   │   │   ├── layout_analyzer.py
│   │   │   │   ├── parser_router.py
│   │   │   │   ├── docling_wrapper.py
│   │   │   │   ├── ocr_pipeline.py
│   │   │   │   ├── markdown_normalizer.py
│   │   │   │   └── quality_checks.py
│   │   │   ├── chunking/
│   │   │   │   ├── section_chunker.py
│   │   │   │   └── chunk_metadata.py
│   │   │   ├── extraction/
│   │   │   │   ├── claim_extractor.py
│   │   │   │   ├── ontology_guided_extractor.py
│   │   │   │   ├── evidence_linker.py
│   │   │   │   ├── confidence_scorer.py
│   │   │   │   └── summary_extractor.py
│   │   │   ├── resolution/
│   │   │   │   ├── entity_resolver.py
│   │   │   │   ├── alias_registry.py
│   │   │   │   └── canonicalizer.py
│   │   │   ├── reconciliation/
│   │   │   │   ├── delta_engine.py
│   │   │   │   ├── conflict_classifier.py
│   │   │   │   ├── supersession_engine.py
│   │   │   │   └── trust_router.py
│   │   │   ├── graph/
│   │   │   │   ├── graph_repository.py
│   │   │   │   ├── fact_materializer.py
│   │   │   │   ├── graph_queries.py
│   │   │   │   └── graph_summaries.py
│   │   │   ├── wiki/
│   │   │   │   ├── block_assembler.py
│   │   │   │   ├── page_templates.py
│   │   │   │   ├── wikijs_client.py
│   │   │   │   └── freshness_service.py
│   │   │   ├── retrieval/
│   │   │   │   ├── lexical_search.py
│   │   │   │   ├── vector_search.py
│   │   │   │   ├── graph_retrieval.py
│   │   │   │   ├── hybrid_search.py
│   │   │   │   ├── reranker.py
│   │   │   │   └── context_assembler.py
│   │   │   ├── agents/
│   │   │   │   ├── proposal_agent.py
│   │   │   │   ├── card_refresh_agent.py
│   │   │   │   └── contradiction_review_agent.py
│   │   │   └── audit/
│   │   │       └── audit_log_service.py
│   │   ├── worker/
│   │   │   ├── celery_app.py
│   │   │   ├── tasks_ingestion.py
│   │   │   ├── tasks_extraction.py
│   │   │   ├── tasks_reconciliation.py
│   │   │   └── tasks_wiki.py
│   │   └── main.py
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   ├── e2e/
│   │   └── fixtures/
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Upload/
│   │   │   ├── Review/
│   │   │   ├── Wiki/
│   │   │   ├── Cards/
│   │   │   ├── Search/
│   │   │   ├── Conflicts/
│   │   │   └── Evidence/
│   │   ├── hooks/
│   │   ├── lib/
│   │   ├── pages/
│   │   ├── state/
│   │   └── types/
│   ├── package.json
│   └── Dockerfile
├── infrastructure/
│   ├── docker-compose.yml
│   ├── helm/
│   ├── terraform/
│   └── monitoring/
├── docs/
│   ├── adr/
│   ├── ontology/
│   ├── api/
│   ├── user-guide/
│   └── examples/
├── scripts/
│   ├── bootstrap_dev.sh
│   ├── seed_ontology.py
│   ├── rebuild_wiki.py
│   └── reindex_vectors.py
└── AGENT.md
```

---

## 🔄 End-to-End Workflows

## 1. Document-to-Knowledge Workflow

```text
Upload document
  → register source + checksum + storage path
  → analyze layout
  → parse to Markdown
  → quality checks
  → structure-aware chunking
  → claim extraction + evidence linking
  → entity resolution
  → reconciliation against accepted knowledge
      ├─ confirmation
      ├─ expansion
      ├─ supersession/update
      ├─ contradiction
      └─ insufficient evidence
  → trust routing
      ├─ auto-accept
      ├─ shadow/pending
      └─ human escalation
  → materialize accepted facts to graph
  → regenerate impacted wiki blocks / cards
  → refresh retrieval indexes
  → emit audit events / alerts
```

## 2. Knowledge Card Refresh Workflow

```text
Scheduled or triggered refresh
  → detect stale blocks / updated facts / new contradictions
  → recompute card sections from graph + accepted claims
  → preserve editorial sections where required
  → attach freshness markers
  → publish updated draft or accepted version based on governance
```

## 3. Conflict Resolution Workflow

```text
Conflict detected
  → create ConflictRecord
  → classify severity and scope
  → route to appropriate curator lane
  → show current accepted fact, proposed fact, evidence, timeline
  → curator action
      ├─ accept new fact
      ├─ reject new claim
      ├─ merge into curated statement
      ├─ mark as temporal supersession
      ├─ split/merge entity
      └─ escalate
  → update graph / wiki / audit logs
  → notify downstream subscriptions where relevant
```

## 4. Agent Context Assembly Workflow

```text
Agent task request
  → classify intent
  → choose retrieval strategy
  → retrieve claims / wiki sections / graph neighborhoods / evidence
  → rerank and compress
  → build context pack with citations and confidence
  → send to generation component
  → persist task trace if enabled
```

---

## 🧪 Testing Strategy

### Unit tests
- parser routing logic
- markdown normalization
- chunking behavior
- claim extraction schema validation
- evidence linking correctness
- entity resolution scoring
- conflict classification
- trust routing rules
- wiki block assembly
- retrieval fusion logic

### Integration tests
- source upload to graph materialization
- PDF parsing with representative fixtures
- OCR fallback behavior
- graph reconciliation with seeded ontology
- wiki generation from accepted facts
- retrieval across lexical, vector, and graph channels

### End-to-end tests
- upload a new document
- process claims
- review pending conflict
- approve / reject
- verify wiki update
- verify search and agent retrieval output

### Evaluation tests
In addition to software tests, implement **knowledge quality evaluation**:
- extraction precision / recall on gold datasets
- entity resolution accuracy
- contradiction false positive rate
- citation completeness rate
- average time-to-curation
- context usefulness for target agent tasks

---

## 📏 Success Metrics

The system is successful when:

### Knowledge quality
- accepted facts remain evidence-backed and auditable
- contradiction false positives are manageable
- entity duplication decreases over time
- stale or superseded knowledge is surfaced quickly

### User workflow
- curators work primarily in the wiki / card interface
- reviewers can resolve most issues without reopening raw PDFs immediately
- field staff can trust the visible verification status and provenance

### Agent workflow
- agents retrieve concise high-value context instead of raw document dumps
- answers include source references and confidence information
- proposal drafting and card refresh workflows accelerate materially

### Operational quality
- ingestion failures are observable and recoverable
- reprocessing is deterministic and version-aware
- stack runs fully on self-managed infrastructure

---

## 🔐 Security, Governance, and Audit

### Requirements
- role-based access control
- tenant / workspace separation where relevant
- immutable audit logs for curation actions
- model invocation logs where policy permits
- document access controls propagated to retrieval results
- redaction / restricted-content handling if required by domain

### Auditability
Every important action must be traceable:
- upload
- parsing
- extraction
- entity resolution
- acceptance / rejection
- wiki publication
- agent retrieval bundle creation

---

## 🔧 Engineering Standards

### Python
- Python 3.11+
- formatting: `black`
- linting: `ruff`
- imports: `isort`
- typing: `mypy --strict`
- dependency management: `uv` or Poetry acceptable

### TypeScript
- strict mode enabled
- ESLint + Prettier
- avoid `any`

### API conventions
- async-first endpoints
- typed schemas everywhere
- explicit error types
- idempotent reprocessing endpoints where possible

### Coding standards
- public functions require docstrings
- comments explain **why**, not **what**
- avoid hard-coded vendor assumptions
- all infrastructure bindings must be adapter-based where realistic

---

## 🧯 Common Pitfalls to Avoid

1. **Treating the graph as the only source of truth**
   - the evidence and claim layers matter just as much
2. **Treating wiki pages as canonical data storage**
   - wiki is a curation and presentation layer
3. **Dropping provenance during normalization or summarization**
   - if a statement cannot be traced, it should not become trusted knowledge
4. **Overwriting accepted facts without reconciliation**
   - always reconcile through update / contradiction workflows
5. **Ignoring time**
   - many conflicts are temporal, not factual disagreements
6. **Relying on a single retrieval mode**
   - hybrid retrieval is required
7. **Forcing entity resolution in ambiguous cases**
   - unresolved is better than wrong
8. **Allowing generated summaries to drift away from evidence**
   - summaries must remain anchored and refreshable
9. **Using proprietary model providers as a hard dependency**
   - self-hosted open-source inference is the default assumption
10. **Building a system that only ingestion engineers can operate**
   - curators need a humane wiki-centric workflow

---

## 🚀 Phased Implementation Roadmap

## Phase 0 — Foundations
- source registration
- document storage
- ontology load
- graph adapter
- PostgreSQL metadata schema
- authentication / authorization
- observability baseline

## Phase 1 — Document normalization
- parser routing
- Markdown normalization
- chunking
- OCR fallback
- parsing quality reports

## Phase 2 — Claim and evidence extraction
- claim schema
- evidence linking
- confidence scoring
- initial ontology-guided extraction

## Phase 3 — Entity resolution and reconciliation
- canonicalization
- delta engine
- contradiction detection
- trust routing
- fact materialization

## Phase 4 — Wiki and knowledge cards
- page templates
- wiki block assembler
- card rendering
- inline evidence and review actions

## Phase 5 — Hybrid retrieval and agent interfaces
- lexical/vector/graph retrieval
- reranking
- context assembler
- MCP / agent APIs

## Phase 6 — Evaluation and optimization
- knowledge quality benchmarks
- latency and cost optimization
- curation UX refinement
- governance hardening

---

## 🧾 Example Environment Variables

```bash
# Core services
APP_ENV=development
API_HOST=0.0.0.0
API_PORT=8000

# PostgreSQL
POSTGRES_DSN=postgresql://metamorph:metamorph@postgres:5432/metamorph

# Redis
REDIS_URL=redis://redis:6379/0

# Graph
GRAPH_BACKEND=neo4j
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=change-me

# Object storage
S3_ENDPOINT=http://minio:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=metamorph-documents
S3_REGION=us-east-1

# Vector search
VECTOR_BACKEND=pgvector
QDRANT_URL=http://qdrant:6333

# Search
SEARCH_BACKEND=postgres
OPENSEARCH_URL=http://opensearch:9200

# Wiki
WIKI_BACKEND=wikijs
WIKIJS_URL=http://wikijs:3000
WIKIJS_API_KEY=change-me

# Identity
OIDC_ISSUER_URL=http://keycloak:8080/realms/metamorph
OIDC_CLIENT_ID=metamorph
OIDC_CLIENT_SECRET=change-me

# Model serving (self-hosted)
LLM_BACKEND=vllm
VLLM_BASE_URL=http://vllm:8001
OLLAMA_BASE_URL=http://ollama:11434
EMBEDDING_MODEL=multilingual-e5-large
RERANK_MODEL=bge-reranker-large

# OCR / parsing
TESSERACT_LANGS=eng+fra+ara

# Telemetry
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
```

---

## 📘 Documentation Requirements

### Required documentation
- ADRs for major architecture decisions
- ontology documentation
- claim schema documentation
- conflict resolution playbook
- card template specification
- retrieval strategy guide
- operator runbooks
- curator user guide

### ADR examples
- graph backend choice
- vector backend choice
- wiki integration strategy
- self-hosted model serving strategy
- contradiction routing policy

---

## ✅ Final Implementation Rules

1. Build for **trust, traceability, and maintainability**, not just ingestion throughput.
2. Preserve the distinction between **raw source**, **evidence**, **claims**, **facts**, and **wiki views**.
3. Keep the system **open-source and cloud-agnostic by default**.
4. Prefer **self-hosted open models** and pluggable inference abstractions.
5. Use the **wiki / knowledge-card layer as the human curation interface**.
6. Use **hybrid retrieval** for all serious downstream agentic workflows.
7. Treat contradiction resolution as a **first-class product capability**.
8. Never lose provenance.
9. Never silently overwrite accepted knowledge.
10. Optimize for a future in which the curated wiki / card layer becomes the trusted operational context for humans and agents alike.
