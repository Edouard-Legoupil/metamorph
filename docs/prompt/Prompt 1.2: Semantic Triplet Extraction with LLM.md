Implement a semantic triplet (claim) extraction service in the backend pipeline, operating on normalized Markdown input. Configure extraction with robust fallback—prefer local LLMs where possible, but support chaining for cloud providers if configured. Extract claims with subject, predicate, and object, as well as extraction confidence and evidence text span, for all document and card types defined in PIPELINE.md. Ensure the output meets the canonical schema, supports batch and streaming processing, and links all extracted triplets to the correct document/version/artifact identifiers for provenance. Report extraction coverage and low-confidence warnings in the curation dashboard; persist all extractions in the database. 

Verification & Test Guidance
- [ ] The backend has an extraction module/service that runs after parsing and normalization, producing semantic claims/triplets.
- [ ] Each extracted triplet/claim has subject, predicate, object/value, confidence, evidence, and provenance fields conforming to system schema.
- [ ] The triplet extraction service handles batch jobs, tracks status, and assigns extracted claims to the correct document/artifact provenance.
- [ ] The curation UI/dashboard exposes extraction stats or low-confidence warnings.
- [ ] Tests or manual runs show claims can be extracted from at least three document/card types.