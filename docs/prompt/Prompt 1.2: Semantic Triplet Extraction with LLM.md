Implement the triplet extraction service that converts parsed Markdown into semantic triplets using LiteLLM.

Create services/extraction/triplet_extractor.py:

1. LiteLLM configuration for extraction:
   - Primary model: GPT-4 or Claude (high accuracy)
   - Fallback chain: GPT-3.5 -> Claude Instant -> Local LLM
   - Track token usage and costs per document
   - Implement rate limiting and retry logic

2. Document chunking for extraction:
   - Split Markdown at semantic boundaries (headings, sections)
   - Maintain context window of 4000 tokens with 200 token overlap
   - Preserve section hierarchy for relationship inference

3. Extraction prompts by document type:
   - For Policy/SOP documents: Extract normative triplets (APPLIES_TO, SUPERSEDES, GOVERNS)
   - For Assessments/Reports: Extract factual triplets (POPULATION_FIGURE, INDICATOR_VALUE)
   - For Evaluations: Extract evidence triplets (PRODUCES, ENABLED_BY, CONTRADICTS)
   - For Partner documents: Extract capacity triplets (IMPLEMENTED_BY, CAPACITY_RATING)

4. JSON mode enforcement:
   - Response must conform to triplet_schema
   - Include extraction_confidence for each triplet
   - Provide raw_text_snippet as evidence

5. Post-extraction processing:
   - Deduplicate identical triplets from same document
   - Calculate aggregate confidence scores
   - Store triplets with document_id reference
   - Update document status = "TRIPLETS_EXTRACTED"

6. Extraction quality metrics:
   - Track extraction confidence distribution
   - Flag low-confidence (<0.7) extractions for human review
   - Generate extraction report for curator dashboard


- Wire extract_triplets_from_markdown into the "triplet extraction" Celery task, called after document parsing.
- Extend persist_doc_triplets with your graph-database upsert logic (for full auto-update of Neo4j).
- Add batch/extraction endpoints or pipeline queue integration as desired.   