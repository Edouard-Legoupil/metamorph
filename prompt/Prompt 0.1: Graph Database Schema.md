Use instruction within the AGENT.md - Based on the provided Turtle ontology (`unhcr-knowledge-ontology.ttl`) within the ontology folder, implement the graph database schema for Metamorph.

#### Requirements

1. **Node Labels**: Create nodes corresponding to all classes in the ontology. Use the class names as node labels (e.g., `:Country`, `:PopulationGroup`, `:Project`). Where a class is a subclass, you may optionally apply both the subclass and superclass labels (e.g., `:Policy` and `:DocumentaryArtifact`) to enable broader queries.

   **Key Node Labels (by domain)**:

   - **Geographic**: `Country`, `Region`, `Settlement`, `Border`, `OperationalZone`, `DisasterZone`, `RecipientRegion`, `IATILocation`
   - **Situation & Context**: `Situation`, `DisplacementEvent`, `HazardEvent`, `ConflictEvent`, `ProtectionIncident`, `AccessConstraint`
   - **Population**: `PopulationGroup`, `HouseholdProfile`, `VulnerabilityProfile`, `CommunityStructure`, `RegistrationCohort`
   - **Operational**: `Operation`, `Programme`, `Project`, `Activity`, `SubOffice`, `ImplementingPartner`, `ServicePoint`, `IATIActivity`, `Participation`
   - **Policy & Legal**: `Policy`, `SOP`, `LegalFramework`, `NationalLaw`, `ExComConclusion`, `PledgeCommitment`, `StandardIndicator`
   - **Finance**: `Donor`, `FundingInstrument`, `Budget`, `Expenditure`, `FundingAppeal`, `IATITransaction`
   - **Stakeholders**: `Organisation`, `UNAgency`, `ClusterSector`, `NGOPartner`, `PrivateDonor`, `GovernmentAuthority`, `Position`, `FocalPoint`, `ContactInfo`
   - **Knowledge**: `Indicator`, `InterventionType`, `EvidenceFinding`, `EffectivenessMetric`, `ContextCondition`, `LessonsLearned`, `UnintendedEffect`, `Document`, `Assessment`, `SituationReport`, `ActivityReport`, `TrainingMaterial`, `Dataset`, `Evaluation`, `Sector`

