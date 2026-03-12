from typing import List, Dict, Any


def extract_triplets_from_markdown(
    markdown: str,
    doc_type: str = "Assessment",
    doc_id: str = None,
    curator_metadata: Dict = None,
) -> Dict[str, Any]:
    """
    Expanded implementation for blueprint-aligned claim extraction from markdown.
    Parses headings, paragraphs, lists, tables for atomic claims. Adds provenance,
    qualifiers, temporal info, evidence, confidence, entity resolution confidence.
    """
    from datetime import datetime
    import re

    lines = markdown.splitlines()
    triplets = []
    section = None
    section_path = []
    for idx, line in enumerate(lines):
        # Headings
        heading_match = re.match(r"^(#+)\s*(.*)", line)
        if heading_match:
            section = heading_match.group(2).strip()
            section_path.append(section)
            continue

        # Table row detection
        if "|" in line and not line.strip().startswith("|"):
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 2:
                subj = parts[0]
                pred_obj = parts[1:]
                for po in pred_obj:
                    triplet = {
                        "subject": {"label": "TableRow", "name": subj},
                        "predicate": "HAS_VALUE",
                        "object": {"label": "Value", "name": po},
                        "qualifiers": {},
                        "temporal": {},
                        "provenance": {
                            "source_document_id": doc_id,
                            "section_path": section_path[-3:],
                            "extraction_method": "MARKDOWN_TABLE_PARSER",
                            "extracted_at": datetime.utcnow().isoformat(),
                            "span_start": idx,
                            "span_end": idx,
                            "raw_text_snippet": line,
                        },
                        "confidence": {
                            "extraction_confidence": 0.91,
                            "entity_resolution_confidence": 0.85,
                        },
                        "status": "proposed",
                    }
                    triplets.append(triplet)
            continue

        # Bullet lists / qualitative claims
        if re.match(r"^\s*[-\*]\s+(.*)$", line):
            claim_txt = re.sub(r"^\s*[-\*]\s+", "", line).strip()
            triplet = {
                "subject": {"label": "ListItem", "name": section or "Uncategorized"},
                "predicate": "ATTRIBUTED_STATEMENT",
                "object": {"label": "Statement", "name": claim_txt},
                "qualifiers": {},
                "temporal": {},
                "provenance": {
                    "source_document_id": doc_id,
                    "section_path": section_path[-3:],
                    "extraction_method": "MARKDOWN_LIST_PARSER",
                    "extracted_at": datetime.utcnow().isoformat(),
                    "span_start": idx,
                    "span_end": idx,
                    "raw_text_snippet": line,
                },
                "confidence": {
                    "extraction_confidence": 0.92,
                    "entity_resolution_confidence": 0.86,
                },
                "status": "proposed",
            }
            triplets.append(triplet)
            continue

        # Temporal detection (rudimentary)
        date_matches = re.findall(r"(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})", line)
        if date_matches and section:
            triplet = {
                "subject": {"label": "Section", "name": section},
                "predicate": "DATED",
                "object": {"label": "Date", "name": date_matches[0]},
                "qualifiers": {},
                "temporal": {"observed_at": date_matches[0]},
                "provenance": {
                    "source_document_id": doc_id,
                    "section_path": section_path[-3:],
                    "extraction_method": "DATE_PARSER",
                    "extracted_at": datetime.utcnow().isoformat(),
                    "span_start": idx,
                    "span_end": idx,
                    "raw_text_snippet": line,
                },
                "confidence": {
                    "extraction_confidence": 0.9,
                    "entity_resolution_confidence": 0.8,
                },
                "status": "proposed",
            }
            triplets.append(triplet)
            continue

        # Heading-to-claim (legacy, now richer)
        if section and line.strip():
            # Qualifier detection example (amount, currency, location)
            amt_match = re.search(r"\$([\d,]+)", line)
            curr_match = re.search(r"(USD|EUR|GBP)", line)
            country_match = re.search(r"\b(Sudan|Ukraine|Yemen|Syria)\b", line)
            qualifiers = {}
            if amt_match:
                qualifiers["amount"] = amt_match.group(1)
            if curr_match:
                qualifiers["currency"] = curr_match.group(1)
            if country_match:
                qualifiers["country"] = country_match.group(1)
            triplet = {
                "subject": {"label": "Section", "name": section},
                "predicate": "MENTIONS",
                "object": {"label": "Document", "name": doc_id},
                "qualifiers": qualifiers,
                "temporal": {},
                "provenance": {
                    "source_document_id": doc_id,
                    "section_path": section_path[-3:],
                    "extraction_method": "HEADING_CLAIM_PARSER",
                    "extracted_at": datetime.utcnow().isoformat(),
                    "span_start": idx,
                    "span_end": idx,
                    "raw_text_snippet": line,
                },
                "confidence": {
                    "extraction_confidence": 0.93,
                    "entity_resolution_confidence": 0.88,
                },
                "status": "proposed",
            }
            triplets.append(triplet)
    # --- Entity Resolution Integration ---
    from app.services.extraction.entity_resolver import resolve_entity

    for triplet in triplets:
        # For subject and object, try resolve
        subj = triplet["subject"]
        obj = triplet["object"]
        if subj and "name" in subj:
            subj_id, subj_conf, subj_candidates = resolve_entity(
                subj["name"], subj.get("label", "Entity"), triplet.get("qualifiers", {})
            )
            if subj_id:
                triplet["subject"]["id"] = subj_id
            triplet["confidence"]["entity_resolution_confidence"] = subj_conf
            triplet["subject"]["candidate_entities"] = subj_candidates
        if obj and "name" in obj:
            obj_id, obj_conf, obj_candidates = resolve_entity(
                obj["name"], obj.get("label", "Entity"), triplet.get("qualifiers", {})
            )
            if obj_id:
                triplet["object"]["id"] = obj_id
            triplet["confidence"]["object_resolution_confidence"] = obj_conf
            triplet["object"]["candidate_entities"] = obj_candidates
    return {"triplets": triplets, "status": "ok", "triplet_count": len(triplets)}
