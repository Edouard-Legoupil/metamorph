from fastapi import APIRouter, Query, Body
from typing import List
from app.services.alerts.delta_alert_service import (
    ALERTS,
    create_alert,
    acknowledge_alert,
    dismiss_alert,
    snooze_alert,
    alert_analytics,
)

router = APIRouter()


@router.get("/card/{card_id}/alerts")
def get_card_alerts(card_id: str, status: str = Query(None)):
    alerts = [a for a in ALERTS if a["card_id"] == card_id]
    if status:
        alerts = [a for a in alerts if a["status"] == status]
    return alerts


@router.get("/alerts")
def get_dashboard_alerts(status: str = Query(None)):
    alerts = ALERTS
    if status:
        alerts = [a for a in alerts if a["status"] == status]
    return alerts


from fastapi import Depends
from app.core.security import get_api_key


@router.post("/alerts/{alert_id}/acknowledge")
def post_acknowledge_alert(
    alert_id: str, user_id: str = Body(...), api_key: str = Depends(get_api_key)
):
    return acknowledge_alert(alert_id, user_id)


@router.post("/alerts/{alert_id}/dismiss")
def post_dismiss_alert(
    alert_id: str,
    user_id: str = Body(...),
    reason: str = Body(...),
    api_key: str = Depends(get_api_key),
):
    return dismiss_alert(alert_id, user_id, reason)


@router.post("/alerts/{alert_id}/snooze")
def post_snooze_alert(
    alert_id: str, days: int = Body(7), api_key: str = Depends(get_api_key)
):
    return snooze_alert(alert_id, days)


@router.get("/analytics")
def get_alert_analytics():
    return alert_analytics()
