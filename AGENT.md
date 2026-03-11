# Coding Agent Instructions for Metamorph: Humanitarian Knowledge Platform


## 🎯 Mission Overview

from _ctypes import PyObj_FromPtr
You are building Metamorph — an open-source platform that transforms PDFs ("knowledge tombstones") into a living wiki connected to a knowledge graph, specifically designed for humanitarian operations following UNHCR's Knowledge Card System.

Your output will be used by the agentic systems thaht will serve Humanitarian staff (for instance when they write proposals, or when they need to renew knowledge cards). It will help them draft document faster, with AI assistance and full source traceability.

## 📚 Reference Documents

All prompts reference these three core documents:

knowledge-card.yaml	Defines the 6 card types (KC-1 through KC-6), their sections, word limits, and graph queries
humanitarian-knowledge-ontology.md	Complete Labeled Property Graph ontology — all node types, edge types, and property schemas
knowledge-pipeline-blueprint.md	Three-component architecture: Ingestion → Reconciliation → Orchestration, with trust routing

You must ensure all code aligns with these specifications.

## 🏗 Technology Cloud-Agnostic Stack

* __Backend API	FastAPI (Python 3.11+)__:	Async support, automatic OpenAPI docs, Pydantic v2 for schema validation

* __Graph Database	Neo4j 5+ (Community Edition)__:		Native graph support, Cypher queries, APOC procedures, perfect for LPG ontology

* __Task Queue	Celery + Redis__:		Async processing for long-running PDF extraction

* __Vector Store	pgvector (PostgreSQL 15+)__:		Embeddings for semantic search, hybrid search with graph

* __Object Storage	S3-compatible (MinIO for dev)__:		Cloud-agnostic file storage, separate from graph

* __AI Gateway	LiteLLM__:		Switch between OpenAI, Anthropic, Claude, local models without code changes

* __Frontend	React 18 + TypeScript__:		Wiki-style interface, shadcn/ui components, TailwindCSS

* __Wiki Engine	Wiki.js__:		Mature open-source wiki with REST API, can push approved content

* __Container	Docker + Docker Compose__:	Development consistency, easy deployment

* __Orchestration	Kubernetes (for production)__:	Cloud-agnostic deployment via Helm

* __GLinker__:		Entity resolution and disambiguation
* __PDF Processing Libraries__:	
   
   * __Docling__:	Primary parser for standard humanitarian documents (reports, policies, situation updates)
   * __MinerU__:	Escalation parser for complex layouts (multi-column, dense tables, embedded charts)
   * __PyMuPDF (fitz)__:	Layout analysis for routing decisions, quick text extraction
   * __pytesseract + EasyOCR__:	OCR fallback for scanned documents
   * __pdfplumber + camelot-py__:	Table extraction (used by Docling internally)
   * __pandoc + pypandoc__:	Universal document to Markdown conversion (fallback)


## 🧠 Core Architecture Principles

### 1. Three-Stage Pipeline 

```
[Stage 1: Document-Centric]
    PDF/DOCX → Markdown → Semantic Triplets
         ↓
[Stage 2: Entity-Centric]
    Triplets → Graph Database (LPG) with conflict detection
         ↓
[Stage 3: User-Centric]
    Graph → Wiki Pages (via Templates) + MCP Server
```


### 2. Atomic Unit = Semantic Triplet

Everything in the system revolves around triplets:

```json
{
  "subject": {"label": "Donor", "id": "uuid", "name": "USAID"},
  "predicate": "FUNDS",
  "object": {"label": "FundingInstrument", "id": "uuid", "name": "2024 HIP"},
  "metadata": {
    "source_document_id": "...",
    "extraction_confidence": 0.97,
    "page_reference": 14,
    "raw_text_snippet": "USAID will fund the 2024 Humanitarian Implementation Plan..."
  }
}
```

### 3. Trust Routing (Uncertainty-Driven)

Don't review everything — route by confidence:

 * 🟢 Auto-Accept - Confidence: ≥95% - Action: Immediate graph update, 🤖 icon
 * 🟡 Shadow Update - Confidence: 70-95% - Action: Wiki shows ⚠️ pending, enters queue
 * 🔴 Human Escalation - Confidence: <70% or conflict - Action: Blocks update, assigns to curator

### 4. Knowledge Cards Over Raw Graph

The wiki doesn't show raw graph data — it shows Knowledge Cards (KC-1 through KC-6). Each card section is a Block that runs a graph query at render time.

