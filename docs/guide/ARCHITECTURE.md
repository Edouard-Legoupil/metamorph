# Metamorph System Architecture

## 1. Platform Vision
Metamorph is an open-source, cloud-agnostic knowledge graph system, designed to turn document collections into an auditable, highly curated, wiki/graph hybrid. It emphasizes explainability, provenance, curation, contradiction handling, and agent/context readiness.

---

## 2. Design Principles & Layered Approach

- **Preserve provenance, enable human curation, resolve contradiction, track temporal validity, ensure stable entities.**
- **Multi-mode retrieval:** hybrid (vector, graph, lexical, wiki-block).
- **Separation of storage:** original docs, normalized/markdown, claims+evidence, graph, wiki/cards, retrieval indices.
- **Open-source, modular, infra/cloud-agnostic.**

---

## 3. Core Architecture Layers

| Layer | Description |
|---|---|
| 0 | Source of Record – immutable original files, versioned with metadata |
| 1 | Document Normalization – markdown, chunking, structural sec+table, layout |
| 2 | Claims & Evidence – atomic claims with provenance, qualifiers, evidence spans |
| 3 | Reconciled Knowledge – accepted/contradicted/superseded facts, trust-routing |
| 4 | Knowledge Graph – canonical entities, relationships, conflicts, timelines |
| 5 | Wiki / Knowledge Cards – human-friendly, context-rich, editable pages |
| 6 | Retrieval & Agent Context – hybrid retrieval, agent endpoints, context packs |

_(see diagrams below)_

---

## 4. System Diagrams

### 4.1 System Landscape Diagram

```mermaid
flowchart LR
    subgraph U[Users and Agents]
        HF[Human users]
        AG[Agentic systems]
    end
    subgraph FE[Presentation Layer]
        UI[React Frontend]
        WIKI[Wiki.js / Card Views]
    end
    subgraph API[Application Layer]
        FASTAPI[FastAPI API]
        MCP[MCP / Agent API]
        WORKER[Celery Workers]
    end
    subgraph SRC[Source + Normalization]
        S3[MinIO / S3-compatible storage]
        PARSE[Parsing + OCR + Markdown normalization]
        CHUNK[Structure-aware chunking]
    end
    subgraph KNOW[Knowledge Layer]
        PG[(PostgreSQL)]
        GRAPH[(Neo4j / Memgraph)]
        VEC[(PostgreSQL - pgvector)]
        SEARCH[(PostgreSQL -  FTS)]
    end
    subgraph MODEL[Model Layer]
        LiteLLM[Inference: Cloud / Ollama]
        NLP[spaCy / GLiNER / sentence-transformers]
    end
    subgraph GOV[Identity + Observability]
        KC[Keycloak]
        OBS[Prometheus + Grafana + OTel]
    end
    HF --> UI
    HF --> WIKI
    AG --> MCP
    UI --> FASTAPI
    WIKI --> FASTAPI
    MCP --> FASTAPI
    FASTAPI --> PG
    FASTAPI --> GRAPH
    FASTAPI --> VEC
    FASTAPI --> SEARCH
    FASTAPI --> S3
    FASTAPI --> KC
    FASTAPI --> WORKER
    WORKER --> PARSE
    PARSE --> CHUNK
    PARSE --> S3
    CHUNK --> PG
    CHUNK --> VEC
    CHUNK --> SEARCH
    WORKER --> NLP
    WORKER --> LiteLLM
    WORKER --> PG
    WORKER --> GRAPH
    WORKER --> VEC
    WORKER --> SEARCH
    FASTAPI --> OBS
    WORKER --> OBS
```

---

### 4.2 Document-to-Knowledge Pipeline

