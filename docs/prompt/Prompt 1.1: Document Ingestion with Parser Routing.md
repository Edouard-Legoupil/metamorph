Implement the ingestion pipeline  with routing logic between Docling and MinerU.

Create services/ingestion/ingestion_pipeline.py:

1. Document intake:
   - Accept PDF, DOCX, Markdown, HTML
   - Extract document metadata (title, author, publication_date, source_url)
   - Store original file with version tracking
   - Create Document record in graph

2. Layout analysis for parser routing:
   - Extract first 10 pages for sampling
   - Calculate table density (tables per page)
   - Detect multi-column layout
   - Count embedded images/charts
   - Decision logic:
     IF table_density > 0.3 OR columns > 1 OR complex_layout_score > threshold:
         route_to = "mineru"
     ELSE:
         route_to = "docling"

3. Docling integration:
   - Configure for humanitarian document types (policy docs, situation reports, assessments)
   - Preserve: headings, lists, tables, footnotes, citations
   - Output: Markdown with structural annotations

4. MinerU integration:
   - Configure for complex tables, multi-column, embedded charts
   - Enable table structure recognition
   - Extract embedded images with captions
   - Output: Markdown with layout annotations

5. Document record update:
   - Store markdown_path
   - Set status = "EXTRACTED"
   - Record parser_used and processing_time
   - Queue for triplet extraction

Invariant: All output must be Markdown-first for consistent downstream processing.

Add REST API endpoints, asynchronous task wiring, Neo4j upsert, and test coverage for this pipeline

Add  full Neo4j transactional wiring, batch ingest, Playwright E2E tests, and S3/Minio upload testing