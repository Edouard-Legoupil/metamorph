Implement the 6 knowledge card templates from knowledge-card.yaml as wiki page blueprints.

Create services/wiki/card_templates.py:

1. Base card structure:
   - All cards inherit from BaseCard with:
     * card_id, title, description
     * valid_until_default
     * graph_query_anchors (list of node types)
     * proposal_sections_fed (list of proposal sections)

2. KC-1 Donor Intelligence Card:
   - 12 sections with exact word limits from YAML
   - Graph queries for each section:
     * Donor Overview: Donor node properties
     * Organisational Structure: FocalPoint nodes linked to Donor
     * Funding History: FundingInstrument + Expenditure nodes
     * Strategic Alignment: Policy nodes + PledgeCommitment
   - Live fields: contact_details, key_contacts_list
   - Valid until: 12 months default

3. KC-2 Field Context Card:
   - 10 sections with word limits
   - Graph queries:
     * Protection Landscape: LegalFramework + NationalLaw + ProtectionIncident
     * Population Profile: PopulationGroup + RegistrationCohort
     * Socio-Economic: Indicator + Assessment nodes
     * Stakeholder Landscape: ImplementingPartner + UNAgency + NGOPartner
   - Data freshness rules: population_figures ≤6 months
   - Live fields: total_population_figure, registration_count

4. KC-3 Outcome Evidence Card:
   - 13 sections with PICO framework tables
   - Evidence hierarchy: Systematic Review > Multi-Country > RCT > Quasi > Qualitative
   - Indicator enforcement: Each intervention needs KOI and KRI
   - Graph queries: InterventionType + Evaluation + EvidenceFinding + EffectivenessMetric

5. KC-4 Partner Capacity Card:
   - 7 sections with capacity ratings
   - Compliance and risk profile (SENSITIVE - Tier 2+)
   - Graph queries: ImplementingPartner + Project + Evaluation + Audit findings
   - Live fields: active_project_count, total_beneficiaries_reached

6. KC-5 Track Record Card:
   - 5 sections with past performance data
   - Lessons applied (3-part structure)
   - Graph queries: Operation + Project + Evaluation + LessonsLearned

7. KC-6 Crisis Political Economy Card:
   - 4 sections (active complex emergencies only)
   - Scenario planning (3 scenarios required)
   - Graph queries: Crisis + ConflictEvent + AccessConstraint

8. Validation rules:
   - Required sections per card type
   - Word limit enforcement
   - Source document requirements
   - Approval tier requirements (Tier 2 for sensitive sections)


Plug these templates into the page/block assembler and UI workflows.
Add a REST endpoint to enumerate sections/templates or validation test coverage,   

Add - 
- REST endpoints for populating block preview content for any card/section
- End-to-end Playwright or Cypress JSX tests driving frontend/preview workflows
- Live wiring to dynamic graph queries or triplet test data/additional validation hooks