# Architecture Diagram 

## 1. System landscape diagram

![alt text](img/System_landscape_diagram.png)

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
        VEC[(Qdrant / pgvector)]
        SEARCH[(OpenSearch / FTS)]
    end

    subgraph MODEL[Model Layer]
        OLLAMA[Ollama]
        VLLM[vLLM / TGI]
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
    WORKER --> OLLAMA
    WORKER --> VLLM
    WORKER --> PG
    WORKER --> GRAPH
    WORKER --> VEC
    WORKER --> SEARCH

    FASTAPI --> OBS
    WORKER --> OBS
```

---

## 2. Document-to-knowledge pipeline

![alt text](img/Document-to-knowledge_pipeline.png)

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

## 3. Context assembly

 ![alt text](img/Context_assembly.png) 

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

## 4. Hybrid retrieval 

 ![alt text](img/Hybrid_retrieval.png) 

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

## 5. Knowledge-card generation flow

 ![alt text](img/Knowledge-card_generation_flow.png) 

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
