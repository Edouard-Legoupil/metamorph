Implement a system that defines and applies knowledge card templates for the six main card types using configuration (YAML or code). Each card and card section must specify its data source (graph query or claims), markdown or UI section template, precise word limits, human approval requirements, and validation rules. The template logic should enforce the structure and content requirements for all cards and sections, including automatic validation of required fields, freshness/valid-until logic, and section approval tier. Attach the template engine to the block assembler and rendering workflows, and expose REST endpoints for enumerating template sections, validation rules, and test card/block rendering.

Verification & Test Guidance
- [ ] Check for a card template mapping/config (YAML or code) covering all six card types and each required section.
- [ ] Confirm the template logic enforces word limits, required/optional sections, data freshness, and approval/status for each card.
- [ ] Inspect the backend or API for endpoints that list templates, preview block rendering, and test validation logic.
- [ ] Manually preview/test all cards and sections in the UI for correct population, validation messaging, freshness/approval banners, and template enforcement.
- [ ] Review PIPELINE.md, CURATION.md, and code/docs for description of the template/section/validation system.