### 5. Source Traceability Always

Every piece of information on every wiki page must be traceable to:

 * Original source document (PDF link)

 * Extraction timestamp

 * Confidence score

 * Verification status

## 📄 PDF PROCESSING STRATEGY

Two-Tier PDF to Markdown Pipeline: Following the blueprint's routing logic, we use two dedicated PDF-to-Markdown tools with escalation:

### Tier 1: Docling (Primary)

 * Purpose: Fast, accurate extraction for standard humanitarian documents

 * Best for: Reports, policies, situation updates, standard layouts

 * Strengths: Table recognition, heading hierarchy, list preservation, citation extraction

 * Integration: Python SDK (docling) or CLI

 * Output: Clean Markdown with structural annotations

### Tier 2: MinerU (Escalation)

 * Purpose: Complex layouts that defeat Docling

 * Best for: Multi-column academic papers, dense tables, embedded charts, scanned documents with complex formatting

 * Strengths: Layout analysis, table structure reconstruction, multi-column reading order

 * Integration: Python SDK or API

 * Output: Markdown with layout preservation

Routing Logic

```python
def route_to_parser(document_path: str, analysis: LayoutAnalysis) -> str:
    """
    Decide which parser to use based on document characteristics.
    Returns "docling" or "mineru".
    """
    
    # Heuristic thresholds (configurable)
    if (
        analysis.table_density > 0.3 or           # Many tables
        analysis.column_count > 1 or               # Multi-column layout
        analysis.embedded_charts > 5 or            # Many charts/figures
        analysis.scanned_pages_ratio > 0.5 or      # Mostly scanned
        analysis.layout_complexity_score > 0.7     # Custom complexity metric
    ):
        return "mineru"
    
    return "docling"
```

Layout Analysis for Routing: Before routing, perform lightweight analysis using PyMuPDF:
```python

class LayoutAnalysis:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.page_count = 0
        self.table_density = 0.0
        self.column_count = 1
        self.embedded_charts = 0
        self.scanned_pages_ratio = 0.0
        self.layout_complexity_score = 0.0
    
    def analyze_first_n_pages(self, n: int = 5):
        """Analyze first n pages to make routing decision."""
        # Use PyMuPDF (fitz) for quick analysis
        import fitz
        
        doc = fitz.open(self.pdf_path)
        self.page_count = len(doc)
        
        pages_to_check = min(n, self.page_count)
        text_pages = 0
        table_count = 0
        
        for i in range(pages_to_check):
            page = doc[i]
            
            # Check if page is scanned (little to no text)
            text = page.get_text()
            if len(text.strip()) < 100:
                continue
            text_pages += 1
            
            # Rough table detection (looking for tabular structures)
            blocks = page.get_text("dict")
            table_count += self._detect_tables(blocks)
            
            # Detect multi-column via text block positioning
            if self._is_multi_column(blocks):
                self.column_count = max(self.column_count, 2)
        
        self.scanned_pages_ratio = 1 - (text_pages / pages_to_check)
        self.table_density = table_count / pages_to_check
        self.layout_complexity_score = self._calculate_complexity()
        
        return self
```

Parser Router Implementation

