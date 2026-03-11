Implement the triplet extraction schema from the Pipeline Blueprint (Section 2.3) as the atomic unit of knowledge.

Create services/extraction/triplet_schema.py:

1. Triplet data structure:
   {
     "subject": {
       "label": "NodeType from ontology",
       "id": "uuid or null",
       "name": "string",
       "properties": {}  # Extracted properties for new nodes
     },
     "predicate": "EDGE_TYPE from ontology",
     "object": {
       "label": "NodeType from ontology",
       "id": "uuid or null", 
       "name": "string",
       "properties": {}  # Extracted properties for new nodes
     },
     "metadata": {
       "source_document_id": "uuid",
       "source_document_title": "string",
       "extracted_at": "ISO8601",
       "extraction_confidence": 0.0-1.0,
       "page_reference": "integer or null",
       "raw_text_snippet": "string",
       "extraction_method": "LLM | RULE_BASED | HYBRID"
     }
   }

2. Confidence scoring rules:
   - LLM extraction with chain-of-thought: base 0.85, +/- 0.15 based on self-assessment
   - Rule-based extraction (regex, patterns): base 0.70, +/- 0.20 based on pattern strength
   - Hybrid: weighted average of both methods
   - Entity resolution confidence from GLinker: 0.0-1.0

3. Entity resolution interface:
   - resolve_entity(name: str, label: str, context: dict) -> (node_id, confidence)
   - create_pending_entity(name: str, label: str, properties: dict) -> node_id (verification_status: SHADOW)
   - disambiguate_candidates(name: str, label: str) -> list of candidate nodes with scores

4. Validation rules per node/edge type from ontology:
   - Required properties for each node label
   - Cardinality constraints (some edges are one-to-one, others one-to-many)
   - Property type validation (numeric ranges, date formats, ISO codes)

Include example triplets for each knowledge card type:
- KC-1 Donor: (Donor) -[FUNDS]-> (FundingInstrument)
- KC-2 Field: (PopulationGroup) -[DISPLACED_TO]-> (Settlement)
- KC-3 Evidence: (Evaluation) -[PRODUCES]-> (EvidenceFinding)
- KC-4 Partner: (ImplementingPartner) -[IMPLEMENTED_BY]-> (Project)
- KC-5 Track Record: (Operation) -[RESPONDS_TO]-> (Crisis)
- KC-6 Crisis: (ConflictEvent) -[LED_TO]-> (ProtectionIncident)


 
- Integrate this Triplet schema in the core extraction and reconciliation/graph upsert pipelines.
- Implement/proxy resolve_entity, create_pending_entity with entity-linking and shadow entity creation backends.
- Extend validation and cardinality rules for each Ontology update.
- Add  test coverage for triplet schema with a FastAPI endpoint to POST/validate triplets