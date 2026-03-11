import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional

ALERTS: List[Dict] = []  # in-memory store, swap for DB in prod


# 2. Alert record schema
def create_alert(
    card_id: str,
    card_type: str,
    trigger_type: str,
    section_list: List[str],
    new_triplets=None,
    conflict_ids=None,
    severity="INFO",
) -> Dict:
    alert = {
        "alert_id": str(uuid.uuid4()),
        "card_id": card_id,
        "card_type": card_type,
        "trigger_type": trigger_type,
        "affected_sections": section_list,
        "new_triplets": new_triplets or [],
        "conflict_ids": conflict_ids or [],
        "severity": severity,
        "status": "PENDING",
        "created_at": datetime.utcnow().isoformat(),
        "acknowledged_by": None,
        "acknowledged_at": None,
        "resolution_notes": "",
    }
    ALERTS.append(alert)
    deliver_alert(alert)
    return alert


# 1. Trigger conditions
def triplet_affects_card(triplet, card):
    # e.g.: if subject/object in source_nodes of card
    source_nodes = card.get("source_nodes", [])
    subj, obj = triplet.get("subject", {}), triplet.get("object", {})
    return subj.get("id") in source_nodes or obj.get("id") in source_nodes


def contradiction_affects_card(conflict, card):
    referenced = card.get("source_nodes", [])
    existing_obj = conflict.get("existing_value", {}).get("object", {})
    incoming_obj = conflict.get("incoming_value", {}).get("object", {})
    return existing_obj.get("id") in referenced or incoming_obj.get("id") in referenced


def source_doc_superseded(doc_id, card):
    # Placeholder - logic: if card cites doc_id which has been superseded
    cited = card.get("source_documents", [])
    return doc_id in cited


def expiry_warning(card):
    valid_until = card.get("valid_until")
    if not valid_until:
        return False
    exp_dt = datetime.fromisoformat(valid_until)
    delta = (exp_dt - datetime.utcnow()).days
    if delta in [30, 14, 7]:
        return delta
    return False


# 3. Alert delivery
def deliver_alert(alert):
    # In-wiki banner, email, Slack, push (stub: print)
    if alert["severity"] == "CRITICAL":
        print(f"DELIVER IMMEDIATE ALERT [{alert['trigger_type']}]: {alert}")
    else:
        print(f"QUEUED ALERT: {alert}")
    # TODO: Integrate with email, Slack, wiki/banner, mobile


# 4. Curator response
def acknowledge_alert(alert_id: str, user_id: str):
    alert = next((a for a in ALERTS if a["alert_id"] == alert_id), None)
    if alert:
        alert["status"] = "ACKNOWLEDGED"
        alert["acknowledged_by"] = user_id
        alert["acknowledged_at"] = datetime.utcnow().isoformat()
    return alert


def dismiss_alert(alert_id: str, user_id: str, reason: str):
    alert = next((a for a in ALERTS if a["alert_id"] == alert_id), None)
    if alert:
        alert["status"] = "DISMISSED"
        alert["resolution_notes"] = reason
        alert["acknowledged_by"] = user_id
        alert["acknowledged_at"] = datetime.utcnow().isoformat()
    return alert


def snooze_alert(alert_id: str, days: int = 7):
    alert = next((a for a in ALERTS if a["alert_id"] == alert_id), None)
    if alert:
        alert["snooze_until"] = (datetime.utcnow() + timedelta(days=days)).isoformat()
    return alert


# 5. Expiry enforcement
def enforce_card_expiry(card, now=None):
    now = now or datetime.utcnow()
    valid_until = card.get("valid_until")
    if valid_until and now >= datetime.fromisoformat(valid_until):
        card["status"] = "DRAFT"
        card["expired_at"] = now.isoformat()
        # Remove from proposal agent
        # Assign curator for renewal here
        print(f"Card {card['card_id']} expired, set to DRAFT and alert curator.")
        return True
    return False


# 6. Analytics
def alert_analytics():
    by_type = {}
    resolution_times = []
    for a in ALERTS:
        by_type.setdefault(a["card_type"], 0)
        by_type[a["card_type"]] += 1
        if a["status"] == "RESOLVED" and a["acknowledged_at"]:
            created = datetime.fromisoformat(a["created_at"])
            ack = datetime.fromisoformat(a["acknowledged_at"])
            resolution_times.append((ack - created).total_seconds())
    avg_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0
    return {"by_type": by_type, "avg_resolution_time_sec": avg_time}