```python
# services/ingestion/parser_router.py

import asyncio
from pathlib import Path
import logging
from typing import Optional

from .docling_wrapper import DoclingWrapper
from .mineru_wrapper import MinerUWrapper
from .layout_analyzer import LayoutAnalyzer

logger = logging.getLogger(__name__)

class ParserRouter:
    """
    Routes documents to appropriate parser based on layout analysis.
    Implements fallback: try Docling first, escalate to MinerU if needed.
    """
    
    def __init__(self):
        self.docling = DoclingWrapper()
        self.mineru = MinerUWrapper()
        self.analyzer = LayoutAnalyzer()
        
        # Configuration
        self.max_retries = 2
        self.force_mineru_threshold = 0.7  # complexity score
    
    async def process_document(
        self, 
        pdf_path: str, 
        force_parser: Optional[str] = None
    ) -> dict:
        """
        Process PDF through appropriate parser.
        
        Returns:
            Dict with markdown and metadata
        """
        # Analyze document for routing
        analysis = await self.analyzer.analyze(pdf_path)
        
        # Determine which parser to use
        if force_parser:
            parser_name = force_parser
        elif analysis.layout_complexity_score > self.force_mineru_threshold:
            parser_name = "mineru"
            logger.info(f"Complex layout detected, routing to MinerU")
        else:
            parser_name = "docling"
            logger.info(f"Standard layout, routing to Docling")
        
        # Try primary parser
        try:
            if parser_name == "docling":
                result = await self.docling.convert_to_markdown(pdf_path)
            else:
                result = await self.mineru.convert_to_markdown(pdf_path)
            
            # Add routing metadata
            result["metadata"]["routing_basis"] = {
                "parser_chosen": parser_name,
                "complexity_score": analysis.layout_complexity_score,
                "table_density": analysis.table_density,
                "scanned_ratio": analysis.scanned_pages_ratio
            }
            
            return result
            
        except Exception as e:
            logger.warning(f"{parser_name} failed: {e}")
            
            # Fallback to alternative parser
            fallback = "mineru" if parser_name == "docling" else "docling"
            logger.info(f"Falling back to {fallback}")
            
            try:
                if fallback == "docling":
                    result = await self.docling.convert_to_markdown(pdf_path)
                else:
                    result = await self.mineru.convert_to_markdown(pdf_path)
                
                result["metadata"]["fallback_from"] = parser_name
                return result
                
            except Exception as e2:
                logger.error(f"Both parsers failed: {e2}")
                raise
```


## 📁 Project Structure

```text
metamorph/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── documents.py      # Upload, status
│   │   │   │   │   ├── cards.py          # KC-1 through KC-6 CRUD
│   │   │   │   │   ├── wiki.py           # Wiki.js integration
│   │   │   │   │   ├── search.py         # Hybrid search
│   │   │   │   │   ├── conflicts.py      # Conflict resolution
│   │   │   │   │   └── mcp.py            # Model Context Protocol
│   │   │   │   └── dependencies.py
│   │   │   └── __init__.py
│   │   ├── core/
│   │   │   ├── config.py                  # Pydantic settings
│   │   │   ├── security.py                 # API keys, auth
│   │   │   └── logging.py                  # Structured logging
│   │   ├── models/
│   │   │   ├── graph/                      # Neo4j node/edge models
│   │   │   │   ├── base.py
│   │   │   │   ├── geographic.py
│   │   │   │   ├── crisis.py
│   │   │   │   ├── population.py
│   │   │   │   ├── operational.py
│   │   │   │   ├── policy.py
│   │   │   │   ├── finance.py
│   │   │   │   ├── stakeholders.py
│   │   │   │   └── knowledge.py
│   │   │   ├── triplets.py                  # Triplet schema
│   │   │   ├── conflicts.py                  # ConflictRecord
│   │   │   └── cards.py                       # Knowledge card models
│   │   ├── services/
│   │   │   ├── ingestion/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── parser_router.py          # Docling vs MinerU
│   │   │   │   ├── docling_wrapper.py
│   │   │   │   ├── mineru_wrapper.py
│   │   │   │   └── layout_analyzer.py
│   │   │   ├── extraction/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── triplet_extractor.py      # LLM-based
│   │   │   │   ├── entity_resolver.py        # GLinker
│   │   │   │   └── confidence_scorer.py
│   │   │   ├── reconciliation/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── delta_engine.py           # Triplet comparison
│   │   │   │   ├── conflict_classifier.py
│   │   │   │   └── shadow_updater.py
│   │   │   ├── routing/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── trust_router.py           # Tier decision
│   │   │   │   └── tier_assigner.py
│   │   │   ├── wiki/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── block_assembler.py        # Graph → Markdown
│   │   │   │   ├── card_templates.py         # KC-1..6 templates
│   │   │   │   └── wikijs_client.py          # Publishing
│   │   │   ├── search/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── vector_store.py           # pgvector
│   │   │   │   └── hybrid_search.py
│   │   │   ├── alerts/
│   │   │   │   ├── __init__.py
│   │   │   │   └── delta_alert_service.py
│   │   │   └── proposal/
│   │   │   │   ├── __init__.py
│   │   │   │   └── proposal_agent.py          # Card assembly
│   │   ├── worker/
│   │   │   ├── __init__.py
│   │   │   ├── tasks.py                       # Celery tasks
│   │   │   └── celery_app.py
│   │   └── main.py
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── fixtures/                           # Sample PDFs
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Upload/
│   │   │   ├── Documents/
│   │   │   ├── Review/
│   │   │   │   ├── MarkdownEditor.tsx
│   │   │   │   ├── ValidationCard.tsx
│   │   │   │   └── ConflictResolver.tsx
│   │   │   ├── Wiki/
│   │   │   │   ├── PageViewer.tsx
│   │   │   │   ├── BlockRenderer.tsx
│   │   │   │   └── VerifyButton.tsx
│   │   │   ├── Curator/
│   │   │   │   ├── CardWorkspace.tsx
│   │   │   │   ├── SectionEditor.tsx
│   │   │   │   └── QueueDashboard.tsx
│   │   │   └── Search/
│   │   ├── hooks/
│   │   ├── lib/
│   │   ├── types/
│   │   └── App.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
├── infrastructure/
│   ├── docker-compose.yml
│   ├── docker-compose.prod.yml
│   ├── helm/                                    # Kubernetes charts
│   │   └── metamorph/
│   ├── terraform/
│   │   ├── aws/
│   │   ├── gcp/
│   │   └── azure/
│   └── monitoring/
│       ├── prometheus.yml
│       └── grafana-dashboards/
├── docs/
│   ├── api/                                      # OpenAPI docs
│   ├── ontology/                                 # Graph schema docs
│   └── user-guide/
└── scripts/
    ├── seed_graph.py                              # Initial ontology load
    └── migrate.py                                  # DB migrations
```


