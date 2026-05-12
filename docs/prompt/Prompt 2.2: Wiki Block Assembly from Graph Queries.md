Implement a wiki block assembly system such that, for each knowledge card section, a block definition describes the card/section, block type, data source (graph query), template for rendering, and verification status. Connect each block to its query result from the knowledge graph in real time, format and fill markdown templates with the data, enforce word limits, and display freshness/verification and conflict status. The system must handle both static and live-updated fields, display conflict banners as needed, and support auto-updating for designated live content. Document block/section mappings, schema, and rendering pipeline in PIPELINE.md and CURATION.md.

Verification & Test Guidance
- [ ] Confirm backend/services/wiki/block_assembler and frontend UI both exist to render wiki/card sections from block definitions and graph queries.
- [ ] Check that block templates and mappings align with CARD/YAML configuration and all sections are present.
- [ ] Inspect that live fields auto-update in the UI, marking auto/refreshed state, and conflicts display dynamic banners or resolution flows.
- [ ] Confirm word limits, formatting, and verification status appear per section rules (including human lock when required).
- [ ] Manual edit/render test for all major knowledge cards verifies correct query, formatting, data gap handling, conflict display, and provenance badge.