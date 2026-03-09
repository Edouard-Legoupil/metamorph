# Labeled Property Graph (LPG) for Humanitarian Knowledge Ontology



**Version:** 1.0  
**Scope:** Full ontology covering operations, policy, people, finance, logistics, context, and inter-agency coordination 

---

## Table of Contents

1. [LPG Ontology — Node Types](#1-lpg-ontology--node-types)
2. [LPG Ontology — Edge Types](#2-lpg-ontology--edge-types)
3. [LPG Ontology — Property Schemas](#3-lpg-ontology--property-schemas)
4. [Template System](#4-template-system)
5. [Agentic Project Proposal System](#5-agentic-project-proposal-system)

---

## 1. LPG Ontology — Node Types

The ontology is organised into **eight domains**. Every node carries a `node_id`, `created_at`, `last_updated`, `source_documents[]`, and `verification_status` in addition to domain-specific properties listed below.

---

### Domain A — Geographic & Administrative

| Node Label | Description | Key Properties |
|---|---|---|
| `Country` | Sovereign state | `iso3`, `name`, `un_member`, `hpc_status` |
| `Region` | Sub-national administrative unit | `admin_level` (1–4), `pcode`, `parent_country` |
| `Settlement` | Town, camp, site, collective centre | `settlement_type` (camp / urban / rural / transit), `population_figure`, `population_date`, `coordinates` |
| `Border` | A crossing point or border zone | `crossing_type` (official / unofficial), `status` (open / closed / restricted), `avg_daily_crossings` |
| `OperationalZone` | A defined geographic scope for an operation | `zone_code`, `responsible_office`, `access_classification` (phase 1–5 OCHA scale) |
| `DisasterZone` | Area classified under a declared emergency | `declaration_date`, `disaster_type`, `ipc_phase`, `declared_by` |

---

### Domain B — Crisis & Context

| Node Label | Description | Key Properties |
|---|---|---|
| `Crisis` | A named humanitarian crisis or emergency | `crisis_id`, `crisis_type` (conflict / natural_disaster / displacement / famine / epidemic / compound), `onset_date`, `status` (active / protracted / post-crisis), `hno_year` |
| `DisplacementEvent` | A specific movement of population | `event_type` (flee / return / relocation / secondary_displacement), `trigger`, `estimated_affected`, `event_date` |
| `HazardEvent` | A physical event causing harm | `hazard_type` (flood / earthquake / drought / cyclone / disease_outbreak), `magnitude`, `affected_population`, `event_date` |
| `ConflictEvent` | An act of violence or armed conflict | `conflict_type` (armed_clashes / airstrikes / siege / GBV / landmine), `incident_date`, `verified_by`, `casualties` |
| `ProtectionIncident` | A documented protection violation | `incident_type` (arbitrary_detention / forced_eviction / refoulement / statelessness / child_recruitment), `victim_profile`, `perpetrator_type`, `status` |
| `AccessConstraint` | A documented impediment to humanitarian access | `constraint_type` (bureaucratic / physical / security / community), `onset_date`, `resolution_date`, `impact_level` |

---

### Domain C — Population & Beneficiaries

| Node Label | Description | Key Properties |
|---|---|---|
| `PopulationGroup` | A categorised group of people | `group_type` (refugee / IDP / returnee / stateless / host_community / asylum_seeker / UASC / elderly / PWD / female_HoH), `legal_framework` (1951_Convention / UNHCR_Mandate / IDP_GP / other), `estimated_size`, `size_date` |
| `HouseholdProfile` | Aggregate profile of a household type | `avg_size`, `female_headed_pct`, `dependency_ratio`, `primary_language`, `primary_livelihood` |
| `VulnerabilityProfile` | Documented vulnerability characteristics | `vulnerability_type` (medical / legal / SGBV / child_protection / mental_health / documentation), `severity` (1–5), `prevalence_rate` |
| `CommunityStructure` | Formal or informal community governance | `structure_type` (camp_committee / elders_council / women_group / youth_network / CBP), `mandate`, `recognition_status` |
| `RegistrationCohort` | A defined group in a registration system | `registration_system` (proGres / RIMES / biometric), `registration_date_range`, `total_registered`, `verified_count` |

---

### Domain D — Operational & Programmatic

| Node Label | Description | Key Properties |
|---|---|---|
| `Operation` | A country-level or regional operation | `operation_code`, `operation_type` (emergency / protracted / mixed), `start_date`, `mandate`, `global_compact_alignment` |
| `Programme` | A multi-year programmatic framework | `programme_type` (HRP / RRP / MOPAN / CAP / bilateral), `start_year`, `end_year`, `total_budget_usd` |
| `Project` | A time-bound funded activity | `project_code`, `start_date`, `end_date`, `budget_usd`, `donor_id`, `sector`, `status` (pipeline / active / closed / suspended) |
| `Activity` | A specific implementable action within a project | `activity_type` (distribution / registration / legal_counselling / shelter_construction / psychosocial_support / training / advocacy), `unit_of_measure`, `target_count`, `achieved_count` |
| `SubOffice` | A field-level office | `office_code`, `location`, `coverage_zone`, `head_of_office`, `established_date` |
| `ImplementingPartner` | An organisation delivering activities | `partner_type` (NGO / INGO / government / UN_agency / CBO), `partner_code`, `agreement_type` (PCA / FAPA / LOA / MOU), `capacity_rating` |
| `ServicePoint` | A physical location where services are delivered | `service_type` (registration_centre / distribution_point / health_facility / protection_desk / CASH_agent / legal_aid_clinic), `coordinates`, `operating_hours`, `monthly_beneficiaries` |

---

### Domain E — Policy, Legal & Normative

| Node Label | Description | Key Properties |
|---|---|---|
| `Policy` | An organisational policy document | `policy_type` (global / regional / country / operational), `policy_code`, `effective_date`, `review_date`, `mandatory` (boolean), `supersedes` |
| `SOP` | A Standard Operating Procedure | `sop_code`, `sector`, `version`, `effective_date`, `scope` (global / regional / country), `approval_level` |
| `LegalFramework` | An international legal instrument | `instrument_type` (convention / protocol / resolution / declaration / guideline), `adopting_body` (UNGA / HRC / ExCom / Security_Council), `adoption_date`, `binding` (boolean) |
| `NationalLaw` | A domestic legal norm relevant to the operation | `country`, `law_type` (asylum_law / nationality_law / labour_law / land_law), `enactment_date`, `compliance_with_intl_standards` (yes / partial / no) |
| `ExComConclusion` | An UNHCR Executive Committee conclusion | `conclusion_number`, `year`, `topic`, `binding` (boolean) |
| `PledgeCommitment` | A government or donor commitment | `pledging_event`, `commitment_type` (financial / policy / resettlement_quota), `amount`, `fulfilment_status` |
| `StandardIndicator` | A defined measurement norm | `indicator_code`, `indicator_framework` (SPHERE / CHS / IASC / SDG / HAP), `sector`, `unit`, `minimum_standard_value`, `target_value` |

---

### Domain F — Finance & Resources

| Node Label | Description | Key Properties |
|---|---|---|
| `Donor` | A funding entity | `donor_type` (government / private / foundation / UN_pooled_fund / earmarked_trust_fund), `iso3` (if government), `donor_code`, `total_contributions_usd` |
| `FundingInstrument` | A specific funding agreement | `instrument_type` (grant / loan / cost-sharing / pooled_fund_allocation / CERF / CHF), `agreement_number`, `amount_usd`, `start_date`, `end_date`, `earmarking_level` (tightly / softly / unearmarked) |
| `Budget` | A structured financial plan | `budget_type` (project / programme / operation / supplementary), `total_usd`, `year`, `funding_gap_usd`, `funding_coverage_pct` |
| `Expenditure` | A recorded financial transaction | `expenditure_type` (staff / non-staff / operational / capital), `amount_usd`, `period`, `implementing_entity` |
| `FundingAppeal` | A formal request for humanitarian financing | `appeal_type` (HRP / flash / supplementary / CERF_application), `year`, `requested_usd`, `received_usd`, `coverage_pct` |

---

### Domain G — Human Resources & Stakeholders

| Node Label | Description | Key Properties |
|---|---|---|
| `Staff` | An individual staff member (anonymised in graph) | `staff_type` (international / national / affiliate / UNV), `functional_area`, `grade`, `duty_station` |
| `FocalPoint` | A named contact for a specific function | `function` (data / protection / GBV / CCCM / registration / livelihoods), `contact_email`, `office_id`, `languages` |
| `GovernmentAuthority` | A national or local government body | `authority_type` (ministry / directorate / prefecture / municipality / border_authority), `country`, `mandate_area`, `relationship_quality` (cooperative / neutral / restrictive / hostile) |
| `UNAgency` | A UN system entity | `agency_code` (UNHCR / WFP / UNICEF / OCHA / IOM / WHO / UNDP / FAO / UNFPA), `role_in_context` (lead / co-lead / member / observer), `cluster_leadership` |
| `ClusterSector` | A humanitarian coordination mechanism | `cluster_name`, `sector`, `lead_agency`, `co_lead`, `active_members_count`, `meeting_frequency` |
| `NGOPartner` | A non-governmental implementing partner | `organisation_name`, `org_type` (local / national / international), `specialisation`, `operational_countries` |

---

### Domain H — Knowledge & Information

| Node Label | Description | Key Properties |
|---|---|---|
| `Document` | A source document ingested into the pipeline | `document_type` (policy / SOP / assessment / report / guidance_note / training_material / registration_form / legal_text / press_release / situation_report / ProGres_export), `title`, `author`, `publication_date`, `source_url`, `language`, `markdown_path` |
| `Assessment` | A structured needs or situation assessment | `assessment_type` (HNO / MSNA / PDM / PCNA / CCCM_site_assessment / registration_audit), `methodology`, `sample_size`, `fieldwork_dates`, `geographic_scope` |
| `SituationReport` | A periodic operational update | `report_type` (sitrep / flash_update / operational_update / media_briefing), `reporting_period`, `author_office`, `key_figures` |
| `TrainingMaterial` | A capacity-building resource | `training_type` (e-learning / workshop / field_guide / SOP_training / protection_mainstreaming), `target_audience`, `language`, `duration_hours` |
| `Dataset` | A structured data asset | `dataset_type` (population_statistics / site_data / registration_data / expenditure_data / indicator_monitoring), `format`, `update_frequency`, `access_level` (public / internal / restricted) |
| `Indicator` | A specific measured data point | `indicator_code`, `value`, `unit`, `measurement_date`, `source_assessment`, `geographic_scope`, `disaggregation` (sex / age / location / vulnerability) |
| `InterventionType` | A canonical, reusable type of humanitarian action | `intervention_code`, `sector`, `modality` (in-kind / cash / service / advocacy / capacity_building / infrastructure), `delivery_mechanism`, `standard_duration_weeks`, `unit_of_measure` |
| `Evaluation` | A formal assessment of a project or programme's effectiveness | `evaluation_type` (real-time / mid-term / final / meta / impact / process), `commissioned_by`, `conducted_by`, `fieldwork_dates`, `methodology` (RCT / quasi-experimental / mixed_methods / qualitative / survey), `geographic_scope`, `population_scope`, `credibility_rating` (peer-reviewed / internally_validated / draft) |
| `EvidenceFinding` | A discrete, extractable conclusion from an evaluation | `finding_type` (effectiveness / efficiency / relevance / coherence / impact / sustainability / unintended_effect), `finding_text_summary`, `direction` (positive / negative / neutral / mixed), `magnitude` (strong / moderate / weak / inconclusive), `conditions_of_applicability`, `confidence_level` (high / medium / low), `source_evaluation_id` |
| `EffectivenessMetric` | A quantified result from an evaluated intervention | `metric_type` (cost_per_beneficiary / coverage_rate / change_in_indicator / time_to_delivery / dropout_rate / complaint_rate / sustainability_score), `value`, `unit`, `comparator` (baseline / control_group / standard / prior_project), `source_evaluation_id` |
| `ContextCondition` | A documented condition under which an intervention worked or failed | `condition_type` (access_level / market_functionality / community_trust / government_cooperation / seasonal / population_density / urban_rural / displacement_phase), `condition_value`, `effect_on_outcome` (enabler / barrier / neutral) |
| `LessonsLearned` | A practitioner-derived lesson from implementation experience | `lesson_type` (design / targeting / timing / partnership / community_engagement / data_quality / supply_chain / coordination), `lesson_text`, `actionable_recommendation`, `source_type` (evaluation / AAR / PDM / staff_debrief / community_feedback) |
| `UnintendedEffect` | A documented positive or negative consequence not in the original design | `effect_type` (market_distortion / dependency / community_conflict / protection_risk / positive_spillover / stigma / environmental), `direction` (positive / negative), `severity`, `mitigation_applied` |

---

## 2. LPG Ontology — Edge Types

Edges are grouped by domain pair. All edges carry: `edge_id`, `source_document_id`, `confidence`, `created_at`, `valid_from`, `valid_to` (for temporal edges).

### 2.1 Geographic Edges

| Edge | From → To | Meaning |
|---|---|---|
| `LOCATED_IN` | Settlement / ServicePoint / SubOffice → Region / Country | Physical location |
| `BORDERS` | Country → Country | Shares a border |
| `COVERS` | OperationalZone → Region / Settlement | Zone encompasses area |
| `HAS_CROSSING` | Border → Country | Crossing connects two countries |
| `CLASSIFIED_AS` | Region → DisasterZone | Area under emergency classification |

### 2.2 Crisis & Context Edges

| Edge | From → To | Meaning |
|---|---|---|
| `TRIGGERED_BY` | DisplacementEvent → Crisis / HazardEvent / ConflictEvent | Causal link |
| `AFFECTS` | Crisis / HazardEvent → Country / Settlement / PopulationGroup | Impact scope |
| `COMPOUNDS` | Crisis → Crisis | One crisis exacerbates another |
| `LED_TO` | ConflictEvent / HazardEvent → ProtectionIncident | Sequence of harm |
| `CONSTRAINS_ACCESS_TO` | AccessConstraint → OperationalZone / Settlement | Impediment scope |
| `ESCALATED_TO` | ProtectionIncident → Crisis | Individual incidents that trigger a crisis |

### 2.3 Population Edges

| Edge | From → To | Meaning |
|---|---|---|
| `DISPLACED_FROM` | PopulationGroup → Country / Settlement | Origin location |
| `DISPLACED_TO` | PopulationGroup → Country / Settlement | Destination location |
| `TRANSITING_THROUGH` | PopulationGroup → Country / Settlement | Transit point |
| `REGISTERED_AS` | PopulationGroup → RegistrationCohort | Legal/operational classification |
| `PROTECTED_BY` | PopulationGroup → LegalFramework | Applicable legal protection |
| `HAS_PROFILE` | PopulationGroup → VulnerabilityProfile | Documented vulnerability |
| `ORGANISED_AS` | PopulationGroup → CommunityStructure | Formal/informal governance |
| `HOSTED_BY` | PopulationGroup → Settlement | Physical presence |

### 2.4 Operational Edges

| Edge | From → To | Meaning |
|---|---|---|
| `RESPONDS_TO` | Operation / Project → Crisis | Operational mandate |
| `TARGETS` | Project / Activity → PopulationGroup | Beneficiary targeting |
| `DELIVERS_IN` | Project / Activity → Settlement / OperationalZone | Geographic scope |
| `IMPLEMENTED_BY` | Project / Activity → ImplementingPartner / SubOffice | Implementation responsibility |
| `PART_OF` | Project → Programme | Project belongs to programme |
| `INCLUDES` | Programme → Project | Programme contains projects |
| `COORDINATES_WITH` | Operation → UNAgency / ClusterSector | Coordination relationships |
| `OPERATES_AT` | SubOffice → ServicePoint | Office manages service point |
| `ACHIEVES` | Activity → Indicator | Activity produces a measured result |
| `MEASURED_AGAINST` | Indicator → StandardIndicator | Indicator benchmarked against a standard |

### 2.5 Policy & Legal Edges

| Edge | From → To | Meaning |
|---|---|---|
| `APPLIES_TO` | Policy / SOP → Operation / PopulationGroup / Activity | Normative scope |
| `SUPERSEDES` | Policy / SOP → Policy / SOP | Version control |
| `IMPLEMENTS` | NationalLaw / Policy → LegalFramework | Domestic implementation of international norm |
| `CONFLICTS_WITH` | NationalLaw → LegalFramework / Policy | Legal inconsistency |
| `MANDATES` | LegalFramework → Activity / PopulationGroup | Legal obligation |
| `GOVERNS` | LegalFramework / Policy → PopulationGroup | Governing framework |
| `REFERENCES` | Document → LegalFramework / Policy / SOP | Documentary reference |
| `ENDORSED_BY` | Policy → GovernmentAuthority / UNAgency | Formal endorsement |

### 2.6 Finance Edges

| Edge | From → To | Meaning |
|---|---|---|
| `FUNDS` | Donor → FundingInstrument / Project / Programme | Funding relationship |
| `ALLOCATED_TO` | FundingInstrument → Project / Activity | Fund allocation |
| `CONTRIBUTES_TO` | FundingInstrument → Budget | Budget contribution |
| `REQUESTED_IN` | Budget → FundingAppeal | Appeal includes budget line |
| `SPENT_ON` | Expenditure → Activity / Project | Expenditure attribution |
| `COMMITTED_TO` | PledgeCommitment → Operation / Programme | Pledge target |

### 2.7 Knowledge Edges

| Edge | From → To | Meaning |
|---|---|---|
| `DOCUMENTS` | Document → Crisis / Operation / Project / Assessment | Documentary coverage |
| `SUPERSEDES` | Document → Document | Newer version replaces older |
| `CITES` | Document → Document / LegalFramework / StandardIndicator | In-document citation |
| `PRODUCED_BY` | Document / Dataset → UNAgency / SubOffice / NGOPartner | Authoring entity |
| `INFORMS` | Assessment / Dataset → Project / Activity / FundingAppeal | Evidence base |
| `CONTAINS` | Assessment → Indicator | Assessment produces indicators |
| `UPDATES` | SituationReport → Indicator / PopulationGroup | Periodic data refresh |
| `TRAINED_ON` | TrainingMaterial → SOP / Policy / LegalFramework | Training content source |
| `EVALUATES` | Evaluation → Project / Programme / Activity / InterventionType | Evaluation covers this entity |
| `PRODUCES` | Evaluation → EvidenceFinding / EffectivenessMetric / LessonsLearned | Evaluation output |
| `DOCUMENTS` | Evaluation → UnintendedEffect | Records an unintended consequence |
| `APPLIES_IN` | EvidenceFinding / EffectivenessMetric → ContextCondition | Finding holds under this condition |
| `CONTRADICTS` | EvidenceFinding → EvidenceFinding | Two findings from different evaluations conflict |
| `CORROBORATES` | EvidenceFinding → EvidenceFinding | Two findings from different evaluations agree |
| `ENABLED_BY` | InterventionType → ContextCondition | Intervention requires this condition to succeed |
| `РИСК_OF` | InterventionType → UnintendedEffect | Intervention carries this known risk |
| `INSTANCE_OF` | Activity / Project → InterventionType | Activity is an implementation of a canonical intervention type |
| `COMPARED_TO` | EffectivenessMetric → EffectivenessMetric | Cross-project cost or outcome comparison |
| `GENERATED_FROM` | LessonsLearned → EvidenceFinding | Lesson is derived from a finding |

---

## 3. LPG Ontology — Property Schemas

### 3.1 Universal Properties (all nodes)

```json
{
  "node_id": "uuid",
  "label": "NodeType",
  "created_at": "ISO8601",
  "last_updated": "ISO8601",
  "source_documents": ["document_id"],
  "verification_status": "AUTO_ACCEPTED | SHADOW | HUMAN_VERIFIED | COMMUNITY_VERIFIED",
  "community_trust_score": "integer",
  "language": "ISO 639-1",
  "tags": ["string"]
}
```

### 3.2 Universal Edge Properties

```json
{
  "edge_id": "uuid",
  "type": "EDGE_TYPE",
  "source_node_id": "uuid",
  "target_node_id": "uuid",
  "source_document_id": "uuid",
  "confidence": 0.0–1.0,
  "created_at": "ISO8601",
  "valid_from": "ISO8601 | null",
  "valid_to": "ISO8601 | null",
  "verification_status": "AUTO_ACCEPTED | HUMAN_VERIFIED",
  "notes": "string"
}
```

### 3.3 Temporal Versioning

For any node property that changes over time (population figures, budget amounts, indicator values), the graph stores a **time-series array** rather than a single value:

```json
{
  "population_figure": [
    { "value": 45000, "date": "2024-01-01", "source": "doc_id_1" },
    { "value": 52000, "date": "2024-07-01", "source": "doc_id_2" },
    { "value": 49000, "date": "2025-01-01", "source": "doc_id_3" }
  ]
}
```

The **latest verified value** is used for wiki rendering; the full series is available for trend analysis and proposal evidence generation.

---

