Implement entity resolution service based on Pipeline Blueprint Section 2.3.4.

Create services/extraction/entity_resolver.py:

1. GLinker integration:
   - Configure for humanitarian entity types (donors, countries, organizations, policies)
   - Train/adapt for domain-specific entities
   - Return candidate matches with confidence scores

2. Resolution strategies per entity type:
   - Geographic: Use ISO codes, p-codes, coordinates
   - Organizational: Use acronyms, aliases, registration IDs
   - Policy documents: Use document codes, version numbers
   - Population groups: Use demographic descriptors + location

3. Resolution decision logic:
   IF confidence >= 0.95:
       Auto-link to existing node
   IF confidence between 0.70 and 0.95:
       Create shadow node with PENDING status
       Store candidate matches for curator review
   IF confidence < 0.70:
       Create new node with SHADOW status
       Flag for human verification (Tier 1)

4. Property merging rules:
   - When linking to existing node, merge new properties
   - For conflicting properties, create ConflictRecord
   - Append source documents to node.source_documents

5. Alias management:
   - Store all resolved entity names as aliases
   - Enable search by any alias
   - Track alias confidence and source

6. Resolution cache:
   - Cache resolved entities by name+type
   - Invalidate on graph updates
   - Reduce API calls to GLinker