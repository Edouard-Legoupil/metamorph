from fastapi import APIRouter
from app.services.wiki.block_assembler import assemble_blocks_for_card

router = APIRouter()


@router.get("/card/{card_id}")
def get_blocks_for_card(card_id: str):
    """
    Returns all wiki/card blocks (section blocks) for a given card ID.
    """
    # For demo/testing, use card_id as both card_id and page_id
    blocks = assemble_blocks_for_card(card_id, page_id=card_id)
    return blocks