## 🧩 Coding Standards & Practices

python (Backend) Style

 * Black for formatting (line length 100)

 * isort for import sorting

 * mypy with strict mode (no Any unless absolutely necessary)

 * ruff for linting

Typing
```python

from typing import Optional, List, Dict, Any, Union
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, validator

class Triplet(BaseModel):
    subject: EntityRef
    predicate: str  # Should be Literal["FUNDS", "LOCATED_IN", ...] but dynamic
    object: Union[EntityRef, LiteralValue]
    metadata: ExtractionMetadata
    
    class Config:
        frozen = True  # Triplets are immutable
```
### Async First

 * Use async def for FastAPI endpoints

 * Use asyncio.to_thread for CPU-bound operations (OCR, PDF parsing)

 * Database drivers: asyncpg for PostgreSQL, neo4j async driver

### Error Handling

```python
from app.core.exceptions import (
    ProcessingError, 
    ExtractionError,
    ConflictError,
    NotFoundError
)

@router.post("/upload")
async def upload_document(file: UploadFile):
    try:
        result = await ingestion_service.process(file)
        return {"job_id": result.job_id}
    except ExtractionError as e:
        raise HTTPException(400, f"Extraction failed: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(500, "Internal server error")
```

### Logging (Structured)
```python

import structlog
logger = structlog.get_logger()

logger.info(
    "document_uploaded",
    document_id=str(doc_id),
    file_size=file.size,
    file_type=file.type,
    user=current_user.id
)
```

TypeScript/React (Frontend) Style

 * ESLint with Airbnb config

 * Prettier for formatting

 * TypeScript strict mode

Component Structure
tsx
```
// components/Review/ValidationCard.tsx
import { FC, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Conflict, ConflictResolution } from '@/types';

interface ValidationCardProps {
  conflict: Conflict;
  onResolve: (resolution: ConflictResolution) => void;
}

export const ValidationCard: FC<ValidationCardProps> = ({ 
  conflict, 
  onResolve 
}) => {
  const [loading, setLoading] = useState(false);
  
  const handleApprove = async () => {
    setLoading(true);
    await onResolve({ action: 'approve', conflictId: conflict.id });
    setLoading(false);
  };
  
  return (
    <Card className="p-4 border-l-4 border-l-yellow-500">
      {/* Component JSX */}
    </Card>
  );
};
```


### State Management

 * React Query for server state (caching, mutations, polling)

 * Zustand for UI state (filters, modals, sidebar)

 * Avoid Redux unless absolutely necessary

Styling

 * TailwindCSS with custom theme

 * shadcn/ui for component library

 * Dark mode support required



##  🔄 Key Workflows

### 1. Document Processing Pipeline

```text
Upload PDF 
    → Parser Router (Docling vs MinerU)
    → Markdown Generation
    → Triplet Extraction (LLM)
    → Entity Resolution (GLinker)
    → Delta Engine (compare with graph)
        ├── EXPANSION → Trust Router → Auto/Shadow/Human
        ├── CONFIRMATION → Increment source count
        └── CONTRADICTION → ConflictRecord → Shadow/Human
    → Wiki Block Update (if approved)
```

