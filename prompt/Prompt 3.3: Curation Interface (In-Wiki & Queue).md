Implement the curation interface from Pipeline Blueprint Sections 4.4 and 6.2.

Create frontend components for curation:

1. In-wiki curation (embedded in reading experience):
   - Each block has [Verify] button (visible to authenticated users)
   - Each block has [Flag] button for reporting issues
   - Clicking Verify:
     * Increments community_trust_score
     * If threshold reached, promotes to COMMUNITY_VERIFIED
     * Shows success toast
   - Clicking Flag:
     * Opens modal with reason options
     * Allows comment
     * Creates FlagRecord

2. Atomic validation cards (curation queue):
   Component: ValidationCard
   Props: {
     conflict_id,
     type: "QUANTITATIVE|NORMATIVE|CONTACT|STRUCTURAL",
     severity: "CRITICAL|MINOR",
     current_value: {value, source, date},
     incoming_value: {value, source, date},
     assigned_tier: 1|2|3,
     context: {document_title, page_reference, snippet}
   }
   Actions: [Approve Update] [Reject] [Edit] [Escalate]

3. Curation queue dashboard:
   Columns (per 6.2):
   - Conflict ID (clickable for detail)
   - Type with icon
   - Severity badge (🔴 CRITICAL / 🟡 MINOR)
   - Current Value (truncated with source tooltip)
   - Proposed Value (truncated with source tooltip)
   - Assigned Tier
   - Age (time since creation)
   - Actions: Approve / Reject / Edit / Escalate
   
   Filters:
   - By type, severity, tier, status
   - Search by entity name
   - Sort by age, severity

4. Conflict resolution workflow:
   - Approve: Update graph with incoming value, close conflict
   - Reject: Keep current value, close conflict with note
   - Edit: Open editor to create merged/corrected value
   - Escalate: Move to next tier (1→2→3)
   - Resolution adds note and resolved_by

5. Notification system:
   - On assignment to tier
   - On escalation
   - On SLA breach (24h for CRITICAL, 7d for MINOR)
   - On resolution (notify original flagger)

6. Mobile-responsive design:
   - Queue view optimized for phone
   - Quick approve/reject actions
   - Swipe gestures for common actions

- Wire up /api/v1/blocks/card/{card_id}/preview and /api/v1/curation/conflicts to power these components.
- Reuse ValidationCard both in-wiki (for atomic popups on conflict) and in dashboard.
