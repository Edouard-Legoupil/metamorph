Use instruction within the AGENT.md - Based on the provided Turtle ontology (`unhcr-knowledge-ontology.ttl`) within the ontology folder, implement the graph database schema for Metamorph.

Build the graph database schema for Metamorph using the ontology found in docs/ontology/unhcr-knowledge-ontology.ttl. For every ontology class, add a graph node label with core and domain properties, using the ontology’s property and type definitions. Each relationship in the ontology should appear as an edge type, with direction, cardinality, and property constraints as indicated. All nodes/edges must support versioning, identifiers, provenance, and verification status, with supporting indexes and constraints for identity, text, and geospatial search. Initial loader should seed authoritative master/reference data. The schema and lifecycle must be documented in DATABASE.md and PIPELINE.md.

Verification & Test Guidance
- [ ] Inspect backend/services/graph or a corresponding module for a schema/adapter that registers all ontology-specified node/edge types.
- [ ] Confirm all required properties and relationship directions, indexes, and versioning fields are implemented.
- [ ] Ensure at least one loader script seeds countries/master data.
- [ ] Validate documentation in DATABASE.md/PIPELINE.md describing canonical schema and mapping to ontology.
- [ ] Check presence of automated tests for node/edge creation, property constraints, version/time-series retrieval, and relationship traversal.



Indexes & Constraints:

   Unique constraint on identifier for all nodes.

   Index on name (if present) and hasTag for text search.

   Geospatial index on geo:lat/geo:long for location queries.

   Composite indexes for frequently queried property combinations (e.g., country + crisis).

   Full‑text search indexes on textual properties like title, description, raw_text_snippet.

Implementation Details:

   Use Neo4j 5+ with APOC library for advanced graph procedures.

   Use the neo4j Python driver (async) in the backend.

   Provide a set of Cypher scripts to create the schema, indexes, and constraints.

   Include a script to seed the graph with initial reference data (e.g., countries, standard indicators).

Testing:

   Provide unit tests that verify node creation, property assignment, and relationship traversal.

   Include tests for temporal versioning queries (retrieving latest value, historical trend).