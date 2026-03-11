# Knowledge Pipeline Blueprint

## From Document-Centric Storage to a Living World Brain

**Version:** 1.0 — Structured Technical Specification  
**Purpose:** LLM-ready platform build specification  
**Architecture:** Three-component pipeline — Ingestion → Reconciliation → Orchestration

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Component 1: Ingestion & Extraction](#2-component-1-ingestion--extraction)
3. [Component 2: Knowledge Reconciliation](#3-component-2-knowledge-reconciliation)
4. [Component 3: Orchestration & Curation](#4-component-3-orchestration--curation)
5. [Data Models & Schemas](#5-data-models--schemas)
6. [Interface Specifications](#6-interface-specifications)
7. [Trust & Routing Logic](#7-trust--routing-logic)

---

## 1. System Overview

### 1.1 Core Transformation

The platform evolves knowledge through three successive representations:

| Stage | Model | Description | Mode |
|---|---|---|---|
| **Stage 1** | Document-Centric | Collection of PDFs with human-in-the-loop tagging | Passive storage |
| **Stage 2** | Entity-Centric | Knowledge graph connecting entities via enriched metadata | Active linking |
| **Stage 3** | User-Centric | Wiki pages consolidating information, surfacing confirmation and disagreement | Active synthesis |

### 1.2 Operating Principle

The system operates as a **listener**: as soon as a document is published, the pipeline triggers automatically. This shifts the organisation from *information storage* (passive) to *intelligence synthesis* (active).

### 1.3 Key Design Challenge

A knowledge graph is a **cloud** of interconnected data. A wiki is a **linear** series of human-readable pages. To bridge the two, the platform uses:

- **Template-Based Synthesis** for structured wiki generation from graph data
- **Dynamic Aggregation** for real-time page assembly from latest approved sources
- **Knowledge Delta Analysis** to detect and surface what has changed between document versions

### 1.4 Downstream Outputs

- **Fine-tuning dataset:** Auto-generated high-quality training data for domain-specific LLMs, produced from validated knowledge deltas
- **MCP endpoint:** The knowledge graph is exposed as a Model Context Protocol server, making it available to any agentic system

---

## 2. Component 1: Ingestion & Extraction

### 2.1 Data Model — Labeled Property Graph (LPG)

All extracted knowledge is stored in a **Labeled Property Graph**. This is the canonical internal representation. See other humanitarian-knowledge-ontology.md for the full ontology.



### 2.2 Content Extraction Pipeline

#### 2.2.1 Routing Logic

```
IF document layout is standard (prose, headings, simple tables):
    → route to Docling
ELSE IF document has high table density OR non-standard layout:
    → route to MinerU
```

#### 2.2.2 Parser Specifications

| Parser | Use Case | Output |
|---|---|---|
| **Docling** | Standard documents | Markdown preserving table structures and heading hierarchies |
| **MinerU** | Complex layouts, dense tables, multi-column, embedded charts | Markdown with structural annotations |

**Invariant:** All output from both parsers is **Markdown-first**. This ensures a consistent format for downstream embedding and NLP.

### 2.3 Atomic Extraction — Semantic Triplets

#### 2.3.1 Definition

Each parsed document is decomposed into **Semantic Triplets**:

```
Subject → Predicate → Object
```

Triplets are the atomic unit of the knowledge graph. They enable:
- Contradiction detection (same subject + predicate, different object across documents)
- Deduplication (exact match triplets are collapsed)
- Versioning (timestamp and source document attached to each triplet)

#### 2.3.2 Triplet Schema

```json
{
  "subject": { "label": "NodeType", "id": "string", "name": "string" },
  "predicate": "EDGE_TYPE",
  "object": { "label": "NodeType", "id": "string", "name": "string" },
  "metadata": {
    "source_document_id": "string",
    "source_document_title": "string",
    "extracted_at": "ISO8601 timestamp",
    "extraction_confidence": 0.0–1.0,
    "page_reference": "integer",
    "raw_text_snippet": "string"
  }
}
```

#### 2.3.3 Example Triplets

```
(Camp Alpha) -[HAS_SHELTER_RATIO]-> (1:20)
  source: Emergency Plan 2025, p.14, confidence: 0.97

(Global Protection SOP) -[APPLIES_TO]-> (All UNHCR Operations)
  source: HQ Policy 2024, p.2, confidence: 0.99

(SOP v3) -[SUPERSEDES]-> (SOP v2)
  source: Policy Update Circular, p.1, confidence: 0.95
```

#### 2.3.4 Entity Resolution

Use **GLinker** (or equivalent entity disambiguation tool) to:
- Map extracted entity mentions to canonical graph nodes
- Detect new entities not yet in the graph
- Flag ambiguous entity references for human review

---

## 3. Component 2: Knowledge Reconciliation

### 3.1 Purpose

Transform a messy, growing collection of parsed triplets into a **single source of truth**, solving two distinct problems:

| Problem | Definition | Solution |
|---|---|---|
| **Deduplication** | Prevent the graph from accumulating redundant or conflicting nodes | Delta Engine with triplet comparison |
| **Transcription** | Convert the graph back into clean, human-readable wiki pages | Template-Based Synthesis |

### 3.2 Delta Engine

When a new document is parsed into triplets, the engine runs a comparison against existing graph state. Each triplet resolves to one of three outcomes:

```
NEW TRIPLET → outcome: EXPANSION
  Action: Add new node/edge to graph. Flag as 🤖 machine-generated.

EXISTING TRIPLET, SAME VALUE → outcome: CONFIRMATION
  Action: Increment source count. No wiki change.

EXISTING TRIPLET, DIFFERENT VALUE → outcome: CONTRADICTION
  Action: Do NOT overwrite. Create a ConflictRecord. Route to human review.
```

#### 3.2.1 ConflictRecord Schema

```json
{
  "conflict_id": "uuid",
  "subject": "entity_id",
  "predicate": "EDGE_TYPE",
  "existing_value": { "object": "...", "source": "document_id", "date": "..." },
  "incoming_value": { "object": "...", "source": "document_id", "date": "..." },
  "conflict_type": "QUANTITATIVE | NORMATIVE | CONTACT | STRUCTURAL",
  "severity": "CRITICAL | MINOR",
  "status": "UNRESOLVED | RESOLVED | ACKNOWLEDGED",
  "assigned_to_tier": 1 | 2 | 3
}
```

### 3.3 Wiki Structure

The wiki is the human-readable projection of the knowledge graph. It is composed of three functional layers.

#### 3.3.1 The Living Knowledge Layer

- Wiki pages are assembled from **Blocks**, where each Block is a projection of one or more graph nodes/triplets
- When a new publication is approved and its triplets validated, the relevant Block updates automatically
- Users never read raw PDFs; they read synthesised, sourced, up-to-date wiki pages

**Page assembly rule:** Each Block declares a graph query. The wiki engine runs that query at render time and populates the Block with the latest approved data.

#### 3.3.2 The Conflict Resolution Layer

When a `ConflictRecord` exists for a given triplet and is unresolved, the wiki **displays both truths**:

```
⚠️  CONFLICT DETECTED

Global Policy (HQ SOP 2024) states: Shelter Ratio = 1:20
Regional Guidance (Field Report Q3 2025) states: Shelter Ratio = 1:15 
                                                  [for Cox's Bazar operations]

Status: Pending human review — assigned to Regional Focal Point
```

This prevents silent overwriting of knowledge and makes disagreement visible to users.

#### 3.3.3 The Deep Reference Trace

Every paragraph on every wiki page exposes a **"View Original"** affordance:

- Clicking opens the exact Markdown snippet from the source file
- Includes a direct link to the original PDF hosted on the document server
- Triplet metadata (confidence score, extraction date, page number) is visible

---

## 4. Component 3: Orchestration & Curation

### 4.1 Design Principle — Uncertainty-Driven Exception Model

The goal is to move away from "Review Everything" toward a model where:
- The AI handles **90%** of routine knowledge updates autonomously
- Humans are only engaged for the **10%** of high-stakes or ambiguous cases

### 4.2 Three-Tier Routing System

The routing decision is based on the AI's **self-assessed extraction confidence** and the **type of knowledge change detected**.

#### 4.2.1 Routing Tiers

| Tier | Label | Trigger Condition | Action |
|---|---|---|---|
| 🟢 **Auto-Accept** | Green | Confidence ≥ 95% AND entity resolved via GLinker AND data matches expected schema | Immediately expand or update Graph + Wiki. Add 🤖 icon. |
| 🟡 **Shadow Update** | Yellow | Confidence 70–95% OR minor delta (e.g. statistic changed ≤ 10%) | Update Wiki with "⚠️ Pending Verification" tag. Visible to users. Enters async review queue. |
| 🔴 **Human Escalation** | Red | Confidence < 70% OR direct policy contradiction OR new entity discovery | Do not update. Enter Curation Queue. Assign to appropriate human tier. |

#### 4.2.2 Conflict Severity Classification

Use the following rules to determine whether a contradiction is **CRITICAL** (routes Red) or **MINOR** (routes Yellow):

| Knowledge Type | Critical Trigger | Minor Trigger |
|---|---|---|
| **Quantitative** | Change > 10% in a safety-relevant metric | Change ≤ 10%, non-safety metric |
| **Legal / Normative** | Change in keywords: "Mandatory," "Shall," "Right," "Prohibited" | Editorial rewording with same meaning |
| **Contact / Operational** | Replacement of named individual or contact point | Update to secondary/supplementary contact |
| **Structural** | New policy supersedes existing without explicit SUPERSEDES edge | Addition of new sub-clause |

### 4.3 Anti-Bottleneck Mechanics

#### 4.3.1 Shadow Update Window

During the human review wait time for Yellow-tier items, the wiki displays the new information with a "Pending Verification" tag. Knowledge is available but marked for caution. This prevents curation from blocking information access.

#### 4.3.2 Implicit Verification (Community Trust Score)

```
IF user reads a wiki page containing 🤖 auto-generated content
AND does not flag it within [configurable window, default: 14 days]
THEN increment CommunityTrustScore for that content block

IF CommunityTrustScore >= threshold [configurable, default: 3 unique readers]
THEN auto-promote content status from "Machine-Generated" to "Community-Verified"
```

### 4.4 Curation Interface Design

Curation is broken into **micro-tasks** delivered through two channels.

#### 4.4.1 Atomic Validation Cards

Push a single decision card to the curator:

```
📋 VALIDATION REQUIRED

The 2026 Emergency Report states:
  Shelter Ratio in Camp X = 1:15

Current Wiki value:
  Shelter Ratio in Camp X = 1:20  [source: 2024 Field Assessment]

[ ✅ Approve Update ]  [ ❌ Reject ]  [ ✏️ Edit ]
```

#### 4.4.2 In-Wiki Curation

Do not build a separate curation dashboard. Instead, embed curation directly into the wiki reading experience:

- Each auto-generated paragraph has a small **[Verify]** button
- When a staff member reads a page and clicks Verify on a paragraph, the 🤖 flag clears
- This transforms routine reading into passive verification

### 4.5 Hierarchy of Trust — Tiered Curation

```
Tier 0 — AI
  Scope: Bulk ingestion, auto-accept decisions, shadow updates
  No human approval needed

Tier 1 — Field Data Focal Point
  Scope: Operational data (demographics, camp statistics, local maps, contact updates)
  Approves: Yellow-tier items in their geographic scope

Tier 2 — Regional Focal Point
  Scope: Regional SOPs and strategy documents
  Approves: Yellow and Red-tier items with regional normative implications

Tier 3 — Thematic HQ
  Scope: Global policy
  Summoned only for: CRITICAL conflicts involving global policy contradictions
```

---

## 5. Data Models & Schemas

### 5.1 Document Record

```json
{
  "document_id": "uuid",
  "title": "string",
  "source_url": "string",
  "published_date": "ISO8601",
  "ingested_at": "ISO8601",
  "parser_used": "docling | mineru",
  "markdown_path": "string",
  "status": "INGESTED | EXTRACTED | RECONCILED | ARCHIVED",
  "triplet_count": "integer",
  "conflict_count": "integer"
}
```

### 5.2 Graph Node

```json
{
  "node_id": "uuid",
  "label": "Operation | Policy | Sector | PopulationGroup | Location | Document",
  "name": "string",
  "aliases": ["string"],
  "created_at": "ISO8601",
  "last_updated": "ISO8601",
  "source_documents": ["document_id"],
  "verification_status": "AUTO_ACCEPTED | PENDING | HUMAN_VERIFIED | COMMUNITY_VERIFIED",
  "community_trust_score": "integer"
}
```

### 5.3 Wiki Block

```json
{
  "block_id": "uuid",
  "page_id": "uuid",
  "block_type": "FACT | STATISTIC | POLICY_SUMMARY | CONTACT | PROCEDURE",
  "graph_query": "Cypher or equivalent query string",
  "rendered_content": "string (Markdown)",
  "source_triplets": ["triplet_id"],
  "verification_status": "🤖 AUTO | ⚠️ PENDING | ✅ VERIFIED",
  "last_rendered": "ISO8601",
  "active_conflict_ids": ["conflict_id"]
}
```

---

## 6. Interface Specifications

### 6.1 Wiki Page — Required UI Elements

| Element | Behaviour |
|---|---|
| Block content | Rendered from graph query at page load |
| 🤖 icon | Present on auto-accepted, unverified blocks |
| ⚠️ Conflict banner | Displayed when `active_conflict_ids` is non-empty |
| [Verify] button | Clears 🤖 status for authenticated users of appropriate tier |
| [View Original] button | Opens source Markdown snippet + PDF link in side panel |
| Pending Verification tag | Displayed on Shadow Update (Yellow) content |

### 6.2 Curation Queue — Required Columns

| Column | Description |
|---|---|
| Conflict ID | Unique identifier |
| Type | QUANTITATIVE / NORMATIVE / CONTACT / STRUCTURAL |
| Severity | CRITICAL / MINOR |
| Current Value | Existing graph value + source |
| Proposed Value | Incoming value + source |
| Assigned Tier | 1 / 2 / 3 |
| Actions | Approve / Reject / Edit / Escalate |

### 6.3 MCP Endpoint (Agentic Access)

The knowledge graph must be exposed as a **Model Context Protocol (MCP) server** with at minimum the following tools:

| Tool Name | Description |
|---|---|
| `get_entity` | Retrieve a node and all its edges by entity ID or name |
| `search_knowledge` | Semantic search over verified wiki blocks |
| `get_conflicts` | Retrieve all unresolved ConflictRecords |
| `get_document_triplets` | Return all triplets extracted from a given document |
| `get_wiki_page` | Return rendered Markdown for a wiki page by ID or slug |

---

## 7. Trust & Routing Logic

### 7.1 Full Routing Decision Tree

```
NEW TRIPLET ARRIVES
│
├── Does it match an existing triplet (same subject + predicate)?
│   │
│   ├── NO → Is entity resolved by GLinker?
│   │         ├── YES + confidence ≥ 0.95 → 🟢 AUTO-ACCEPT (EXPANSION)
│   │         ├── YES + confidence 0.70–0.95 → 🟡 SHADOW UPDATE
│   │         └── NO (new entity) → 🔴 HUMAN ESCALATION (Tier 1+)
│   │
│   └── YES → Does the object value match?
│             ├── YES → CONFIRMATION (no action, increment source count)
│             └── NO → Classify conflict severity
│                       ├── CRITICAL → 🔴 HUMAN ESCALATION
│                       └── MINOR → 🟡 SHADOW UPDATE
```

### 7.2 Verification State Machine

```
[EXTRACTED] 
    → (confidence ≥ 0.95) → [AUTO_ACCEPTED 🤖]
        → (community_trust_score ≥ threshold) → [COMMUNITY_VERIFIED ✅]
        → (human clicks Verify) → [HUMAN_VERIFIED ✅]
    → (confidence 0.70–0.95) → [SHADOW_PENDING ⚠️]
        → (curator approves) → [HUMAN_VERIFIED ✅]
        → (curator rejects) → [REJECTED]
    → (confidence < 0.70) → [ESCALATED 🔴]
        → (tier resolves) → [HUMAN_VERIFIED ✅]
        → (tier rejects) → [REJECTED]
```


