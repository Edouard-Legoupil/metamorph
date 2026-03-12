# Database and Schema Blueprint

## Overview

Metamorph uses **polyglot persistence** because no single database is ideal for all workloads.

### Storage responsibilities
- **Object storage (MinIO / S3 compatible)**: raw source files, normalized Markdown, large artifacts
- **Graph DB (Neo4j CE / Memgraph)**: canonical entity graph, accepted facts, graph traversal, contradiction graph patterns
- **PostgreSQL**: system-of-record for documents, chunks, claims, evidence spans, curation, jobs, audit
- **Vector store ( pgvector)**: embeddings for chunks, claims, wiki sections, entity profiles
- **Search index (PostgreSQL FTS)**: lexical retrieval and hybrid scoring support

---

## 1. PostgreSQL logical schema

### Schema namespaces
- `core` — documents, jobs, users, workspaces
- `content` — chunks, markdown sections, tables, wiki blocks
- `knowledge` — claims, evidence spans, canonical fact registry, alias registry
- `review` — conflicts, review tasks, decisions, annotations
- `audit` — immutable audit events
- `retrieval` — cached retrieval packs, rerank traces, prompt/context traces

---

## 2. Core relational entities

## 2.1 `core.documents`

Stores source document metadata.

```sql
create table if not exists core.documents (
  document_id uuid primary key,
  workspace_id uuid not null,
  source_uri text,
  original_filename text not null,
  media_type text not null,
  checksum_sha256 text not null,
  storage_bucket text not null,
  storage_key text not null,
  source_type text not null,
  language_code text,
  ingestion_status text not null,
  version_no integer not null default 1,
  parent_document_id uuid,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (workspace_id, checksum_sha256)
);
```

### Notes
- store a new row for materially distinct file versions
- use `parent_document_id` to preserve lineage
- do not store the full file blob in PostgreSQL

---

## 2.2 `content.markdown_documents`

Stores normalized Markdown references and document-level quality metadata.

```sql
create table if not exists content.markdown_documents (
  markdown_id uuid primary key,
  document_id uuid not null references core.documents(document_id),
  storage_bucket text not null,
  storage_key text not null,
  parser_name text not null,
  parser_version text,
  ocr_used boolean not null default false,
  quality_score numeric(5,4),
  quality_flags jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);
```

---

## 2.3 `content.sections`

Represents the structured section tree of a normalized document.

```sql
create table if not exists content.sections (
  section_id uuid primary key,
  markdown_id uuid not null references content.markdown_documents(markdown_id),
  parent_section_id uuid references content.sections(section_id),
  heading_level integer,
  heading_text text,
  ordinal integer not null,
  page_start integer,
  page_end integer,
  section_path text[] not null,
  char_start integer,
  char_end integer,
  created_at timestamptz not null default now()
);
```

---

## 2.4 `content.chunks`

Stores structure-aware chunks used for extraction and retrieval.

```sql
create table if not exists content.chunks (
  chunk_id uuid primary key,
  document_id uuid not null references core.documents(document_id),
  section_id uuid references content.sections(section_id),
  chunk_type text not null,
  content_text text not null,
  page_start integer,
  page_end integer,
  char_start integer,
  char_end integer,
  token_estimate integer,
  parent_heading text,
  section_path text[] not null,
  quality_flags jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);
```

Recommended indexes:

```sql
create index if not exists idx_chunks_document on content.chunks(document_id);
create index if not exists idx_chunks_section_path on content.chunks using gin (section_path);
create index if not exists idx_chunks_fts on content.chunks using gin (to_tsvector('simple', content_text));
```

---

## 2.5 `knowledge.evidence_spans`

Stores exact or approximate evidence ranges supporting a claim.

```sql
create table if not exists knowledge.evidence_spans (
  evidence_id uuid primary key,
  document_id uuid not null references core.documents(document_id),
  chunk_id uuid references content.chunks(chunk_id),
  page_no integer,
  span_start integer,
  span_end integer,
  raw_text text not null,
  capture_method text not null,
  confidence numeric(5,4),
  created_at timestamptz not null default now()
);
```

---

## 2.6 `knowledge.claims`

Stores atomic claims before and after reconciliation.

```sql
create table if not exists knowledge.claims (
  claim_id uuid primary key,
  workspace_id uuid not null,
  document_id uuid not null references core.documents(document_id),
  claim_type text not null,
  subject_surface text not null,
  predicate text not null,
  object_surface text,
  value_json jsonb,
  qualifiers_json jsonb not null default '{}'::jsonb,
  temporal_json jsonb not null default '{}'::jsonb,
  provenance_json jsonb not null default '{}'::jsonb,
  extraction_json jsonb not null default '{}'::jsonb,
  confidence_json jsonb not null default '{}'::jsonb,
  status text not null default 'proposed',
  canonical_subject_id uuid,
  canonical_object_id uuid,
  canonical_fact_id uuid,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
```