### 2. Knowledge Card Authoring

```text
Curator opens KC-2 (Field Context)
    → System pre-populates from graph:
        * Population figures (latest)
        * Protection incidents (last 12 months)
        * Active projects (by sector)
    → Curator edits, adds narrative
    → Submits for review
    → Tier-based approval (field → regional → HQ)
    → On approval: status = APPROVED, valid_until = now + 12mo
    → Card available for proposal generation
```

### 3. Conflict Resolution

```text
ConflictRecord created (CRITICAL/MINOR)
    → Assigned to Tier 1/2/3
    → Curator sees in queue or in-wiki
    → Views current vs proposed with sources
    → Actions:
        * Approve: Update graph, close conflict
        * Reject: Keep current, close with note
        * Edit: Create merged version
        * Escalate: Move to higher tier
    → On resolution, update affected wiki blocks
    → Notify original document uploader
```

## 🧪 Testing Strategy

### Unit Tests

 * Test each service in isolation

 * Mock external APIs (LiteLLM, GLinker, Wiki.js)

 * Test confidence scoring logic

 * Test conflict classification rules

### Integration Tests

 * Test document ingestion end-to-end with sample PDFs

 * Test triplet extraction against known documents

 * Test graph queries return expected results

 * Test wiki block rendering with mock data

### End-to-End Tests (Playwright)

 * User uploads PDF

 * Processing completes

 * Review interface loads

 * Curator approves card

 * Wiki page updates

 * Search finds content

### Test Fixtures

```text
tests/fixtures/
├── pdfs/
│   ├── simple_report.pdf
│   ├── scanned_document.pdf
│   ├── complex_tables.pdf
│   └── multi_column.pdf
├── triplets/
│   └── expected_extractions.json
└── graph/
    └── seed_data.cypher
```

🚀 Development Prompt

Phase 0: Foundation 
 * [Prompt 0.1: Graph Database Schema](prompt/Prompt 0.1: Graph Database Schema.md)
 * [Prompt 0.2: Semantic Triplet Extraction Schema](prompt/Prompt 0.2: Semantic Triplet Extraction Schema.md)

Phase 1: Ingestion Pipeline 
 * [Prompt 1.1: Document Ingestion with Parser Routing](prompt/Prompt 1.1: Document Ingestion with Parser Routing.md)
 * [Prompt 1.2: Semantic Triplet Extraction with LLM](prompt/Prompt 1.2: Semantic Triplet Extraction with LLM.md)
 * [Prompt 1.3: Entity Resolution with GLinker Integration](prompt/Prompt 1.3: Entity Resolution with GLinker Integration.md)

Phase 2: Reconciliation   
 * [Prompt 2.1: Delta Engine with Conflict Detection](prompt/Prompt 2.1: Delta Engine with Conflict Detection.md)
 * [Prompt 2.2: Wiki Block Assembly from Graph Queries](prompt/Prompt 2.2: Wiki Block Assembly from Graph Queries.md)
 * [Prompt 2.3: Knowledge Card Template Implementation](prompt/Prompt 2.3: Knowledge Card Template Implementation.md)

Phase 3: Knowledge Cards 
 * [Prompt 3.1: Three-Tier Routing System](prompt/Prompt 3.1: Three-Tier Routing System.md)
 * [Prompt 3.2: Community Trust & Implicit Verification](prompt/Prompt 3.2: Community Trust & Implicit Verification.md)
 * [Prompt 3.3: Curation Interface (In-Wiki & Queue)](prompt/Prompt 3.3: Curation Interface (In-Wiki & Queue).md)

Phase 4: Curation Interface
 * [Prompt 4.1: Curator Workspace for Knowledge Cards](prompt/Prompt 4.1: Curator Workspace for Knowledge Cards.md)
 * [Prompt 4.2: Delta Alert System for Card Updates](prompt/Prompt 4.2: Delta Alert System for Card Updates.md)

Phase 5: MCP
 * [Prompt 5.1: Model Context Protocol (MCP) Server](prompt/Prompt 5.1: Model Context Protocol (MCP) Server.md)


## 🔧 Configuration & Environment

### Required Environment Variables

