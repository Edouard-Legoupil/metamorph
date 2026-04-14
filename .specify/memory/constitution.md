# Metamorph Constitution

## 1. Project Principles
- **Human judgment is not optional:** The system assists curators; it does not replace judgment.
- **Every claim must be traceable:** Provenance, document source, date, and curator must be stored for every piece of knowledge.
- **Honesty over presentation:** Surface difficulties, risks, and gaps.
- **Expiry is a feature:** Validity periods are enforced for all knowledge cards.

## 2. Technical Stack
- **Document Parsing:** Docling, MinerU
- **Graph Storage:** Neo4j (or similar Labeled Property Graph)
- **API:** FastAPI/GraphQL
- **Agentic System:** Mistral Vibe CLI, Claude Code, etc.

## 3. Workflow
1. Ingest and extract knowledge from documents.
2. Reconcile and update the knowledge graph.
3. Generate and curate knowledge cards.
4. Draft proposals using agentic systems.

## 4. Data Model
- **Nodes:** Documents, entities, events, interventions, outcomes.
- **Edges:** Relationships (e.g., "funded by", "affected by").
- **Properties:** Provenance, validity period, curator, status.