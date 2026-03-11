import uuid
from datetime import datetime
from typing import Dict, List

AUDIT_LOGS: List[Dict] = []


def audit_log(event_type: str, actor: str, action: str, details: Dict):
    AUDIT_LOGS.append(
        {
            "log_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "actor": actor,
            "action": action,
            "details": details,
        }
    )


# Utility to query by actor or event type
def query_logs(event_type: str = None, actor: str = None):
    logs = AUDIT_LOGS
    if event_type:
        logs = [l for l in logs if l["event_type"] == event_type]
    if actor:
        logs = [l for l in logs if l["actor"] == actor]
    return logs
