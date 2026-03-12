# Metamorph Curation & Review

## 1. Curation Overview

Metamorph empowers curators, reviewers, and analysts to keep knowledge clean, current, and trustworthy. Micro-tasks, conflict queues, and in-wiki review make quality control seamless.

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
- Reviewer actions trigger backend workflows and audit logging.

### 2.3 Trust Routing and Verification States
- **Auto-Accept**: High confidence, eligible by policy—becomes accepted and visible
- **Shadow/Pending**: Moderate confidence—pending badge, queue for review
- **Escalation**: Low confidence, contradiction, sensitive domain—human review only

### 2.4 Community Trust
- Community verification: If trusted users read a block and do not flag, trust score increases, fresh status may be promoted.

---

## 3. Conflict Handling
- Conflicts queued by contradiction detection (quantitative, normative, contact, structural, temporal, classification)
- Each conflict record (`review.conflicts`) contains:
  - Existing value, incoming value
  - Evidence and scope note
  - Severity and tier assignment
  - Status: unresolved, under review, resolved, escalated, dismissed
  - Micro-task for reviewer

---

## 4. Review Tiers & Escalation

- **Tier 1—Field/local:** domain/operational data
- **Tier 2—Regional:** regional SOP/strategy/conflicts
- **Tier 3—HQ/Thematic:** policy/legal/global, high-impact decisions
- Each tier has its own review queues, escalation paths, and audit policies.

---

## 5. Audit & QA
- All reviewer actions are audit-trailed and appear in immutable logs
- Curation actions update block/claim/fact status and provenance
- All state transitions documented for trust, governance, reproducibility

---

See [PIPELINE.md](./PIPELINE.md) for knowledge flow, [ARCHITECTURE.md](./ARCHITECTURE.md) for system context, and [API.md](./API.md) for ValidationCard/curation APIs.