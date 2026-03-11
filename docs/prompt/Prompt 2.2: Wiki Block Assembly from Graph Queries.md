Implement the wiki block system from Pipeline Blueprint Section 3.3 and Knowledge Card YAML.

Create services/wiki/block_assembler.py:

1. Block definition schema:
   {
     "block_id": "uuid",
     "page_id": "uuid",
     "card_id": "KC-1|KC-2|KC-3|KC-4|KC-5|KC-6",
     "section_name": "string",  # matches knowledge card sections
     "block_type": "FACT|STATISTIC|POLICY_SUMMARY|CONTACT|PROCEDURE|EVIDENCE",
     "graph_query": {
       "type": "CYPHER|AQL",
       "query": "string",
       "parameters": {}  # e.g., {"country": "node_id", "crisis": "node_id"}
     },
     "template": "markdown_template_string with {placeholders}",
     "verification_status": "AUTO|PENDING|VERIFIED",
     "active_conflict_ids": ["conflict_id"],
     "source_triplets": ["triplet_id"],
     "word_limit": "integer",  # from knowledge card
     "live_fields": ["field_names"]  # exempt from human lock
   }

2. Graph query executor:
   - Execute query at render time (real-time data)
   - Cache results with TTL based on data volatility
   - Handle query failures gracefully
   - Return structured data for template filling

3. Template renderer:
   - Fill markdown templates with query results
   - Format numbers with thousand separators
   - Format dates consistently
   - Handle null/missing data with "Data Gap" flags

4. Knowledge card section mapping:
   - Load all sections from knowledge-card.yaml
   - Map each section to block definitions
   - Enforce word limits in UI
   - Validate required sections per card

5. Live field handling:
   - Fields in live_fields bypass human approval
   - Update directly from graph on render
   - Mark as "Auto-updated" in UI
   - Track update history

6. Conflict display logic:
   - If active_conflict_ids exists, show conflict banner
   - Display both values with sources
   - Include resolution interface for authorized users