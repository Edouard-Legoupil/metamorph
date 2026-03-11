from fastapi import APIRouter
from app.services.wiki.card_templates import (
    KC1DonorCard,
    KC2FieldContextCard,
    KC3OutcomeEvidenceCard,
    KC4PartnerCapacityCard,
    KC5TrackRecordCard,
    KC6CrisisCard,
)
from app.services.wiki.block_assembler import validate_assembled_blocks

router = APIRouter()


@router.get("/enumerate-cards")
def get_card_templates():
    cards = [
        KC1DonorCard(),
        KC2FieldContextCard(),
        KC3OutcomeEvidenceCard(),
        KC4PartnerCapacityCard(),
        KC5TrackRecordCard(),
        KC6CrisisCard(),
    ]
    return [
        {
            "card_id": c.card_id,
            "title": c.title,
            "description": c.description,
            "sections": getattr(c, "sections", []),
        }
        for c in cards
    ]


@router.get("/validate-card/{card_id}")
def validate_card_route(card_id: str):
    # Returns list of errors (empty if valid for default queries/sections)
    errors = validate_assembled_blocks(card_id, "ui-page-test")
    return {"errors": errors}