```bash
# Database
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

POSTGRES_DSN=postgresql://user:pass@postgres:5432/metamorph

REDIS_URL=redis://redis:6379/0

# Storage
STORAGE_PROVIDER=s3  # or local
S3_ENDPOINT=http://minio:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=metamorph-documents

# AI (LiteLLM)
LITELLM_PROXY_URL=http://litellm:4000
LITELLM_MODEL_PREFERENCE=gpt-4,claude-3,ollama/llama3
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...
OLLAMA_BASE_URL=http://ollama:11434

# Wiki.js
WIKIJS_URL=http://wikijs:3000
WIKIJS_API_KEY=...

# Security
SECRET_KEY=...
API_KEY_HEADER=X-API-Key
CORS_ORIGINS=["http://localhost:3000"]
```


### Docker Compose Configuration

```yaml
# docker-compose.yml additions for PDF processing

services:
  # ... existing services ...
  
  docling:
    build:
      context: .
      dockerfile: Dockerfile.docling
    volumes:
      - ./uploads:/uploads
      - ./models:/models  # Cache OCR models
    environment:
      - OCR_LANGUAGE=eng+fra+ara  # Common humanitarian languages
      - TABLE_STRUCTURE=true
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G
  
  mineru:
    image: mineru/mineru:latest  # Adjust based on actual MinerU distribution
    volumes:
      - ./uploads:/uploads
      - ./models/mineru:/root/.cache/mineru
    environment:
      - MINERU_USE_GPU=false  # Set true if GPU available
      - MINERU_MEMORY_LIMIT=8G
    deploy:
      resources:
        limits:
          memory: 8G
        reservations:
          memory: 4G

Parser-Specific Dockerfile
dockerfile

# Dockerfile.docling
FROM python:3.11-slim

# Install system dependencies for Docling
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-fra \
    tesseract-ocr-ara \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Docling with extras
RUN pip install docling[all]  # Includes table extraction, OCR

# Copy wrapper code
COPY services/ingestion/docling_wrapper.py .
COPY services/ingestion/parser_router.py .

# Create model cache directory
RUN mkdir -p /models

CMD ["python", "-c", "import time; time.sleep(infinity)"]  # Run as service
```


## 📝 Documentation Requirements

### Code Documentation

 * Docstrings: Google style for all public functions

 * Type hints: Complete coverage

 * Complex logic: Add comments explaining "why", not "what"

### API Documentation

 * FastAPI generates OpenAPI (available at /docs)

 * Add detailed descriptions to all endpoints

 * Include example requests/responses

 * Document error codes

Architecture Decision Records (ADRs)

For significant decisions, create ADRs in docs/adr/:

```markdown

# ADR-001: Use Neo4j over ArangoDB

## Context
We need a graph database supporting the LPG ontology...

## Decision
Neo4j because:
- Mature Cypher query language
- APOC procedures for graph algorithms
- Strong community and tooling

## Consequences
- Must manage APOC compatibility
- License is GPL (but AGPL ok for open source)
```


## 🚨 Common Pitfalls to Avoid

1. Storing Documents in the Graph: The graph stores metadata and triplets, not the documents themselves. Documents go in S3-compatible storage.

2. Overwriting Data Without Conflict Detection: Never silently overwrite existing graph data. Always go through delta engine → conflict detection → routing.

3. Ignoring Confidence Scores: Confidence scores aren't optional. Every triplet must have one. Use them for routing decisions.

4. Building a Separate Curation Dashboard: Curation should happen in the wiki, not in a separate admin panel. Embed Verify buttons, conflict banners, and quick actions directly in the reading experience.

5. Hardcoding AI Providers: Always use LiteLLM abstraction. Never call OpenAI/Anthropic directly. This keeps the system cloud-agnostic.

6. Forgetting Source Traceability: Every wiki paragraph must link back to source documents. If it can't, it shouldn't be in the wiki.

7. Skipping the Shadow Update Window: Yellow-tier items should appear in the wiki immediately (with warning), not wait for human approval. This prevents curation bottlenecks.

8. Not Handling Parser Failures Gracefully: Always implement fallback between Docling and MinerU. Never assume a single parser will succeed.

## 🎯 Success Criteria

The system is successful when:

 * A new document is uploaded and within minutes, its content appears in the relevant wiki pages (with appropriate verification badges)

 * 80% of knowledge card sections pre-populated from the graph

 * When a new policy supersedes an old one, all affected wiki pages show conflict banners within 1 hour

 * A field officer reads a wiki page and can verify a paragraph with one click, contributing to community trust scores

 * An AI agent can query the MCP server and get structured knowledge with confidence scores and sources


