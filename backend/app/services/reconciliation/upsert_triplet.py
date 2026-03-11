from app.services.extraction.triplet_schema import Triplet, validate_triplet
from typing import Dict


def upsert_triplet_to_graph(triplet: Triplet) -> Dict:
    """
    Upserts both subject, object, and creates edge, using ontology validation and verification.
    """
    # 1. Validate the triplet
    errors = validate_triplet(triplet)
    if errors:
        return {"status": "error", "errors": errors}
    # 2. Upsert subject & object (stub for now)
    # ...actual Neo4j/pgvector upsert here...
    # 3. Create the edge w/ evidence props from metadata
    # ...actual Cypher/graph logic here...
    return {"status": "ok", "triplet": triplet.dict()}
