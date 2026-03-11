Implement the curator workspace for creating and editing knowledge cards.

Create frontend/components/CuratorWorkspace/:

1. Card selection dashboard:
   - Grid view of all 6 card types with metadata
   - Filter by: country, crisis, donor, status (DRAFT|UNDER_REVIEW|APPROVED|SUPERSEDED|ARCHIVED)
   - Search by title, author, keywords
   - Create new card button (with type selection)

2. Card editor (per knowledge-card.yaml):
   - Left sidebar: Section navigation with word count progress
   - Main panel: Markdown editor for current section
   - Right panel: Graph data explorer for that section
   - Bottom panel: Source documents and extracted triplets

3. Draft assistance (Pipeline Blueprint intro):
   - When opening new card, pre-populate sections from graph:
     * Population figures from PopulationGroup nodes
     * Indicator values from Indicator nodes
     * Project history from Project nodes
     * Evaluation findings from EvidenceFinding nodes
   - Show "Draft generated from graph" banner
   - Allow curator to accept/modify/reject each pre-filled item

4. Section requirements enforcement:
   - Show word limit with progress bar
   - Highlight missing required sections
   - Validate against card schema (e.g., each intervention needs KOI+KRI)
   - Warn if data freshness rules violated (e.g., population >6 months)

5. Source traceability:
   - Each paragraph can be linked to source documents
   - Click source to view original markdown/PDF
   - Show extraction confidence and date
   - Allow adding manual sources

6. Version control:
   - Track changes between versions
   - Show diff view when updating
   - Maintain version history
   - Auto-increment version on approval

7. Approval workflow:
   - Submit for review (status → UNDER_REVIEW)
   - Tier-based approval routing (per card type and section sensitivity)
   - Approval notification to requester
   - On approval: status → APPROVED, set valid_until
   - On expiry: auto-revert to DRAFT, re-enter queue


Wire in all required code - 
- Register CuratorWorkspace in UI nav/router.
- Configure API endpoints as needed.
- Add e2e Playwright test scenario for: create card → prefill → validate → save → submit for review → approve/escalate!
-- Add Playwright test and integration with authentication/user context for curation workflow   