from typing import List, Dict, Any


def extract_triplets_from_markdown(
    markdown: str,
    doc_type: str = "Assessment",
    doc_id: str = None,
    curator_metadata: Dict = None,
) -> Dict[str, Any]:
    """
    Dummy implementation for triplet extraction. Replace with your pipeline logic.
    """
    # Example: Split markdown into lines and create a fake triplet per heading
    triplets = []
    for line in markdown.splitlines():
        if line.startswith("#"):
            triplet = {
                "subject": {"label": "Section", "name": line.strip("# ").strip()},
                "predicate": "MENTIONS",
                "object": {"label": "Document", "name": doc_id},
                "metadata": {
                    "source_document_id": doc_id,
                    "extraction_confidence": 0.95,
                    "raw_text_snippet": line,
                    "extraction_method": "STUB",
                },
            }
            triplets.append(triplet)
    return {"triplets": triplets, "status": "ok", "triplet_count": len(triplets)}
