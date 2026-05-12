Implement a delta engine to compare every newly extracted claim/triplet with existing accepted facts and decide if the outcome is confirmation, expansion, update, contradiction, or insufficient evidence. Classify and log each detected conflict (with type and severity), create a ConflictRecord as necessary, and route by criticality—auto-accept, shadow update, or human escalation per policy. Make sure shadowed or pending/contested claims appear as such in all wiki/card blocks and are always visible for review/curation. Provide API endpoints for batch/journaled ingestion and curator/agent review.

Verification & Test Guidance
- [ ] A delta engine service/module exists with explicit logic for comparing claims to graph facts using all relevant predicate types (numeric, text, entity).
- [ ] ConflictRecords are created with unique IDs, affected entities, values, evidence, conflict type, and severity; all are persisted as described in PIPELINE.md and CURATION.md.
- [ ] Each delta routing outcome triggers an action: accepted → graph update, contradiction → conflict queue, shadow → pending block in wiki.
- [ ] Wiki/card UI shows conflicts and pending resolution, with banners and side-by-side values where appropriate.
- [ ] API endpoint(s) exist for integrating this logic into curation/agent review and allowing batch or live processing of incoming claims.
- [ ] Documentation or code comments in the pipeline/curation/reconciliation modules explain outcome routing and how conflicts/escalations are handled.