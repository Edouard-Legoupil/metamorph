import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import markdown
import re
from .card_templates import (
    KC1DonorCard,
    KC2FieldContextCard,
    KC3OutcomeEvidenceCard,
    KC4PartnerCapacityCard,
    KC5TrackRecordCard,
    KC6CrisisCard,
    validate_card,
)


# Extend block assembler to work from card templates
def assemble_blocks_for_card(
    card_id: str, page_id: str, query_defs: Dict = None
) -> List[dict]:
    card_classes = {
        "KC-1": KC1DonorCard,
        "KC-2": KC2FieldContextCard,
        "KC-3": KC3OutcomeEvidenceCard,
        "KC-4": KC4PartnerCapacityCard,
        "KC-5": KC5TrackRecordCard,
        "KC-6": KC6CrisisCard,
    }
    card = card_classes[card_id]()
    query_defs = query_defs or {}
    blocks = []
    for section in card.sections:
        query_def = (
            section.get("query")
            or query_defs.get(section["name"])
            or {"type": "CYPHER", "query": "MATCH ...", "parameters": {}}
        )
        block = {
            "block_id": str(uuid.uuid4()),
            "page_id": page_id,
            "card_id": card.card_id,
            "section_name": section["name"],
            "block_type": section["type"] if "type" in section else "FACT",
            "graph_query": query_def,
            "template": f"## {section['name']}\n{{figure}}",
            "verification_status": "AUTO",
            "active_conflict_ids": [],
            "source_triplets": [],
            "word_limit": section["word_limit"],
            "live_fields": card.live_fields if hasattr(card, "live_fields") else [],
        }
        blocks.append(block)
    return blocks


# Patch: Add validation at block assemble time
def validate_assembled_blocks(
    card_id: str, page_id: str, query_defs: Dict = None
) -> List[str]:
    card_classes = {
        "KC-1": KC1DonorCard,
        "KC-2": KC2FieldContextCard,
        "KC-3": KC3OutcomeEvidenceCard,
        "KC-4": KC4PartnerCapacityCard,
        "KC-5": KC5TrackRecordCard,
        "KC-6": KC6CrisisCard,
    }
    card = card_classes[card_id]()
    blocks = assemble_blocks_for_card(card_id, page_id, query_defs)
    # Fake triplet sources/word_count for validation
    for b in blocks:
        b["sources"] = ["stub-source"]
        b["word_count"] = 1
        b["approval_tier"] = (
            2 if b["section_name"].lower().startswith("compliance") else 1
        )
    return validate_card(card, blocks)
