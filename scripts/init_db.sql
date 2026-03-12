-- Metamorph DB Init Script
-- Aggregates all schema from DATABASE_BLUEPRINT.md

-- ==========================
-- == core.documents
-- ==========================
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

-- ==========================
-- == content.markdown_documents
-- ==========================
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

-- ==========================
-- == content.sections
-- ==========================
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

-- ==========================
-- == content.chunks
-- ==========================
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
create index if not exists idx_chunks_document on content.chunks(document_id);
create index if not exists idx_chunks_section_path on content.chunks using gin (section_path);
create index if not exists idx_chunks_fts on content.chunks using gin (to_tsvector('simple', content_text));

-- ==========================
-- == knowledge.evidence_spans
-- ==========================
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

-- ==========================
-- == knowledge.claims
-- ==========================
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
create index if not exists idx_claims_document on knowledge.claims(document_id);
create index if not exists idx_claims_status on knowledge.claims(status);
create index if not exists idx_claims_predicate on knowledge.claims(predicate);
create index if not exists idx_claims_subject on knowledge.claims(canonical_subject_id);
create index if not exists idx_claims_object on knowledge.claims(canonical_object_id);
create index if not exists idx_claims_qualifiers_gin on knowledge.claims using gin (qualifiers_json);

-- ==========================
-- == knowledge.claim_evidence
-- ==========================
create table if not exists knowledge.claim_evidence (
  claim_id uuid not null references knowledge.claims(claim_id),
  evidence_id uuid not null references knowledge.evidence_spans(evidence_id),
  role text not null default 'supporting',
  primary key (claim_id, evidence_id)
);

-- ==========================
-- == knowledge.entities
-- ==========================
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

-- ==========================
-- == knowledge.canonical_facts
-- ==========================
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

-- ==========================
-- == review.conflicts
-- ==========================
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

-- ==========================
-- == review.curator_decisions
-- ==========================
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

-- ==========================
-- == content.wiki_blocks
-- ==========================
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

-- ==========================
-- == audit.events
-- ==========================
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
create index if not exists idx_audit_target on audit.events(target_type, target_id);
