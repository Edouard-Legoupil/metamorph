Implement the Delta Engine from Pipeline Blueprint Section 3.2 for triplet reconciliation.

Create services/reconciliation/delta_engine.py:

1. Triplet comparison logic:
   - Match by (subject_id, predicate) or (subject_name, predicate) if IDs not yet assigned
   - For quantitative predicates: compare numeric values with tolerance
   - For normative predicates: compare text with semantic similarity
   - For contact predicates: exact match required

2. Conflict classification (per Pipeline Blueprint 3.2.1):
   conflict_type:
     - QUANTITATIVE: Numeric values differ
     - NORMATIVE: Policy/legal text differs
     - CONTACT: Contact details differ
     - STRUCTURAL: Relationship type differs
   
   severity (per 4.2.2 rules):
     - CRITICAL: 
       * Quantitative change >10% in safety metrics
       * Normative keywords: "Mandatory", "Shall", "Right", "Prohibited"
       * Contact person replacement
       * Policy supersession without explicit edge
     - MINOR:
       * Quantitative change ≤10%
       * Editorial rewording
       * Secondary contact update

3. ConflictRecord schema:
   {
     "conflict_id": "uuid",
     "subject": {"id": "uuid", "label": "NodeType", "name": "string"},
     "predicate": "EDGE_TYPE",
     "existing_value": {
       "object": {},  # node or literal
       "source_document_id": "uuid",
       "source_date": "ISO8601",
       "extraction_date": "ISO8601"
     },
     "incoming_value": {
       "object": {},
       "source_document_id": "uuid", 
       "source_date": "ISO8601",
       "extraction_date": "ISO8601"
     },
     "conflict_type": "QUANTITATIVE|NORMATIVE|CONTACT|STRUCTURAL",
     "severity": "CRITICAL|MINOR",
     "status": "UNRESOLVED|RESOLVED|ACKNOWLEDGED",
     "assigned_to_tier": 1|2|3,
     "resolution_notes": "string",
     "resolved_at": "ISO8601",
     "resolved_by": "staff_id"
   }

4. Outcome routing (per Pipeline Blueprint 7.1):
   - EXPANSION: New triplet, no conflict → route by confidence
   - CONFIRMATION: Exact match → increment source count
   - CONTRADICTION: Different value → create ConflictRecord
     * CRITICAL → 🔴 Human Escalation (Tier 2+)
     * MINOR → 🟡 Shadow Update

5. Shadow update implementation:
   - Update wiki with pending verification tag
   - Display both values in conflict banner
   - Enter async review queue
   - Allow users to verify/flag while pending


- Integrate this into the triplet ingestion pipeline, so all incoming graph writes are reconciled/journaled.
- Add a REST endpoint for curator/agent review.
- Hook shadow updates to the wiki/notification system or add batch processing for incoming triplets.   