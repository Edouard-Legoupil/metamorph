import os
from typing import List, Dict, Tuple, Optional
import hashlib
from functools import lru_cache
import uuid


# --- Emulated GLinker Client Stub ---
def glinker_query(name: str, label: str, context: dict = None) -> List[Dict]:
    # Placeholder for real GLinker API
    # Match on domain-aware, type-specific fields (see below)
    # Return sorted [{"id": "...", "name": str, "label": str, "confidence": float, "aliases": [...], "properties": {...}}]
    # For now, returns 1 random high-confidence candidate for demo
    id_ = str(uuid.uuid5(uuid.NAMESPACE_DNS, (name + label).lower()))
    return [
        {
            "id": id_,
            "name": name,
            "label": label,
            "confidence": 0.91,
            "aliases": [name.lower()],
            "properties": context or {},
        }
    ]


# --- Resolution Cache (name+label) -> result (auto invalidates on process restart or cache clear) ---
@lru_cache(maxsize=2048)
def resolve_entity_cached(name: str, label: str) -> Optional[Dict]:
    candidates = glinker_query(name, label)
    if not candidates:
        return None
    best = max(candidates, key=lambda c: c["confidence"])
    return best


# --- Resolution Strategies per Type ---
def resolve_geographic(name: str, properties: dict) -> List[Dict]:
    # Prefer ISO/pcode/coords similarity
    iso = properties.get("iso3")
    pcode = properties.get("pcode")
    # Call GLinker with augmented context
    return glinker_query(name, "GeographicEntity", {"iso3": iso, "pcode": pcode})


def resolve_organization(name: str, properties: dict) -> List[Dict]:
    # Use acronyms, aliases, reg ID
    alias = properties.get("acronym") or name.split()[0][:3]
    regid = properties.get("registration_id")
    return glinker_query(
        name, "Organisation", {"acronym": alias, "registration_id": regid}
    )


def resolve_policy(name: str, properties: dict) -> List[Dict]:
    code = properties.get("policyCode")
    version = properties.get("version", None)
    context = {"policyCode": code, "version": version}
    return glinker_query(name, "Policy", context)


def resolve_population_group(name: str, properties: dict) -> List[Dict]:
    # Use descriptive+location
    demog = properties.get("groupType")
    loc = properties.get("location")
    context = {"groupType": demog, "location": loc}
    return glinker_query(name, "PopulationGroup", context)


# --- Decision Logic ---
def resolve_entity(
    name: str, label: str, properties: dict
) -> Tuple[Optional[str], float, List[Dict]]:
    """
    Return (node_id_to_link [or None], confidence, candidates)
    """
    # Dispatch by label
    if label in ("Country", "Region", "GeographicEntity"):
        candidates = resolve_geographic(name, properties)
    elif label in ("Organisation", "ImplementingPartner", "Donor"):
        candidates = resolve_organization(name, properties)
    elif label in ("Policy", "SOP", "LegalFramework"):
        candidates = resolve_policy(name, properties)
    elif label in ("PopulationGroup",):
        candidates = resolve_population_group(name, properties)
    else:
        candidates = glinker_query(name, label, properties)
    best = max(candidates, key=lambda c: c["confidence"], default=None)
    confidence = best["confidence"] if best else 0
    if confidence >= 0.95:
        return best["id"], confidence, candidates
    if 0.70 <= confidence < 0.95:
        # Create shadow node, log for curator review
        return None, confidence, candidates
    return None, confidence, candidates


# --- Merge Property and Alias Handling ---
def merge_properties(existing: dict, incoming: dict) -> dict:
    # Merge, create conflict record if needed
    for k, v in incoming.items():
        if k not in existing or existing[k] == v:
            existing[k] = v
        elif existing[k] != v:
            # Create a ConflictRecord (just logging for now)
            print(f"Conflict for {k}: '{existing[k]}' vs '{v}'")
    return existing


def add_alias(entity: dict, alias: str, source: str = None, confidence: float = 1.0):
    aliases = entity.setdefault("aliases", [])
    if alias not in aliases:
        aliases.append(alias)
    # Track confidence/source if system supports


# --- For search-by-alias/results as well ---
def search_by_alias(alias: str, label: str) -> List[Dict]:
    # For real: query all entities for alias matches
    return glinker_query(alias, label)


# --- For cache invalidation (on graph updates or entity merge) ---
def invalidate_cache_for(name: str, label: str):
    key = (name, label)
    resolve_entity_cached.cache_clear()


# === SHADOW NODE/STATUS MANAGEMENT ===
def create_shadow_entity(name: str, label: str, properties: dict) -> Dict:
    shadow_id = f"shadow-{uuid.uuid4()}"
    node = {
        "id": shadow_id,
        "name": name,
        "label": label,
        "status": "SHADOW",
        "properties": properties or {},
    }
    # Real: Store in Neo4j with status=SHADOW
    return node
