from fastapi import APIRouter, Body
from typing import List, Dict
from app.services.extraction.triplet_extractor import extract_triplets_from_markdown

router = APIRouter()


@router.post("/batch-extract-triplets")
async def batch_extract_triplets(payload: List[Dict]):
    """
    Takes a batch of documents/markdown, extracts triplets for each. Payload: [{doc_id, markdown, doc_type, metadata}]
    """
    results = []
    for doc in payload:
        out = extract_triplets_from_markdown(
            doc["markdown"], doc["doc_type"], doc["doc_id"], doc.get("metadata", {})
        )
        results.append({"doc_id": doc["doc_id"], "result": out})
    return results
