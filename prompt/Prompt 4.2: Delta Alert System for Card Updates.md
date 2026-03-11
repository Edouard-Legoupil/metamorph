Implement the delta alert system from knowledge-card.yaml (pipeline_role.delta_alerting).

Create services/alerts/delta_alert_service.py:

1. Alert trigger conditions:
   - When new triplets touch any source_nodes of approved cards
   - When contradictions affect referenced nodes
   - When source documents are superseded
   - When valid_until approaching expiry (30/14/7 days)

2. Alert record schema:
   {
     "alert_id": "uuid",
     "card_id": "uuid (KC-1 through KC-6 reference)",
     "card_type": "DONOR|FIELD|EVIDENCE|PARTNER|TRACK|CRISIS",
     "trigger_type": "NEW_DATA|CONTRADICTION|SUPERSEDED|EXPIRY_WARNING",
     "affected_sections": ["section_name"],
     "new_triplets": ["triplet_id"],
     "conflict_ids": ["conflict_id"] if applicable,
     "severity": "INFO|WARNING|CRITICAL",
     "status": "PENDING|ACKNOWLEDGED|RESOLVED|DISMISSED",
     "created_at": "ISO8601",
     "acknowledged_by": "staff_id",
     "acknowledged_at": "ISO8601",
     "resolution_notes": "string"
   }

3. Alert delivery:
   - In-wiki: Card view shows alert banner
   - Email digest (daily for INFO, immediate for CRITICAL)
   - Slack/Teams integration
   - Mobile push (via app)

4. Curator response options:
   - Update card: Open card editor with pre-filled changes
   - Acknowledge: Mark as acknowledged, keep alert visible
   - Dismiss: Remove alert (with reason required)
   - Snooze: Remind in [7/14/30] days

5. Expiry enforcement (per YAML):
   - On valid_until date, card status auto-reverts to DRAFT
   - Card removed from proposal agent availability
   - Curator assigned for renewal
   - Expired card view shows "EXPIRED - Renewal Required"

6. Alert analytics:
   - Track alert frequency by card type
   - Measure time to resolution
   - Identify cards needing frequent updates
   - Suggest optimal valid_until periods


connect:
- In-wiki banners for cards with outstanding alerts (by querying ALERTS)
- Curator dashboard tab for cards with pending/acknowledged/dismissed alerts
- Notifiers and review assignments on new/critical/dormant alerts
- Agentic workflow integration for "needs update"/expiry tasks
- Add  REST endpoints for alert review, curator UI integration, and frontend wiring for banners, notifications, and analytics panel,   