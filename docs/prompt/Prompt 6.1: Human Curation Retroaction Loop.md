Implement a human curation retroaction loop to ensure all curator-driven edits, approvals, rejections, merges, and conflict resolutions performed via the wiki/card UI or the reviewer dashboard are fully and reliably injected into the canonical knowledge base.

- Whenever a curator or reviewer approves, rejects, or edits a claim, conflict, or wiki/card block, immediately record the action in an immutable audit log and curation history table, capturing actor, action, rationale, and timestamp.
- Update the corresponding knowledge claim, canonical fact, or entity record in both the relational database and graph database to reflect the new status (APPROVED, SUPERSEDED, REJECTED, MERGED, or ESCALATED). Retain all prior versions with provenance and supersession links.
- On each curation decision, propagate the change by refreshing all affected wiki/card blocks, updating verification badges, trust status, and provenance/curation banners in the UI.
- Invalidate or update all affected retrieval indices and ensure that agentic/REST API responses immediately reflect the new state.
- Expose REST endpoints (e.g., POST /api/v1/curation/decision, PATCH /api/v1/claims/:id, or similar) to serve this action loop from UI to backend, requiring provenance for every human retroaction.
- Ensure complete bidirectional traceability: from any accepted fact or resolved Wiki block, an agent or reviewer must be able to query and see the full curation/change history, including exactly which human actions resulted in accepted knowledge.
- Update all documentation (PIPELINE.md, CURATION.md, API.md) with a step-by-step description of this retroaction and audit loop, including API contracts and the event model for block/card refresh.

Verification & Test Guidance
- [ ] Confirm that POST/PATCH endpoints (e.g., /api/v1/curation/decision, /api/v1/claims/:id) record all curation actions and status changes in the backend, and require provenance, rationale, and user identification.
- [ ] Inspect audit log and curation history tables for every curator or reviewer decision; confirm that each accepted claim/block/fact is traceable to an action and actor.
- [ ] Make a curation change (approve, reject, merge, edit) in the UI and verify the change immediately appears in the canonical knowledge base, graph, and relevant wiki/card blocks.
- [ ] Agent or API retrieval of any fact, claim, or block must surface its curation/provenance/audit history.
- [ ] Watch curation, QA, conflict, and agent dashboards for accurate and real-time retroaction reflection at every stage.
- [ ] Documentation in PIPELINE.md and CURATION.md clearly spells out each step of the curation retroaction feedback loop.