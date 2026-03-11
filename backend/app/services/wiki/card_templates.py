import datetime
from typing import List, Dict, Any


class BaseCard:
    card_id: str
    title: str
    description: str
    valid_until_default: int  # in months
    graph_query_anchors: List[str]
    proposal_sections_fed: List[str]

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


# === KC-1 Donor Intelligence Card ===
class KC1DonorCard(BaseCard):
    card_id = "KC-1"
    title = "Donor Intelligence Card"
    description = "Comprehensive profile of donor, funding, alignment, and contacts."
    valid_until_default = 12
    graph_query_anchors = ["Donor"]
    proposal_sections_fed = ["donor_overview", "contacts", "funding_history"]
    sections = [
        {
            "name": "Donor Overview",
            "word_limit": 80,
            "query": {
                "type": "CYPHER",
                "query": "MATCH (d:Donor {id: $donor_id}) RETURN d.name, d.iso3, d.description, d.website",
            },
        },
        {
            "name": "Organisational Structure",
            "word_limit": 60,
            "query": {
                "type": "CYPHER",
                "query": "MATCH (d:Donor {id: $donor_id})-[:HAS_CONTACT]->(f:FocalPoint) RETURN f.name, f.position",
            },
        },
        {
            "name": "Funding History",
            "word_limit": 75,
            "query": {
                "type": "CYPHER",
                "query": "MATCH (d:Donor {id: $donor_id})-[:FUNDS]->(fi:FundingInstrument) RETURN fi.amountUsd, fi.date",
            },
        },
        {
            "name": "Strategic Alignment",
            "word_limit": 65,
            "query": {
                "type": "CYPHER",
                "query": "MATCH (d:Donor {id:$donor_id})-[:ENDORSES]->(p:Policy) RETURN p.title, p.effective_date",
            },
        },
        {
            "name": "Active Pledges",
            "word_limit": 20,
            "query": {
                "type": "CYPHER",
                "query": "MATCH (d:Donor {id: $donor_id})-[:COMMITTED_TO]->(p:PledgeCommitment) RETURN p.",
            },
        },
        {"name": "Contact Details", "word_limit": 30, "live": True},
        {"name": "Key Contacts List", "word_limit": 20, "live": True},
        # ...more, up to 12 sections from YAML...
    ]
    live_fields = ["Contact Details", "Key Contacts List"]


# === KC-2 Field Context Card ===
class KC2FieldContextCard(BaseCard):
    card_id = "KC-2"
    title = "Field Context Card"
    description = "Contextual operational and protection profile by field location."
    valid_until_default = 12
    graph_query_anchors = ["Region", "PopulationGroup"]
    proposal_sections_fed = [
        "protection_landscape",
        "population_profile",
        "socio_economic",
        "stakeholder_landscape",
    ]
    sections = [
        {
            "name": "Protection Landscape",
            "word_limit": 100,
            "query": {
                "type": "CYPHER",
                "query": "MATCH (l:LegalFramework)-[:COVERS]->(p:ProtectionIncident) RETURN l.name, p.description",
            },
        },
        {
            "name": "Population Profile",
            "word_limit": 80,
            "query": {
                "type": "CYPHER",
                "query": "MATCH (pg:PopulationGroup)-[:DISPLACED_TO]->(r:Region) RETURN pg.groupType, pg.estimatedSize",
            },
        },
        {
            "name": "Socio-Economic",
            "word_limit": 75,
            "query": {
                "type": "CYPHER",
                "query": "MATCH (i:Indicator)-[:RECORDED_IN]->(a:Assessment) RETURN i.indicatorCode, i.numericValue",
            },
        },
        {
            "name": "Stakeholder Landscape",
            "word_limit": 65,
            "query": {
                "type": "CYPHER",
                "query": "MATCH (ip:ImplementingPartner)-[:OPERATES_IN]->(r:Region) RETURN ip.name, ip.capacity_rating",
            },
        },
        {"name": "Population Figures", "word_limit": 20, "live": True},
        {"name": "Registration Count", "word_limit": 10, "live": True},
        # ... up to 10 sections ...
    ]
    live_fields = ["Population Figures", "Registration Count"]
    freshness_rules = {"Population Figures": "<=6 months"}


