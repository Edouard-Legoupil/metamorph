import requests
from typing import Dict, Any
from datetime import datetime

REGISTERED_WEBHOOKS = []  # [{"url": ..., "event_type": ...}]


def register_webhook(url: str, event_type: str):
    REGISTERED_WEBHOOKS.append({"url": url, "event_type": event_type})


def dispatch_webhook(event_type: str, payload: Dict[str, Any]):
    for hook in REGISTERED_WEBHOOKS:
        if hook["event_type"] == event_type:
            try:
                requests.post(
                    hook["url"],
                    json={
                        "event_type": event_type,
                        "timestamp": datetime.utcnow().isoformat(),
                        "payload": payload,
                    },
                    timeout=5,
                )
            except Exception as e:
                print(f"Webhook {hook['url']} failed: {e}")
