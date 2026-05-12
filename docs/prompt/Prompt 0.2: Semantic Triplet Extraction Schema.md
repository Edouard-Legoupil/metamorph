Implement a triplet (claim) extraction schema as the atomic unit of structured knowledge for the system, referencing the definition in PIPELINE.md and the ontology. This schema must capture subject, predicate, and object fields, along with provenance (source document, extraction time, method, evidence span), and include extraction and entity-resolution confidence. Define a clear interface for entity linking and pending/shadow entity creation. The triplet schema should be flexible enough to support all knowledge card types, and must be validated against ontology property and cardinality constraints.

Verification & Test Guidance
- [ ] Inspect backend/services/extraction for a module that clearly defines a Triplet or Claim schema with subject, predicate, object, and provenance/confidence.
- [ ] Verify entity linking and shadow creation appear as service/module interfaces and are used during extraction.
- [ ] Check the extraction pipeline for reference to this schema.
- [ ] Ensure that extracted triplets map to the actual ontology node/edge labels and property constraints found in PIPELINE.md and DATABASE.md.
- [ ] Find backend/unit test or API endpoint that allows submitted triplet/claim validation against the schema.
- [ ] Review example usage for all knowledge card types (donor, field, evidence, etc.) and confirm each is supported by the schema structure.
