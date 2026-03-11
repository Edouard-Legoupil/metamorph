from app.services.reconciliation.delta_engine import delta_engine, shadow_update
from app.services.reconciliation.journal import journal_conflict
from app.services.ingestion.graph_db import upsert_triplets_neo4j

# write_triplets_with_reconciliation takes a list of triplets, compares against graph (existing_triplets), journals conflicts,
# performs shadow updates if needed, and writes non-conflicting triplets


def write_triplets_with_reconciliation(
    doc_id: str, triplets: list, existing_triplets: list
):
    new_to_write = []
    for incoming in triplets:
        outcome = delta_engine(incoming, existing_triplets)
        if outcome["outcome"] == "EXPANSION":
            new_to_write.append(incoming)
        elif outcome["outcome"] == "CONFIRMATION":
            # Here you could increment a source/support count, or leave as is.
            continue
        elif outcome["outcome"] == "CONTRADICTION":
            # Journal conflict
            journal_conflict(outcome["conflict_record"])
            if outcome["action"] == "shadow_update":
                shadow_update(outcome["conflict_record"])
            # If you want to insert anyway as a pending node/rel, do so here
            # For now, do not write contradictory data
    if new_to_write:
        upsert_triplets_neo4j(doc_id, new_to_write)
    return new_to_write
