from fastapi import APIRouter, Body
from typing import List, Dict, Any
from app.services.routing.trust_router import (
    determine_tier,
    shadow_update,
    auto_accept,
    human_escalation,
    routing_report,
)
from datetime import datetime

router = APIRouter()


@router.post("/batch-route")
def batch_trust_route(triplets: List[Dict], existing_state: Dict = Body({})):
    results = []
    for triplet in triplets:
        outcome, details = determine_tier(
            triplet,
            existing_state,
            triplet["metadata"].get("entity_resolution_confidence", None),
        )
        # Apply outcome
        if outcome == "🟢 AUTO_ACCEPT":
            auto_accept(triplet)
        elif outcome == "🟡 SHADOW_UPDATE":
            shadow_update(triplet)
        elif outcome == "🔴 HUMAN_ESCALATION":
            human_escalation(triplet, details.get("tier", 1), details.get("reason", ""))
        results.append(
            {
                "triplet_id": triplet.get("metadata", {}).get("triplet_id"),
                "outcome": outcome,
                **details,
            }
        )
    return {"results": results, "metrics": routing_report()}


@router.get("/sla-metrics")
def get_sla_metrics():
    return routing_report()
