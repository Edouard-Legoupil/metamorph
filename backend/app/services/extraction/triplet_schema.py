from typing import Optional, Dict, Any, List, Tuple, Literal, Union
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, validator, constr
import re


# === Atomic Triplet Data Structure ===
class TripletEntity(BaseModel):
    label: str  # Ontology NodeType
    id: Optional[Union[UUID, str]] = None
    name: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class TripletMetadata(BaseModel):
    source_document_id: Union[UUID, str]
    source_document_title: str
    extracted_at: str
    extraction_confidence: float
    page_reference: Optional[int] = None
    raw_text_snippet: str
    extraction_method: Literal["LLM", "RULE_BASED", "HYBRID"]


class Triplet(BaseModel):
    subject: TripletEntity
    predicate: str  # Ontology EDGE_TYPE
    object: TripletEntity
    metadata: TripletMetadata


# === Entity Resolution Interface (stubs) ===
def resolve_entity(name: str, label: str, context: dict) -> Tuple[Optional[str], float]:
    """
    Return (node_id, confidence) from entity linker/GLinker.
    """
    # Dummy example logic
    # Real implementation would call GLinker or similar
    node_id = None
    confidence = 0.5
    return node_id, confidence


def create_pending_entity(name: str, label: str, properties: dict) -> str:
    """
    Create node in DB with verification_status=SHADOW, return ID.
    """
    return "shadow-id-{}-{}".format(label, re.sub(r"[^a-zA-Z0-9]", "", name))


def disambiguate_candidates(name: str, label: str) -> List[Dict[str, Any]]:
    """
    Return candidate nodes with confidence scores.
    """
    return []  # Stub


# === Confidence Scoring Rules ===
def score_confidence(
    extraction_method: Literal["LLM", "RULE_BASED", "HYBRID"],
    self_reported_score: Optional[float] = None,
    pattern_strength: Optional[float] = None,
    llm_weight: float = 0.5,
    rule_weight: float = 0.5,
) -> float:
    if extraction_method == "LLM":
        base = 0.85
        if self_reported_score is not None:
            return max(0, min(1, base + (self_reported_score - 0.85)))
        return base
    elif extraction_method == "RULE_BASED":
        base = 0.70
        if pattern_strength is not None:
            return max(0, min(1, base + (pattern_strength - 0.7)))
        return base
    elif extraction_method == "HYBRID":
        # Weighted average
        llm_score = self_reported_score or 0.85
        rule_score = pattern_strength or 0.7
        return max(
            0,
            min(
                1,
                (llm_score * llm_weight + rule_score * rule_weight)
                / (llm_weight + rule_weight),
            ),
        )
    return 0.5


# === Validation Rules Example (Ontology-Driven) ===
REQUIRED_PROPERTIES = {
    "Country": ["iso3", "name"],
    "Donor": ["name"],
    "FundingInstrument": ["amountUsd"],
    "PopulationGroup": ["groupType"],
    "Settlement": ["settlementType", "name"],
    "ImplementingPartner": ["name"],
    "Project": ["projectCode"],
    "Operation": ["operationCode"],
    "Crisis": [],
    "ConflictEvent": ["name"],
    "ProtectionIncident": ["name"],
    # ... extend for all node types ...
}

PROPERTY_TYPES = {
    "iso3": constr(pattern=r"^[A-Z]{3}$"),
    "amountUsd": float,
    "groupType": str,
    "populationFigure": int,
    "projectCode": str,
    "operationCode": str,
    "date": constr(pattern=r"^\d{4}-\d{2}-\d{2}$"),
}

CARDINALITY_CONSTRAINTS = {
    # Example: Donor FUNDS FundingInstrument is many-to-many
    ("Donor", "FUNDS", "FundingInstrument"): "M:N",
    ("PopulationGroup", "DISPLACED_TO", "Settlement"): "M:N",
    ("Evaluation", "PRODUCES", "EvidenceFinding"): "1:N",
    ("ImplementingPartner", "IMPLEMENTED_BY", "Project"): "1:N",
    ("Operation", "RESPONDS_TO", "Crisis"): "M:N",
    ("ConflictEvent", "LED_TO", "ProtectionIncident"): "M:N",
}


def validate_triplet(triplet: Triplet) -> List[str]:
    errors = []
    for node in [triplet.subject, triplet.object]:
        label = node.label
        for prop in REQUIRED_PROPERTIES.get(label, []):
            if prop not in node.properties:
                errors.append(f"Missing required property '{prop}' for {label}")
            elif label in PROPERTY_TYPES and not isinstance(
                node.properties[prop], PROPERTY_TYPES[prop]
            ):
                errors.append(f"Type error for property '{prop}' on {label}")
    # Custom type and value checks can go here
    # TODO: Edge cardinality logic hook
    return errors


