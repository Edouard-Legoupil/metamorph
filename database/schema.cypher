// ==================== Universal Constraints (all nodes) ===================
CREATE CONSTRAINT entity_identifier_unique IF NOT EXISTS FOR (n:Entity) REQUIRE n.identifier IS UNIQUE;
CREATE INDEX entity_hasTag IF NOT EXISTS FOR (n:Entity) ON (n.hasTag);
// ==================== Major Node Classes by Domain =======================
// --- GEOGRAPHY ---
CREATE CONSTRAINT ON (n:Country) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:Region) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:Settlement) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:Border) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:OperationalZone) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:DisasterZone) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:RecipientRegion) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:IATILocation) ASSERT n.identifier IS UNIQUE;
CREATE POINT INDEX geo_point_idx IF NOT EXISTS FOR (n:GeographicEntity) ON (n.geo_lat, n.geo_long);
CREATE INDEX country_name IF NOT EXISTS FOR (n:Country) ON (n.name);
CREATE INDEX region_pcode IF NOT EXISTS FOR (n:Region) ON (n.pcode);
// --- SITUATION & CONTEXT ---
CREATE CONSTRAINT ON (n:Situation) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:DisplacementEvent) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:HazardEvent) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:ConflictEvent) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:ProtectionIncident) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:AccessConstraint) ASSERT n.identifier IS UNIQUE;
// --- POPULATION ---
CREATE CONSTRAINT ON (n:PopulationGroup) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:HouseholdProfile) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:VulnerabilityProfile) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:CommunityStructure) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:RegistrationCohort) ASSERT n.identifier IS UNIQUE;
// --- OPERATIONAL ---
CREATE CONSTRAINT ON (n:Operation) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:Programme) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:Project) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:Activity) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:IATIActivity) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:Participation) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:SubOffice) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:ImplementingPartner) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:ServicePoint) ASSERT n.identifier IS UNIQUE;
// --- POLICY & LEGAL ---
CREATE CONSTRAINT ON (n:Policy) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:SOP) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:LegalFramework) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:NationalLaw) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:ExComConclusion) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:PledgeCommitment) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:StandardIndicator) ASSERT n.identifier IS UNIQUE;
// --- FINANCE ---
CREATE CONSTRAINT ON (n:Donor) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:FundingInstrument) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:Budget) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:Expenditure) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:FundingAppeal) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:IATITransaction) ASSERT n.identifier IS UNIQUE;
CREATE INDEX project_code IF NOT EXISTS FOR (n:Project) ON (n.projectCode);
CREATE INDEX indicator_code IF NOT EXISTS FOR (n:Indicator) ON (n.indicatorCode);
// --- STAKEHOLDERS ---
CREATE CONSTRAINT ON (n:Organisation) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:UNAgency) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:ClusterSector) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:NGOPartner) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:PrivateDonor) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:GovernmentAuthority) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:Position) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:FocalPoint) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:ContactInfo) ASSERT n.identifier IS UNIQUE;
// --- KNOWLEDGE ---
CREATE CONSTRAINT ON (n:Indicator) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:InterventionType) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:EvidenceFinding) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:EffectivenessMetric) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:ContextCondition) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:LessonsLearned) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:UnintendedEffect) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:Document) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:Assessment) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:SituationReport) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:ActivityReport) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:TrainingMaterial) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:Dataset) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:Evaluation) ASSERT n.identifier IS UNIQUE;
CREATE CONSTRAINT ON (n:Sector) ASSERT n.identifier IS UNIQUE;
// ==== FULLTEXT & COMPOSITE INDEXES ====
CALL db.index.fulltext.createNodeIndex("fulltext_titles", ["DocumentaryArtifact", "SituationReport", "Assessment", "Policy", "LegalFramework", "ActivityReport", "Programme", "Project", "Evaluation"], ["title", "description", "raw_text_snippet"]);
// ==== RELATIONSHIP INDEXES (all rels get traceability) ====
CREATE INDEX rel_source_document IF NOT EXISTS FOR ()-[r]-() ON (r.source_document_id);
CREATE INDEX rel_confidence IF NOT EXISTS FOR ()-[r]-() ON (r.confidence);
// ==== DOCUMENTARY ARTIFACT SUBCLASS LABELS ==== (handled at ingest)
// ==== RELATIONSHIPS ==== (handled at ingest, see code docs or ontology for full mapping)
