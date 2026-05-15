Implement a comprehensive curator workspace to support browsing, filtering, creating, editing, reviewing, and publishing knowledge cards of all types. The workspace must present a dashboard of cards (filterable/searchable by status and metadata), a full-featured section and markdown editor, pre-population of sections from the graph, clear validation of required fields, section word counts, and approval workflows tied to user roles and data sensitivity. Provide features for source traceability, version control (with diff and history), and schema/data freshness validation. Integrate this workspace with the navigation, relevant APIs, and ensure e2e tests verify card creation, review, approval, and expiry flow. Curation actions and all review states must be auditable/backed by the backend.

Verification & Test Guidance
- [ ] CuratorWorkspace UI is present, linked in navigation, and can browse, create, and edit knowledge cards of all template types.
- [ ] Cards and card sections support word count/progress, source linking, and show prefilled graph data when available.
- [ ] Schema and freshness rules are validated at edit time; warnings/errors surface in the UI as documented.
- [ ] Version history and diff views work as described, all changes can be reviewed and approved per workflow.
- [ ] E2E or Playwright tests exist to simulate: curator creates card → prefill from graph → validate → save → submit for tiered approval, expiring/renewing as necessary.
- [ ] All review/approval actions are audit-trailed in backend tables or logs.