2. **Node Properties**: For each node label, include the datatype properties defined in the ontology. All nodes must also include the universal properties from `:Entity`:

   - `identifier` (string) – a unique identifier (e.g., UUID)
   - `createdAt` (datetime)
   - `lastUpdated` (datetime)
   - `verificationStatus` (string) – one of: `AUTO_ACCEPTED`, `SHADOW`, `HUMAN_VERIFIED`, `COMMUNITY_VERIFIED`
   - `hasTag` (list of strings) – free‑text tags

   Additional domain‑specific properties (examples):
   - `:Country` – `iso3`
   - `:Region` – `adminLevel`, `pcode`
   - `:Settlement` – `settlementType`, `populationFigure`, `populationDate`
   - `:GeographicEntity` – `geo:lat`, `geo:long`
   - `:Situation` – `situationId`, `situationType`
   - `:Event` – `onsetDate`
   - `:PopulationGroup` – `groupType`, `estimatedSize`
   - `:Project` – `projectCode`, `budgetUsd`, `startDate`, `endDate`
   - `:Policy` – `policyCode`
   - `:LegalFramework` – `instrumentType`
   - `:Donor` – `donorCode`
   - `:FundingInstrument` – `amountUsd`
   - `:IATITransaction` – `transactionTypeCode`, `transactionDate`, `transactionValue`, `transactionCurrency`, etc.
   - `:Indicator` – `indicatorCode`, `numericValue`
   - `:EvidenceFinding` – `textValue`
   - `:Sector` – `sectorCode`, `sectorVocabulary`, `sectorPercentage`, `sectorLabel`

   **Temporal Versioning**: For properties that change over time (e.g., `populationFigure`, `budgetUsd`, indicator values), store a **time‑series array** rather than a single value:
   ```json
   {
     "populationFigure": [
       { "value": 45000, "date": "2024-01-01", "source": "doc_id_1" },
       { "value": 52000, "date": "2024-07-01", "source": "doc_id_2" }
     ]
   }

The latest value is used for current rendering; the full series is available for trend analysis.

Relationship Types (Edges): For each object property in the ontology, create a corresponding relationship type. Use the property name (without namespace) as the relationship type, e.g., :FUNDS, :LOCATED_IN. Note the directionality defined in the ontology. Many properties have an inverse; implement only one direction (the one most commonly queried) and rely on the inverse for traversal.

Key relationship types (domain → range):

   :LOCATED_IN (GeographicEntity → GeographicEntity) – transitive, with inverse :CONTAINS

   :BORDERS (GeographicEntity → GeographicEntity) – symmetric

   :COVERS (OperationalZone → GeographicEntity) – inverse :COVERED_BY

   :HAS_CROSSING (Border → GeographicEntity)

   :CLASSIFIED_AS (GeographicEntity → DisasterZone) – inverse :CLASSIFIES_REGION

   :TRIGGERED_BY (DisplacementEvent → Event)

   :AFFECTS (Entity → Entity) – symmetric

   :COMPOUNDS (Situation → Situation) – symmetric

   :LED_TO (Event → ProtectionIncident)

   :CONSTRAINS_ACCESS_TO (AccessConstraint → GeographicEntity) – inverse :ACCESS_CONSTRAINED_BY

   :ESCALATED_TO (ProtectionIncident → Situation)

   :DISPLACED_FROM (PopulationGroup → GeographicEntity)

   :DISPLACED_TO (PopulationGroup → GeographicEntity)

   :TRANSITING_THROUGH (PopulationGroup → GeographicEntity)

   :REGISTERED_AS (PopulationGroup → RegistrationCohort) – inverse :REGISTERS

   :PROTECTED_BY (PopulationGroup → LegalFramework)

   :HAS_PROFILE (PopulationGroup → VulnerabilityProfile) – inverse :PROFILE_OF

   :ORGANISED_AS (PopulationGroup → CommunityStructure)

   :HOSTED_BY (PopulationGroup → Settlement) – inverse :HOSTS

   :RESPONDS_TO (Operation → Situation)

   :TARGETS (Activity → PopulationGroup) – inverse :IS_TARGETED_BY

   :DELIVERS_IN (Activity → GeographicEntity)

   :IMPLEMENTED_BY (Project → ImplementingPartner) – inverse :IMPLEMENTS_

   :PART_OF (Project → Programme) – transitive, inverse :INCLUDES

   :COORDINATES_WITH (Organisation → Organisation) – symmetric

   :OPERATES_AT (SubOffice → ServicePoint)

   :ACHIEVES (Activity → Indicator)

   :MEASURED_AGAINST (Indicator → StandardIndicator)

   :HAS_INTERVENTION_TYPE (Activity → InterventionType)

   :HAS_PARTICIPATION (IATIActivity → Participation)

   :HAS_SECTOR (IATIActivity → Sector)

   :HAS_LOCATION (IATIActivity → IATILocation)

   :HAS_RECIPIENT_REGION (IATIActivity → RecipientRegion)

   :REPRESENTS_OPERATION (IATIActivity → Operation)

   :PARTICIPATION_ORG (Participation → Organisation)

   :APPLIES_TO (LegalFramework → PopulationGroup)

   :SUPERSEDES (DocumentaryArtifact → DocumentaryArtifact)

   :IMPLEMENTS (Operation → LegalFramework)

   :CONFLICTS_WITH (LegalFramework → LegalFramework) – symmetric

   :MANDATES (LegalFramework → Activity) – inverse :MANDATED_BY

   :GOVERNS (LegalFramework → PopulationGroup) – inverse :GOVERNED_BY

   :REFERENCES (DocumentaryArtifact → Entity)

   :ENDORSED_BY (Policy → Organisation)

   :FUNDS (Donor → Project) – inverse :FUNDED_BY

   :ALLOCATED_TO (FundingInstrument → Project) – inverse :ALLOCATED_FROM

   :CONTRIBUTES_TO (FundingInstrument → Budget)

   :REQUESTED_IN (Budget → FundingAppeal)

   :SPENT_ON (Expenditure → Activity)

   :COMMITTED_TO (PledgeCommitment → Operation)

   :HAS_TRANSACTION (IATIActivity → IATITransaction)

   :TRANSACTION_PROVIDER_ORG (IATITransaction → Organisation)

   :PROVIDER_ORG_IS_DONOR (IATITransaction → Donor)

   :HAS_CONTACT_INFO (IATIActivity → ContactInfo)

   :REPORTED_BY (IATIActivity → Organisation)

   :DOCUMENTS (DocumentaryArtifact → Entity)

   :CITES (DocumentaryArtifact → DocumentaryArtifact)

   :PRODUCED_BY (DocumentaryArtifact → Organisation) – inverse :PRODUCED

   :INFORMS (EvidenceFinding → Policy)

   :RECORDS (Assessment → Indicator)

   :UPDATES (SituationReport → Situation)

   :TRAINED_ON (TrainingMaterial → InterventionType)

   :EVALUATES (Evaluation → Programme)

   :PRODUCES (Evaluation → EvidenceFinding)

   :APPLIES_IN (InterventionType → ContextCondition)

   :CONTRADICTS (EvidenceFinding → EvidenceFinding) – symmetric

   :CORROBORATES (EvidenceFinding → EvidenceFinding) – symmetric

   :ENABLED_BY (InterventionType → ContextCondition) – inverse :ENABLES

   :RISK_OF (InterventionType → UnintendedEffect)

   :COMPARED_TO (EffectivenessMetric → EffectivenessMetric) – symmetric

   :GENERATED_FROM (LessonsLearned → EvidenceFinding)

All edges must include:

   source_document_id (reference to the document node that provided the evidence)

   confidence (float 0‑1)

   created_at (datetime)

   verification_status (same as node status)

Indexes & Constraints:

   Unique constraint on identifier for all nodes.

   Index on name (if present) and hasTag for text search.

   Geospatial index on geo:lat/geo:long for location queries.

   Composite indexes for frequently queried property combinations (e.g., country + crisis).

   Full‑text search indexes on textual properties like title, description, raw_text_snippet.

Implementation Details:

   Use Neo4j 5+ with APOC library for advanced graph procedures.

   Use the neo4j Python driver (async) in the backend.

   Provide a set of Cypher scripts to create the schema, indexes, and constraints.

   Include a script to seed the graph with initial reference data (e.g., countries, standard indicators).

Testing:

   Provide unit tests that verify node creation, property assignment, and relationship traversal.

   Include tests for temporal versioning queries (retrieving latest value, historical trend).