Recommended indexes:

```sql
create index if not exists idx_claims_document on knowledge.claims(document_id);
create index if not exists idx_claims_status on knowledge.claims(status);
create index if not exists idx_claims_predicate on knowledge.claims(predicate);
create index if not exists idx_claims_subject on knowledge.claims(canonical_subject_id);
create index if not exists idx_claims_object on knowledge.claims(canonical_object_id);
create index if not exists idx_claims_qualifiers_gin on knowledge.claims using gin (qualifiers_json);
```

---

## 2.7 `knowledge.claim_evidence`

Many-to-many link table between claims and evidence spans.

```sql
create table if not exists knowledge.claim_evidence (
  claim_id uuid not null references knowledge.claims(claim_id),
  evidence_id uuid not null references knowledge.evidence_spans(evidence_id),
  role text not null default 'supporting',
  primary key (claim_id, evidence_id)
);
```

---

## 2.8 `knowledge.entities`

Relational registry for canonical entities and aliases.

```sql
create table if not exists knowledge.entities (
  entity_id uuid primary key,
  entity_type text not null,
  canonical_name text not null,
  display_name text,
  external_ids_json jsonb not null default '{}'::jsonb,
  alias_json jsonb not null default '[]'::jsonb,
  status text not null default 'active',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
```

---

## 2.9 `knowledge.canonical_facts`

Stores accepted or curated fact registry for governance, even if the graph DB is the primary traversal engine.

```sql
create table if not exists knowledge.canonical_facts (
  canonical_fact_id uuid primary key,
  fact_type text not null,
  subject_entity_id uuid not null references knowledge.entities(entity_id),
  predicate text not null,
  object_entity_id uuid references knowledge.entities(entity_id),
  value_json jsonb,
  qualifiers_json jsonb not null default '{}'::jsonb,
  temporal_json jsonb not null default '{}'::jsonb,
  status text not null default 'accepted',
  source_count integer not null default 0,
  supersedes_fact_id uuid references knowledge.canonical_facts(canonical_fact_id),
  last_reviewed_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
```

---

## 2.10 `review.conflicts`

Contradiction and supersession queue.

```sql
create table if not exists review.conflicts (
  conflict_id uuid primary key,
  workspace_id uuid not null,
  conflict_class text not null,
  severity text not null,
  status text not null default 'open',
  rationale text,
  candidate_resolution_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  resolved_at timestamptz
);
```

Supporting link tables:

```sql
create table if not exists review.conflict_claims (
  conflict_id uuid not null references review.conflicts(conflict_id),
  claim_id uuid not null references knowledge.claims(claim_id),
  side text,
  primary key (conflict_id, claim_id)
);

create table if not exists review.conflict_facts (
  conflict_id uuid not null references review.conflicts(conflict_id),
  canonical_fact_id uuid not null references knowledge.canonical_facts(canonical_fact_id),
  side text,
  primary key (conflict_id, canonical_fact_id)
);
```

---

## 2.11 `review.curator_decisions`

Tracks human decisions.

```sql
create table if not exists review.curator_decisions (
  decision_id uuid primary key,
  workspace_id uuid not null,
  actor_id uuid not null,
  decision_type text not null,
  target_type text not null,
  target_id uuid not null,
  payload_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);
```

---

## 2.12 `content.wiki_blocks`

Represents rendered or renderable card/wiki sections.

```sql
create table if not exists content.wiki_blocks (
  block_id uuid primary key,
  page_key text not null,
  block_type text not null,
  title text,
  render_state text not null default 'draft',
  source_query_json jsonb not null default '{}'::jsonb,
  content_markdown text,
  freshness_json jsonb not null default '{}'::jsonb,
  provenance_json jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);
```

---

## 2.13 `audit.events`

Immutable audit log.

```sql
create table if not exists audit.events (
  event_id uuid primary key,
  workspace_id uuid,
  actor_id uuid,
  event_type text not null,
  target_type text,
  target_id uuid,
  payload_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);
```

Recommended index:

```sql
create index if not exists idx_audit_target on audit.events(target_type, target_id);
```

---

## 3. Graph database blueprint

## 3.1 Graph modeling philosophy

Use the graph database for:
- entity-centric traversal
- accepted fact relationships
- temporal relationship patterns
- contradiction neighborhoods
- graph-based summary preparation

Do **not** use the graph DB as the only store for provenance-rich claim data.

---

## 3.2 Node labels

### Core labels
- `Entity`
- `Person`
- `Organization`
- `Location`
- `Country`
- `Operation`
- `Policy`
- `Project`
- `FundingInstrument`
- `PopulationGroup`
- `Event`
- `Document`
- `CanonicalFact`
- `Conflict`
- `KnowledgeCard`

