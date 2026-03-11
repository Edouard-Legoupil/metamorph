from fastapi import APIRouter, Query, Body
from app.services.wiki.block_assembler import (
    assemble_blocks_for_card,
    render_live_block,
    QueryExecutor,
    BlockTemplateRenderer,
)
from app.services.trust.community_trust import (
    BlockTrust,
    ReadTracker,
    flag_block,
    get_verification_icon,
)
from typing import Dict

# In-memory block trust store (demo only; should be persisted/DB-backed)
block_trust_store = {}

router = APIRouter()


@router.get("/card/{card_id}/preview")
def get_card_block_preview(
    card_id: str, page_id: str, section: str = Query(None), user_id: str = None
):
    blocks = assemble_blocks_for_card(card_id, page_id)
    if section:
        blocks = [b for b in blocks if b["section_name"] == section]
    executor = QueryExecutor()
    renderer = BlockTemplateRenderer()
    content = []
    for b in blocks:
        block_id = b["block_id"]
        trust = block_trust_store.setdefault(block_id, BlockTrust(block_id))
        if user_id:
            if ReadTracker.record_read(block_id, user_id):
                trust.increment_read(user_id)
        block_md = render_live_block(b, executor, renderer)
        icon = get_verification_icon(trust)
        content.append(
            {
                "block_id": block_id,
                "section_name": b["section_name"],
                "markdown": block_md,
                "community_trust_score": trust.community_trust_score,
                "verification_status": trust.verification_status,
                "verification_icon": icon,
            }
        )
    return {"blocks": content}


@router.post("/block/{block_id}/verify")
def post_block_verify(block_id: str, user_id: str = Body(...)):
    trust = block_trust_store.setdefault(block_id, BlockTrust(block_id))
    trust.increment_verify(user_id)
    return {
        "block_id": block_id,
        "score": trust.community_trust_score,
        "status": trust.verification_status,
    }


@router.post("/block/{block_id}/flag")
def post_block_flag(block_id: str, user_id: str = Body(...)):
    trust = block_trust_store.setdefault(block_id, BlockTrust(block_id))
    trust = flag_block(trust, user_id)
    return {
        "block_id": block_id,
        "status": trust.verification_status,
        "score": trust.community_trust_score,
        "flags": list(trust._flags),
    }