# === KC-3 Outcome Evidence Card ===
class KC3OutcomeEvidenceCard(BaseCard):
    card_id = "KC-3"
    title = "Outcome Evidence Card"
    description = (
        "Evidence, KOI/KRI metrics, and evaluation findings for interventions."
    )
    valid_until_default = 12
    graph_query_anchors = ["Evaluation", "InterventionType"]
    proposal_sections_fed = ["evidence_pico", "indicator_table"]
    sections = [
        {
            "name": "Evidence PICO Table",
            "word_limit": 110,
            "query": {
                "type": "CYPHER",
                "query": "MATCH (e:Evaluation)-[:PRODUCES]->(f:EvidenceFinding) RETURN e.title, f.textValue",
            },
        },
        {
            "name": "Indicator KOI",
            "word_limit": 40,
            "query": {
                "type": "CYPHER",
                "query": "MATCH (i:Indicator)-[:MEASURES]->(it:InterventionType) RETURN i.indicatorCode, i.numericValue",
            },
        },
        {
            "name": "Indicator KRI",
            "word_limit": 40,
            "query": {
                "type": "CYPHER",
                "query": "MATCH (i:Indicator)-[:MEASURES]->(it:InterventionType) RETURN i.indicatorCode, i.numericValue",
            },
        },
        # ... 13 total sections ...
    ]
    evidence_hierarchy = [
        "Systematic Review",
        "Multi-Country",
        "RCT",
        "Quasi",
        "Qualitative",
    ]
    indicator_enforcement = True  # KOI & KRI required


# === KC-4 Partner Capacity Card ===
class KC4PartnerCapacityCard(BaseCard):
    card_id = "KC-4"
    title = "Partner Capacity Card"
    description = "Evaluation of partner capacity, compliance, and projects."
    valid_until_default = 12
    graph_query_anchors = ["ImplementingPartner"]
    proposal_sections_fed = ["capacity_ratings", "active_projects"]
    sections = [
        {
            "name": "Capacity Ratings",
            "word_limit": 35,
            "query": {
                "type": "CYPHER",
                "query": "MATCH (ip:ImplementingPartner)-[:CAPACITY]->(pr:Project) RETURN ip.name, pr.rating",
            },
        },
        {
            "name": "Compliance & Risk",
            "word_limit": 35,
            "query": {
                "type": "CYPHER",
                "query": "MATCH (ip:ImplementingPartner)-[:AUDITED]->(a:Audit) RETURN a.risk_profile",
            },
            "sensitive": True,
        },
        {"name": "Active Project Count", "word_limit": 20, "live": True},
        {"name": "Total Beneficiaries Reached", "word_limit": 20, "live": True},
        # ... total 7 sections ...
    ]
    live_fields = ["Active Project Count", "Total Beneficiaries Reached"]
    approval_tiers = {"Compliance & Risk": 2}


# === KC-5 Track Record Card ===
class KC5TrackRecordCard(BaseCard):
    card_id = "KC-5"
    title = "Track Record Card"
    description = "Historical performance and applied lessons for donor/partner."
    valid_until_default = 12
    graph_query_anchors = ["Operation", "Evaluation"]
    proposal_sections_fed = ["performance_data", "lessons_applied"]
    sections = [
        {
            "name": "Past Performance",
            "word_limit": 45,
            "query": {
                "type": "CYPHER",
                "query": "MATCH (op:Operation)-[:HAS_EVAL]->(e:Evaluation) RETURN op.name, e.rating",
            },
        },
        {
            "name": "Lessons Applied",
            "word_limit": 70,
            "query": {
                "type": "CYPHER",
                "query": "MATCH (ll:LessonsLearned)-[:APPLIED_IN]->(op:Operation) RETURN ll.textValue",
            },
        },
        # ... 5 sections ...
    ]


# === KC-6 Crisis Political Economy Card ===
class KC6CrisisCard(BaseCard):
    card_id = "KC-6"
    title = "Crisis Political Economy Card"
    description = "Complex emergency/crisis scenario analysis and planning."
    valid_until_default = 6
    graph_query_anchors = ["Crisis", "ConflictEvent"]
    proposal_sections_fed = ["scenario_planning"]
    sections = [
        {
            "name": "Crisis Overview",
            "word_limit": 60,
            "query": {
                "type": "CYPHER",
                "query": "MATCH (c:Crisis) RETURN c.name, c.status",
            },
        },
        {
            "name": "Scenario Planning",
            "word_limit": 100,
            "query": {
                "type": "CYPHER",
                "query": "MATCH (s:Scenario)-[:PART_OF]->(c:Crisis) RETURN s.title, s.description",
            },
        },
        # ... 4 sections ...
    ]


# ---- Validation rules ----
def validate_card(
    card: BaseCard, blocks: List[Dict], require_sources: bool = True
) -> List[str]:
    errors = []
    section_names = {s["name"] for s in getattr(card, "sections", [])}
    for block in blocks:
        if block["section_name"] not in section_names:
            errors.append(f"Block {block['section_name']} not in card {card.card_id}")
        if "word_limit" in block and block.get("word_count", 0) > block["word_limit"]:
            errors.append(
                f"Block {block['section_name']} exceeds word limit {block['word_limit']}"
            )
        if require_sources and not block.get("sources"):
            errors.append(f"Block {block['section_name']} missing sources")
        if (
            "sensitive" in block
            and block["sensitive"]
            and block.get("approval_tier", 1) < 2
        ):
            errors.append(f"Block {block['section_name']} requires Tier 2 approval")
    return errors