### Common node properties
- `id`
- `type`
- `name`
- `status`
- `created_at`
- `updated_at`
- `confidence`
- `workspace_id`

---

## 3.3 Relationship types

Examples:
- `LOCATED_IN`
- `FUNDS`
- `IMPLEMENTS`
- `AFFECTS`
- `AUTHORED_BY`
- `REFERENCED_IN`
- `EVIDENCED_BY`
- `SUPERSEDES`
- `CONTRADICTS`
- `HAS_ALIAS`
- `MENTIONED_IN`
- `IN_COUNTRY`
- `RELATES_TO`

### Relationship properties
- `canonical_fact_id`
- `valid_from`
- `valid_to`
- `observed_at`
- `status`
- `confidence`
- `source_count`

---

## 3.4 Example graph materialization pattern

### Entity nodes
```cypher
MERGE (s:Entity {id: $subject_entity_id})
  ON CREATE SET s.name = $subject_name, s.type = $subject_type, s.created_at = datetime()
SET s.updated_at = datetime();

MERGE (o:Entity {id: $object_entity_id})
  ON CREATE SET o.name = $object_name, o.type = $object_type, o.created_at = datetime()
SET o.updated_at = datetime();
```

### Canonical fact edge
```cypher
MATCH (s:Entity {id: $subject_entity_id})
MATCH (o:Entity {id: $object_entity_id})
MERGE (s)-[r:FUNDS {canonical_fact_id: $canonical_fact_id}]->(o)
SET r.status = 'accepted',
    r.valid_from = $valid_from,
    r.valid_to = $valid_to,
    r.confidence = $confidence,
    r.source_count = $source_count,
    r.updated_at = datetime();
```

### Evidence link
```cypher
MERGE (d:Document {id: $document_id})
MERGE (f:CanonicalFact {id: $canonical_fact_id})
MERGE (f)-[:REFERENCED_IN]->(d);
```

---

## 4. Vector schema blueprint

## 4.1 Collections / indices

### `chunks`
Use for semantic recall of source content.

Payload fields:
- `chunk_id`
- `document_id`
- `workspace_id`
- `section_path`
- `page_start`
- `page_end`
- `chunk_type`
- `status`

### `claims`
Use for retrieving atomic propositions.

Payload fields:
- `claim_id`
- `predicate`
- `claim_type`
- `canonical_subject_id`
- `canonical_object_id`
- `status`

### `wiki_blocks`
Use for retrieving concise curated summaries.

Payload fields:
- `block_id`
- `page_key`
- `block_type`
- `verification_state`
- `freshness_state`

### `entities`
Optional profile embeddings for entity-centric recall.

Payload fields:
- `entity_id`
- `entity_type`
- `canonical_name`
- `alias_list`

---

## 5. Search blueprint

### Lexical search
Index:
- documents
- chunks
- claims
- wiki blocks

Recommended fields:
- title / heading
- content text
- aliases
- entity names
- tags / ontology types

### Hybrid ranking heuristic
A simple initial scoring function may fuse:
- lexical score
- vector similarity
- graph prior score
- freshness prior
- verification prior

Example:

```text
final_score =
  0.30 * lexical_score +
  0.30 * vector_score +
  0.20 * graph_score +
  0.10 * freshness_score +
  0.10 * verification_score
```

Tune later with real tasks.

---

## 6. State transitions

## Claims
- `proposed`
- `accepted`
- `shadow`
- `disputed`
- `rejected`
- `deprecated`

## Conflicts
- `open`
- `under_review`
- `resolved_accept_new`
- `resolved_keep_current`
- `resolved_merge`
- `escalated`
- `dismissed`

## Wiki blocks
- `draft`
- `rendered`
- `published`
- `stale`
- `shadow_visible`

---

## 7. Migration and versioning strategy

### Documents
- new checksum → new document row
- optionally link lineage via `parent_document_id`

### Ontology
- version ontology explicitly
- store ontology version in claims, facts, and graph materialization metadata

### Parsing / extraction models
- persist parser version, extractor version, prompt or template version where relevant
- allow reprocessing by version

---

## 8. Recommended implementation order

1. PostgreSQL core tables
2. object storage integration
3. chunking and evidence tables
4. claims and evidence linking
5. entity registry and canonical facts
6. conflict tables and decision logs
7. graph materialization adapter
8. vector indexing pipelines
9. wiki blocks and retrieval traces

---

## 9. Minimal viable schema cut

If you need the leanest possible first version, start with:
- `core.documents`
- `content.markdown_documents`
- `content.sections`
- `content.chunks`
- `knowledge.evidence_spans`
- `knowledge.claims`
- `knowledge.claim_evidence`
- `knowledge.entities`
- `knowledge.canonical_facts`
- `review.conflicts`
- `review.curator_decisions`
- `audit.events`

Everything else can be layered on incrementally.
