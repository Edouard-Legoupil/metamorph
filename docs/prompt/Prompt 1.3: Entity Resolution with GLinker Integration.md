Implement entity resolution as a required step when extracting claims. For every extracted subject or object, attempt to resolve to an existing canonical entity using alias matching, graph search, and other similarity signals. Create a new (shadow) entity record when no suitable match is found. Assign a confidence score to each resolved or shadow entity, track ambiguous resolutions, and provide a workflow for reviewing or escalating ambiguous matches. Ensure all entity resolution outcomes are persisted with provenance and status in the system database, and every new or updated entity is auditable. The resolution logic, state machine, and shadow/ambiguous handling must be referenced in PIPELINE.md and DATABASE.md.

Verification & Test Guidance
- [ ] Confirm entity resolution logic is integrated in the claim extraction service for every subject/object.
- [ ] Database/entity registry updates with newly created or linked entities, with status and provenance for ambiguous/shadow records.
- [ ] Manual or automated tests show both resolved and unresolved/shadow cases are handled, with confidence and candidate links.
- [ ] Manual curation or conflict queue provides an interface to review, merge, split, or escalate ambiguous/unresolved entities.
- [ ] PIPELINE.md and DATABASE.md sections describe the entity resolution flow and shadow lifecycle.