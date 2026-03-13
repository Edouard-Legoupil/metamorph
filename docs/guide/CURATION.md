# Metamorph Curation & Review

## 1. Curation Overview

Metamorph empowers curators, reviewers, and analysts to keep knowledge clean, current, and trustworthy. Micro-tasks, conflict queues, in-wiki review, and a robust audit/retroaction pipeline make quality control seamless and auditable.

---

## 2. Curation Workflows

### 2.1 Validation Cards
- Every conflict/claim presents a validation card (`ValidationCard`) with:
  - Current accepted value
  - Incoming/proposed update
  - Evidence, provenance, extraction metadata
  - Buttons: Approve, Reject, Merge/Edit, Escalate

### 2.2 In-Wiki Curation
- Every wiki block can be verified, flagged, edited, or resolved.
- Conflict banners, freshness indicators, and provenance modals are always visible.
- Reviewer actions trigger backend workflows, immediate wiki/card/graph update, and audit logging. All accepted or rejected actions flow into the canonical graph and claim store via the retroaction loop.

### 2.3 Trust Routing and Verification States
- **Auto-Accept**: High confidence, eligible by policy—becomes accepted and visible
- **Shadow/Pending**: Moderate confidence—pending badge, queue for review
- **Escalation**: Low confidence, contradiction, sensitive domain—human review only

### 2.4 Community Trust
- Community verification: If trusted users read a block and do not flag, trust score increases, fresh status may be promoted.

---

## 3. Human Retroaction Feedback Loop
When a curator or reviewer performs any in-wiki or dashboard action—approving, editing, merging, escalating, or rejecting—a new entry is instantly recorded in the audit log and curation table with actor, rationale, and timestamp. The canonical claim, fact, or entity record is updated in both the relational and graph database and previous states are preserved with full provenance. Changes trigger block/card refresh in the UI and update verification badges/banners. All retroaction is bidirectionally traceable via API for both human and agentic use. This ensures that every curation action permanently alters the trusted knowledge base in an auditable and reproducible way. For detailed API contracts, see API.md.

---

## 4. Conflict Handling
- Conflicts queued by contradiction detection (quantitative, normative, contact, structural, temporal, classification)
- Each conflict record (`review.conflicts`) contains:
  - Existing value, incoming value
  - Evidence and scope note
  - Severity and tier assignment
  - Status: unresolved, under review, resolved, escalated, dismissed
  - Micro-task for reviewer

---

## 5. Review Tiers & Escalation

- **Tier 1—Field/local:** domain/operational data
- **Tier 2—Regional:** regional SOP/strategy/conflicts
- **Tier 3—HQ/Thematic:** policy/legal/global, high-impact decisions
- Each tier has its own review queues, escalation paths, and audit policies.

---

## 6. Audit & QA
- All reviewer actions are audit-trailed and appear in immutable logs
- Curation actions update block/claim/fact status and provenance, and are propagated via the human retroaction feedback loop
- All state transitions are documented for trust, governance, and reproducibility
- The API and QA dashboards must reflect all live and historic decisions

---

See [PIPELINE.md](./PIPELINE.md) for knowledge flow and retroaction summary, [ARCHITECTURE.md](./ARCHITECTURE.md) for system context, and [API.md](./API.md) for ValidationCard/curation endpoints. 