# === Example Triplets for Each Knowledge Card Type ===
EXAMPLES = {
    # KC-1 Donor
    "donor": Triplet(
        subject=TripletEntity(
            label="Donor", id=None, name="USAID", properties={"name": "USAID"}
        ),
        predicate="FUNDS",
        object=TripletEntity(
            label="FundingInstrument",
            id=None,
            name="2024 HIP",
            properties={"amountUsd": 1000000},
        ),
        metadata=TripletMetadata(
            source_document_id="doc-123",
            source_document_title="HIP 2024",
            extracted_at=datetime.utcnow().isoformat(),
            extraction_confidence=0.9,
            page_reference=7,
            raw_text_snippet="USAID will fund the 2024 Humanitarian Implementation Plan...",
            extraction_method="LLM",
        ),
    ),
    # KC-2 Field
    "field": Triplet(
        subject=TripletEntity(
            label="PopulationGroup",
            id=None,
            name="South Sudanese refugees",
            properties={"groupType": "Refugee"},
        ),
        predicate="DISPLACED_TO",
        object=TripletEntity(
            label="Settlement",
            id=None,
            name="Bidi Bidi",
            properties={"settlementType": "Camp"},
        ),
        metadata=TripletMetadata(
            source_document_id="doc-222",
            source_document_title="2024 Refugee Registration",
            extracted_at=datetime.utcnow().isoformat(),
            extraction_confidence=0.88,
            page_reference=3,
            raw_text_snippet="...moved to Bidi Bidi settlement...",
            extraction_method="HYBRID",
        ),
    ),
    # KC-3 Evidence
    "evidence": Triplet(
        subject=TripletEntity(
            label="Evaluation", id=None, name="Final Eval2023", properties={}
        ),
        predicate="PRODUCES",
        object=TripletEntity(
            label="EvidenceFinding",
            id=None,
            name="Improved Wash",
            properties={"textValue": "Hygiene indicators improved"},
        ),
        metadata=TripletMetadata(
            source_document_id="doc-eval",
            source_document_title="Evaluation 2023",
            extracted_at=datetime.utcnow().isoformat(),
            extraction_confidence=0.95,
            page_reference=12,
            raw_text_snippet="...Evaluation shows hygiene improved...",
            extraction_method="LLM",
        ),
    ),
    # KC-4 Partner
    "partner": Triplet(
        subject=TripletEntity(
            label="ImplementingPartner", id=None, name="RedCross", properties={}
        ),
        predicate="IMPLEMENTED_BY",
        object=TripletEntity(
            label="Project",
            id=None,
            name="Child Health",
            properties={"projectCode": "PRJ-124"},
        ),
        metadata=TripletMetadata(
            source_document_id="doc-partner",
            source_document_title="Partner List",
            extracted_at=datetime.utcnow().isoformat(),
            extraction_confidence=0.86,
            page_reference=None,
            raw_text_snippet="Project implemented by RedCross...",
            extraction_method="RULE_BASED",
        ),
    ),
    # KC-5 Track Record
    "track": Triplet(
        subject=TripletEntity(
            label="Operation",
            id=None,
            name="Uganda Mission",
            properties={"operationCode": "UG-2024"},
        ),
        predicate="RESPONDS_TO",
        object=TripletEntity(
            label="Crisis", id=None, name="South Sudan Crisis", properties={}
        ),
        metadata=TripletMetadata(
            source_document_id="doc-crisis",
            source_document_title="Ops Report",
            extracted_at=datetime.utcnow().isoformat(),
            extraction_confidence=0.87,
            page_reference=20,
            raw_text_snippet="Operates in response to the South Sudan crisis...",
            extraction_method="HYBRID",
        ),
    ),
    # KC-6 Crisis
    "crisis": Triplet(
        subject=TripletEntity(
            label="ConflictEvent", id=None, name="2022 Border Skirmish", properties={}
        ),
        predicate="LED_TO",
        object=TripletEntity(
            label="ProtectionIncident", id=None, name="Village attack", properties={}
        ),
        metadata=TripletMetadata(
            source_document_id="doc-conflict",
            source_document_title="Conflict Log",
            extracted_at=datetime.utcnow().isoformat(),
            extraction_confidence=0.91,
            page_reference=5,
            raw_text_snippet="2022 Border Skirmish led to attack in Amuru...",
            extraction_method="LLM",
        ),
    ),
}
