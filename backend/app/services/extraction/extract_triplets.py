from .triplet_schema import (
    Triplet,
    validate_triplet,
    resolve_entity,
    create_pending_entity,
)
from typing import List, Dict


def extract_triplets(
    document_text: str, extraction_method: str, metadata: Dict
) -> List[Triplet]:
    """
    Runs extraction (LLM/rules), resolves entities, builds Triplet objects.
    """
    # This is a stub; in reality, your LLM or rule engine would generate these dicts:
    extracted = [
        {
            "subject": {
                "label": "Donor",
                "name": "USAID",
                "properties": {"name": "USAID"},
            },
            "predicate": "FUNDS",
            "object": {
                "label": "FundingInstrument",
                "name": "2024 HIP",
                "properties": {"amountUsd": 100000},
            },
            "metadata": {
                **metadata,
                "raw_text_snippet": "USAID will fund the 2024 Humanitarian Implementation Plan...",
                "extraction_method": extraction_method,
            },
        }
        # ... more extracted triplets ...
    ]
    triplets = []
    for t in extracted:
        # Resolve or create both subject and object nodes
        sub_id, sub_conf = resolve_entity(
            t["subject"]["name"],
            t["subject"]["label"],
            t["subject"].get("properties", {}),
        )
        if not sub_id:
            sub_id = create_pending_entity(
                t["subject"]["name"],
                t["subject"]["label"],
                t["subject"].get("properties", {}),
            )
        obj_id, obj_conf = resolve_entity(
            t["object"]["name"], t["object"]["label"], t["object"].get("properties", {})
        )
        if not obj_id:
            obj_id = create_pending_entity(
                t["object"]["name"],
                t["object"]["label"],
                t["object"].get("properties", {}),
            )
        t["subject"]["id"] = sub_id
        t["object"]["id"] = obj_id
        triplets.append(Triplet(**t))
    return triplets