```mermaid
flowchart TD
    A[Source document] --> B[Register file metadata]
    B --> C[Store original in object storage]
    C --> D[Layout analysis]
    D --> E[Parser routing]
    E --> F[Markdown conversion]
    F --> G[Quality checks]
    G --> H[Section tree + chunking]
    H --> I[Claim extraction]
    I --> J[Evidence linking]
    J --> K[Entity resolution]
    K --> L[Reconciliation]
    L --> M{Outcome}
    M -->|Confirmation| N[Increment source count]
    M -->|Expansion| O[Proposed new accepted fact]
    M -->|Update| P[Supersession workflow]
    M -->|Contradiction| Q[Conflict record]
    M -->|Insufficient evidence| R[Pending review]
    N --> S[Graph materialization / update]
    O --> T{Trust routing}
    P --> T
    Q --> T
    R --> T
    T -->|Auto-accept| S
    T -->|Shadow| U[Shadow wiki state]
    T -->|Human review| V[Curator queue]
    S --> W[Wiki block regeneration]
    U --> W
    V --> W
    W --> X[Vector/lexical index refresh]
    X --> Y[Search and agent context assembly]
```

---

### 4.3 Context Assembly

```mermaid
flowchart TD
    A[Incoming claim] --> B[Find matching canonical facts]
    B --> C[Normalize values and temporal scope]
    C --> D[Conflict classification]
    D --> E{Conflict?}
    E -->|No| F[Accept or stage claim]
    E -->|Yes| G[Create ConflictRecord]
    G --> H[Attach claims, facts, and evidence]
    H --> I[Route by severity/domain]
    I --> J[Curator review page]
    J --> K{Curator action}
    K -->|Accept new fact| L[Supersede prior fact]
    K -->|Keep current| M[Reject incoming claim]
    K -->|Merge| N[Create curated statement]
    K -->|Escalate| O[Send to higher review lane]
    L --> P[Update graph + wiki + audit]
    M --> P
    N --> P
    O --> P
```

---

### 4.4 Hybrid Retrieval

```mermaid
flowchart TD
    A[User / agent query] --> B[Intent classifier]
    B --> C[Retrieval planner]
    C --> D[Lexical search]
    C --> E[Vector retrieval]
    C --> F[Graph traversal]
    C --> G[Wiki block retrieval]
    D --> H[Candidate set]
    E --> H
    F --> H
    G --> H
    H --> I[Reranker / score fusion]
    I --> J[Context assembler]
    J --> K[Compact context pack]
    K --> L[Response generation or direct answer]
    J --> M[Provenance bundle]
    J --> N[Confidence + verification metadata]
```

---

### 4.5 Knowledge Card Generation

```mermaid
flowchart LR
    A[Knowledge-card template] --> B[Section query definitions]
    B --> C[Graph queries]
    B --> D[Claim queries]
    B --> E[Evidence aggregations]
    B --> F[Curated editorial content]
    C --> G[Block assembler]
    D --> G
    E --> G
    F --> G
    G --> H[Draft card]
    H --> I{Publish policy}
    I -->|Auto / low risk| J[Published card]
    I -->|Review required| K[Curator validation]
    K --> J
```


---

## 5. Deployment Patterns

- **Default stack:** FastAPI, PostgreSQL, Redis, Neo4j, MinIO, Qdrant, pgvector, Wiki.js, Keycloak, Prometheus, Grafana, Ollama/vLLM
- **Minimal:** API, worker, frontend, Postgres, Redis, Neo4j, MinIO, vector db, basic model server
- **Full production:** Adds OpenSearch, Wiki.js, Keycloak, advanced monitoring, multiple tier environments
- **Everything is modular and adapter-enabled for cloud/on-prem/local use.**

---

## 6. Principles

- Claims are richer than triplets (hold provenance, qualifiers, time, review, status)
- Hybrid retrieval is required—never only graph/vector/lexical
- Contradiction and provenance are obligatory
- The wiki is the curator interface but not the truth layer
- Never auto-overwrite accepted facts
- All operation is auditable; all state transitions are tracked

---

## 7. Repo Structure

```
backend/
frontend/
infrastructure/
docs/
scripts/
README.md
ARCHITECTURE.md
PIPELINE.md
DATABASE.md
CURATION.md
API.md
SECURITY.md
OPS.md
IMPLEMENTATION_BACKLOG.md
```

---

For more details, see [PIPELINE.md](./PIPELINE.md), [DATABASE.md](./DATABASE.md), and [CURATION.md](./CURATION.md).