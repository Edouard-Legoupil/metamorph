from typing import Dict, Any, Optional, Tuple, List
from uuid import uuid4
from datetime import datetime
import difflib
import math

# 1. Triplet comparison logic


def triplet_key(triplet: Dict) -> Tuple:
    s = triplet["subject"].get("id") or triplet["subject"].get("name")
    return (s, triplet["predicate"])


def compare_numeric(val1, val2, tolerance=0.05):
    try:
        v1 = float(val1)
        v2 = float(val2)
        if v1 == 0 and v2 == 0:
            return True
        if v1 == 0 or v2 == 0:
            return False
        perc_diff = abs(v1 - v2) / max(abs(v1), abs(v2))
        return perc_diff <= tolerance
    except Exception:
        return False


def compare_text_semantic(text1, text2, threshold=0.8):
    # Use difflib ratio as rough semantic sim, real system: embedder/cosine
    ratio = difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    return ratio >= threshold


def compare_contact(obj1: Dict, obj2: Dict) -> bool:
    # Exact match for all contact fields
    fields = ["email", "phone", "website", "address"]
    for f in fields:
        if obj1.get(f) != obj2.get(f):
            return False
    return True


# 2. Conflict classification


def classify_conflict(
    existing: Dict, incoming: Dict, predicate: str
) -> Tuple[str, str]:
    # Determine conflict_type, severity
    # Quantitative
    if predicate in (
        "POPULATION_FIGURE",
        "INDICATOR_VALUE",
        "BUDGET",
    ):  # Extend per ontology
        existing_value = existing["object"].get("numericValue") or existing[
            "object"
        ].get("populationFigure")
        incoming_value = incoming["object"].get("numericValue") or incoming[
            "object"
        ].get("populationFigure")
        if not compare_numeric(existing_value, incoming_value, tolerance=0.10):
            diff_pct = abs(float(existing_value) - float(incoming_value)) / max(
                abs(float(existing_value)), abs(float(incoming_value))
            )
            ctype = "QUANTITATIVE"
            severity = "CRITICAL" if diff_pct > 0.1 else "MINOR"
            return ctype, severity
    # Normative
    if predicate in ("APPLIES_TO", "SUPERSEDES", "GOVERNS"):
        text1 = existing["object"].get("textValue") or ""
        text2 = incoming["object"].get("textValue") or ""
        if not compare_text_semantic(text1, text2):
            keywords = ["mandatory", "shall", "right", "prohibited"]
            t1 = text1.lower()
            t2 = text2.lower()
            is_critical = any(k in t1 or k in t2 for k in keywords)
            return "NORMATIVE", "CRITICAL" if is_critical else "MINOR"
    # Contact
    if predicate == "CONTACT":
        if not compare_contact(existing["object"], incoming["object"]):
            return "CONTACT", "CRITICAL" if existing["object"].get(
                "person"
            ) != incoming["object"].get("person") else "MINOR"
    # Structural
    if predicate != incoming.get("predicate"):
        return "STRUCTURAL", "CRITICAL"
    # Default
    return "STRUCTURAL", "MINOR"


# 3. ConflictRecord schema
def make_conflict_record(
    subject, predicate, existing, incoming, conflict_type, severity
) -> Dict:
    return {
        "conflict_id": str(uuid4()),
        "subject": subject,
        "predicate": predicate,
        "existing_value": existing,
        "incoming_value": incoming,
        "conflict_type": conflict_type,
        "severity": severity,
        "status": "UNRESOLVED",
        "assigned_to_tier": 2 if severity == "CRITICAL" else 1,
        "resolution_notes": "",
        "resolved_at": None,
        "resolved_by": None,
    }


# 4. Delta Engine Main


def delta_engine(triplet: Dict, existing_triplets: List[Dict]) -> Dict[str, Any]:
    """
    Compares incoming triplet to existing set and returns routing/outcome info.
    """
    key = triplet_key(triplet)
    matches = [t for t in existing_triplets if triplet_key(t) == key]
    if not matches:
        # EXPANSION
        return {
            "outcome": "EXPANSION",
            "action": "route_by_confidence",
            "triplet": triplet,
        }

    for ex in matches:
        # Check for confirmation (exact)
        if ex["object"] == triplet["object"]:
            return {
                "outcome": "CONFIRMATION",
                "action": "increment_source_count",
                "triplet": triplet,
            }
        # Else check conflict
        ctype, severity = classify_conflict(ex, triplet, triplet["predicate"])
        conflict = make_conflict_record(
            triplet["subject"], triplet["predicate"], ex, triplet, ctype, severity
        )
        r = {
            "outcome": "CONTRADICTION",
            "conflict_record": conflict,
            "action": "human_escalation" if severity == "CRITICAL" else "shadow_update",
            "triplet": triplet,
        }
        return r
    # Shouldn't reach here for multi-matches; fallback to shadow update
    return {"outcome": "CONTRADICTION", "action": "shadow_update", "triplet": triplet}


# 5. Shadow update logic
def shadow_update(conflict_record: Dict):
    # Stub: in real system, mark wiki with banner, append pending value, enter async review
    # and allow UI actions
    print("Shadow update for wiki pending review: ", conflict_record)
    # Real: upsert to graph/wiki, notify
    return True
