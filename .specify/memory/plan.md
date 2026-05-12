# Metamorph Implementation Plan (v3.0 - Website-First)

## Overview
Metamorph v3.0 is a website-to-knowledge intelligence system. The workflow now starts with website URL input, automatic exploration, file selection, and automatic ingestion.

## Phase 1: Website Crawling & File Discovery (Weeks 1-3)
- Build website crawler that automatically discovers all files on user-specified websites
- Parse sitemap.xml for structured file discovery
- Implement file type detection (PDF, Word, Excel, PowerPoint, HTML, text)
- Create file discovery UI with preview and selection controls
- Respect robots.txt and implement rate limiting

## Phase 2: Automatic Ingestion & Processing (Weeks 4-6)
- Implement automatic ingestion trigger when user confirms file selection
- Build ingestion pipeline for processing selected files
- Integrate Docling and MinerU for document parsing
- Store extracted knowledge in Neo4j graph database with website provenance

## Phase 3: Semantic Extraction & Knowledge Graph (Weeks 7-9)
- Extract semantic triplets (Subject → Predicate → Object) from ingested documents
- Map extracted knowledge to eight humanitarian domains
- Build knowledge graph with full provenance tracking to source websites

## Phase 4: Knowledge Reconciliation (Weeks 10-12)
- Detect changes, contradictions, and confirmations in knowledge
- Implement delta alerting system for curators
- Build trust routing based on confidence, sensitivity, source reliability (including website domain)
- Create validation card workflow for review

## Phase 5: Knowledge Cards (Weeks 13-15)
- Generate six types of Knowledge Cards (KC-1 to KC-6) from graph data
- Implement card approval and expiry workflows
- Build card management interface

## Phase 6: Agentic Proposal Drafting & Deployment (Weeks 16-18)
- Implement agentic proposal drafting from curated knowledge cards
- Deploy system to staging environment
- Deploy three knowledge surfaces (Curated Wiki, Discussion, Revision/Audit)

## Phase 7: Advanced Features & Production (Weeks 19-20)
- Implement website scraping scheduling and incremental updates
- Deploy watchers, notifications, community trust
- Full production deployment
