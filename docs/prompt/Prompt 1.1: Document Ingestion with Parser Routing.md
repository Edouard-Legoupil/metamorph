Implement a file ingestion pipeline that accepts uploads of documents (PDF, DOCX, Markdown, HTML, and other supportable rich formats), collects key metadata (title, author, publication date, source URL, checksum, document type), and stores the original file with version tracking and status in object storage. Route each document to the appropriate normalization parser according to a layout and content analysis—choose the optimal parser for tables, multi-column layouts, or OCR needs. Save normalized Markdown output and update the document record with all processing attributes, parser metadata, execution timing, provenance, and storage key. Document the full ingestion flow in get-started.md and PIPELINE.md. Ensure the ingestion code is robust to novel input and all writes are auditable. 

Verification & Test Guidance
- [ ] Confirm an ingestion pipeline exists with explicit parser routing logic (by file type/layout/complexity).
- [ ] Verify all document uploads record metadata and status in the database.
- [ ] Check that original and normalized files are saved in object storage with persistent, traceable keys.
- [ ] See get-started.md outlines the operational and pipeline ingestion steps for new files.
- [ ] Manually upload example files via the UI/API and verify all DB entries (including version lineage, parser selection, and provenance).