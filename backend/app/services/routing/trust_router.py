from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from app.services.reconciliation.delta_engine import make_conflict_record


def calculate_aggregate_confidence(
    triplet: Dict, entity_resolution_confidence: float = None
) -> float:
    extraction_conf = triplet["metadata"].get("extraction_confidence", 0.0)
    if entity_resolution_confidence is not None:
        # Heavier weighting on extraction confidence, but consider entity link
        return 0.7 * extraction_conf + 0.3 * entity_resolution_confidence
    return extraction_conf


def has_conflict(triplet: Dict) -> bool:
    # Stub - real impl will query graph/journal for unresolved conflicts on (subject, predicate)
    return False


def create_conflict_record(triplet: Dict) -> Dict:
    # Minimal stub, just marks as MINOR for non-demo
    return make_conflict_record(
        triplet["subject"],
        triplet["predicate"],
        {"object": triplet["object"]},
        {"object": triplet["object"]},
        "QUANTITATIVE",
        "MINOR",
    )


# 2. Tier assignment logic
def determine_tier(
    triplet: Dict,
    existing_graph_state: Any,
    entity_resolution_confidence: Optional[float] = None,
) -> Tuple[str, Dict]:
    # 1. Conflicts
    if has_conflict(triplet):
        conflict = create_conflict_record(triplet)
        if conflict["severity"] == "CRITICAL":
            return ("🔴 HUMAN_ESCALATION", {"tier": 2, "conflict": conflict})
        else:
            return ("🟡 SHADOW_UPDATE", {"conflict": conflict})
    # 2. New entity case
    if not triplet["subject"].get("id") or not triplet["object"].get("id"):
        return ("🔴 HUMAN_ESCALATION", {"tier": 1, "reason": "new_entity"})
    # 3. Confidence
    conf = calculate_aggregate_confidence(triplet, entity_resolution_confidence)
    triplet_conf = triplet["metadata"].get("extraction_confidence", 0.0)
    if triplet_conf >= 0.95:
        if triplet["subject"].get("id") and triplet["object"].get("id"):
            return ("🟢 AUTO_ACCEPT", {})
        else:
            return ("🟡 SHADOW_UPDATE", {"reason": "entity_resolution_needed"})
    elif triplet_conf >= 0.70:
        return ("🟡 SHADOW_UPDATE", {"reason": "confidence_threshold"})
    else:
        return ("🔴 HUMAN_ESCALATION", {"tier": 1, "reason": "low_confidence"})


# 3. Shadow update implementation
def shadow_update(triplet: Dict):
    # Update verification_status = SHADOW, mark wiki block pending, create CurationQueueItem (stub)
    # Real logic would update graph and wiki, here just print
    print(f"SHADOW_UPDATE for triplet {triplet}")
    # schedule review, e.g. via background scheduler
    schedule_review(triplet, days=7)


def schedule_review(triplet, days):
    due = datetime.utcnow() + timedelta(days=days)
    print(f"Review for triplet {triplet['subject']['name']} due by {due.isoformat()}")


# 4. Auto-accept implementation
def auto_accept(triplet: Dict):
    # Set verification_status = AUTO_ACCEPTED, add robot icon to wiki, increment count (stub)
    print(f"AUTO_ACCEPTED {triplet}")
    # Real: update in database, add to community verification pool


# 5. Human escalation
def human_escalation(triplet: Dict, tier: int, reason: str = ""):
    # Create CurationQueueItem, assign, notify (stub)
    print(f"HUMAN_ESCALATION (Tier {tier}) for {triplet['subject']['name']}")
    escalate_notification(triplet, tier, reason)
    schedule_review(triplet, days=2)


def escalate_notification(triplet, tier, reason):
    print(f"Notify Tier {tier} for {triplet['subject']['name']} | Reason: {reason}")


# 6. Routing metrics
# In production: store in monitoring system, for demo keep in process stats
tier_counts = {"AUTO_ACCEPT": 0, "SHADOW_UPDATE": 0, "HUMAN_ESCALATION": 0}
resolution_times = []


def record_routing_metric(outcome: str, start_time: datetime, end_time: datetime):
    if outcome in tier_counts:
        tier_counts[outcome] += 1
    resolution_times.append((end_time - start_time).total_seconds())


def routing_report():
    avg_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0
    return {"counts": tier_counts, "avg_resolution_time_sec": avg_time}
