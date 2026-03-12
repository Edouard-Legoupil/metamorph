# Metamorph Database Schema & Data Model

## 1. Overview
Metamorph uses polyglot persistence—PostgreSQL, Neo4j, MinIO, Redis, vector store—so all evidence, claims, entities, graph, and audit are stored with provenance and versioning. This doc contains the canonical relational schema, model conventions, and migration/version guidance.

## 2. PostgreSQL Logical Schema (Summary)

- **core.documents**: source docs (immutable, versioned)
- **content.markdown_documents**: normalized artifact metadata
- **content.sections**: structured section tree
- **content.chunks**: extractor- and retrieval-ready chunks
- **knowledge.evidence_spans**: exact/approximate evidence for claims
- **knowledge.claims**: atomic, evidence-backed claims
- **knowledge.claim_evidence**: m-to-n join claims/evidence
- **knowledge.entities**: canonical and alias registry
- **knowledge.canonical_facts**: accepted knowledge/fact registry
- **review.conflicts**: contradiction/supersession queue
- **review.conflict_claims/conflict_facts**: join tables for conflict identity
- **review.curator_decisions**: reviewed decisions log
- **content.wiki_blocks**: block assembly for wiki/cards
- **audit.events**: immutable audit event log

## 3. Example Table (see full SQL in scripts/init_db.sql)

```
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

## 4. Migration/Versioning Strategy
- All new files are versioned by checksum, lineage, and parent_document_id.
- Schema changes use SQL migration files (e.g. alembic).
- Ontology versions are tracked in claims/facts metadata and graph materialization.
- Extraction/pipeline versions are stored in extraction_json/provenance_json per record.

## 5. Graph Schema (Neo4j)
- **Entity**: all canonical + alias nodes
- **Fact**: accepted facts (with provenance)
- **Conflict**: contradiction links
- **Timeline/Event/Document**: with edges (LOCATED_IN, FUNDS, IMPLEMENTS, etc)
- All graph-backed wiki/knowledge cards retain links to claim/evidence/fact origins.

## 6. Vector Store & Search Schema
- **chunks**: semantic recall of source content
- **claims**: atomic propositions for recall, agentic/QA tasks
- **wiki_blocks**: curated summaries
- **entities**: optional entity profile embeddings

## 7. Minimal Viable Schema Cut
Start with:
- core.documents
- content.markdown_documents
- content.sections
- content.chunks
- knowledge.evidence_spans
- knowledge.claims
- knowledge.claim_evidence
- knowledge.entities
- knowledge.canonical_facts
- review.conflicts
- review.curator_decisions
- audit.events

Other tables can be layered on later. See [PIPELINE.md](./PIPELINE.md) for knowledge/evidence flow; [ARCHITECTURE.md](./ARCHITECTURE.md) for deployment; [CURATION.md](./CURATION.md) for workflow details.