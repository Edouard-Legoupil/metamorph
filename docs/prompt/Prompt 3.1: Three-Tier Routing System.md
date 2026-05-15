Implement a trust routing system that assigns every new claim or update into one of three lanes: auto-accept, shadow/pending review, or human escalation. The routing decision must consider extraction and entity-resolution confidence, presence of existing conflicts, new/ambiguous entities, and domain-specific thresholds. Mark outcomes distinctly in both the graph (with verification and status fields) and in wiki/card blocks (showing current trust level and pending/accept/human review status). Expose routing statistics and tiers in operator monitoring, and queue all ambiguous, unresolved, or critical claims for review within defined SLA windows. Document the decision logic in PIPELINE.md and CURATION.md.

Verification & Test Guidance
- [ ] Confirm the presence of a trust router service/module that routes claims by confidence, conflict, and entity match status.
- [ ] Database and graph include verification and status fields for all claims, blocks, and unresolved entities; wiki/card UI displays these lanes (auto, pending, human) for every block.
- [ ] Curation queue includes escalated items and tracks SLAs.
- [ ] Monitoring/metrics endpoints or dashboards show real-time distribution by tier and mean/median time to resolve.
- [ ] Manual and automated tests verify that new claims are correctly routed on all branches; PIPELINE.md and CURATION.md document the routing and review policy.