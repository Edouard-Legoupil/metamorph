# UNHCR Knowledge Ontology (HKO)


**File:** `unhcr-knowledge-ontology.ttl`

---

## What this ontology is

The UNHCR Knowledge Ontology (HKO) is an OWL/SKOS ontology expressed in Turtle that provides a structured vocabulary for UNHCR's operational, legal, financial, and humanitarian knowledge. It was designed specifically to support **Retrieval-Augmented Generation (RAG) pipelines** and **agentic knowledge graph construction** — meaning that when documents are ingested and indexed, their extracted entities resolve against typed, connected nodes rather than generating isolated text fragments.

The ontology covers ten thematic domains (A–J), plus a set of SKOS controlled vocabularies. It aligns with the **IATI standard** for financial transparency and is deployable as a Neo4j property graph or any RDF triple store.

---

## Ontology structure

### Domains A–H  (operational knowledge)

| Domain | Theme | Key classes |
|--------|-------|-------------|
| **A** | Geographic | `Country`, `Region`, `Settlement`, `OperationalZone`, `Border`, `IATILocation` |
| **B** | Situation & Context | `Situation`, `DisplacementEvent`, `ConflictEvent`, `HazardEvent`, `ProtectionIncident` |
| **C** | Population & Beneficiaries | `PopulationGroup`, `HouseholdProfile`, `VulnerabilityProfile`, `RegistrationCohort` |
| **D** | Operational & Programmatic | `Operation`, `Programme`, `Project`, `Activity`, `IATIActivity`, `ImplementingPartner` |
| **E** | Policy, Legal & Normative | `LegalFramework`, `Policy`, `SOP`, `NationalLaw`, `ExComConclusion`, `PledgeCommitment` |
| **F** | Finance & Resources | `Donor`, `Budget`, `Expenditure`, `FundingInstrument`, `IATITransaction`, `FundingAppeal` |
| **G** | Stakeholders | `Organisation`, `Person`, `Role`, `Position`, `FocalPoint` |
| **H** | Knowledge & Information | `Indicator`, `EvidenceFinding`, `InterventionType`, `LessonsLearned`, `EffectivenessMetric` |

### Domain I  (knowledge provenance — v0.2)

Domain I is the curation backbone. It tracks how every assertion in the graph originated, was verified, and was resolved.

```
DocumentVersion → ContentChunk / Section / WikiBlock
                       ↓
                  EvidenceSpan
                       ↓
                    Claim  ←── ExtractionRun
                       ↓
                CanonicalFact ←── CuratorDecision ←── ReviewTask
                                        ↑
                                 ConflictRecord
```

| Class | Purpose |
|-------|---------|
| `DocumentVersion` | Immutable snapshot of a document at ingestion time (carries SHA-256 hash) |
| `ContentChunk` | Paragraph-level text unit with character offsets and embedding model reference |
| `Section` | Structural heading node grouping chunks within a document |
| `WikiBlock` | ContentChunk sourced from a wiki platform (Confluence, MediaWiki); carries page/revision IDs |
| `EvidenceSpan` | Sentence-level span that directly supports or refutes a Claim |
| `Claim` | An atomic factual assertion, machine-extracted or human-authored, with a confidence score |
| `CanonicalFact` | A verified, authoritative statement accepted by a curator |
| `ConflictRecord` | A logged tension between two or more incompatible Claims |
| `CuratorDecision` | The documented outcome of a curator adjudicating a conflict or validating a claim |
| `ExtractionRun` | A logged NLP/AI pipeline execution that produced Claims from DocumentVersions |
| `ReviewTask` | A work item assigned to a reviewer with priority, deadline, and status |
| `KnowledgeCard` | A curated summary of one or more CanonicalFacts for display or briefing use |

### Domain J  (SKOS controlled vocabularies — v0.2)

All enumerated value spaces are expressed as `skos:ConceptScheme` instances rather than raw strings. This enables controlled filtering, multilingual labels, and provenance-aware reasoning.

| Scheme | Concepts | Used by |
|--------|----------|---------|
| `VerificationStateScheme` | Verified, Unverified, Pending, Disputed, Retracted, Superseded | `Claim`, `Entity` |
| `ConflictClassScheme` | Numerical Discrepancy, Temporal Inconsistency, Source Contradiction, Classification Mismatch, Geographic Ambiguity, Duplication | `ConflictRecord` |
| `SeverityScheme` | Critical (SV-4), High (SV-3), Medium (SV-2), Low (SV-1), Informational (SV-0) | `ConflictRecord`, `ReviewTask` |
| `DocumentTypeScheme` | SitRep, Assessment, Evaluation, Policy, SOP, Guidance, FundingAppeal, ActivityReport, Dataset, TrainingMaterial, LegalInstrument | `DocumentaryArtifact` |
| `InterventionCategoryScheme` | Protection, Shelter, WASH, Health & Nutrition, Education, Livelihoods, Cash-Based, Durable Solutions, Registration, GBV | `InterventionType` |
| `SourceTrustScheme` | Primary Source (ST-1) → Peer-Reviewed → Official Report → Grey Literature → Media → Unverified Open Source (ST-6) | `Claim` |
| `ReviewOutcomeScheme` | Open, InProgress, Accepted, Rejected, Amended, Deferred, Escalated | `ReviewTask`, `CuratorDecision` |

---

## Domain G — Stakeholder modeling pattern (v0.2)

Version 0.2 replaces the flat Position-as-Organisation pattern with a four-class model that clearly separates people, roles, posts, and institutions.

```
Person  ──holdsRole──►  Role
  │
  ├──assignedTo──►  Position  ──positionIn──►  Organisation
  │                    │
  │                    ├──carriesRole──►  Role
  │                    │
  │    (if FocalPoint)─└──focalFor──►  ClusterSector / GeographicEntity / InterventionType
  │
  └──memberOf──►  Organisation
```

**Rules:**
- A `Person` is a human being (staff, consultant, partner contact). It does **not** subclass `Organisation`.
- A `Role` is a reusable functional descriptor (e.g., "Protection Officer"). Roles are not posts.
- A `Position` is a funded HR post — it can be vacant. It belongs to exactly one `Organisation`.
- A `FocalPoint` is a `Position` (not a person). The person *fills* the focal-point position; the position itself carries the `:focalFor` scope link.

---

## Core OWL concepts — plain-language reference

### Class
A class is a category of things. Think of it as a typed folder.

```turtle
:Country a owl:Class .           # all sovereign states
:PopulationGroup a owl:Class .   # groups of persons of concern
:IATITransaction a owl:Class .   # financial transactions from IATI
```

### Subclass
A subclass is a more specific version of another class. All members of the subclass are also members of the parent.

```turtle
:Donor        rdfs:subClassOf :Organisation .
:FocalPoint   rdfs:subClassOf :Position .
:Expenditure  rdfs:subClassOf :IATITransaction .
```

### ObjectProperty
An object property links one entity to another entity.

```turtle
:Geneva  :locatedIn  :Switzerland .
:SSD24   :respondsTo :SudanSituation .
:Act001  :implementedBy :PartnerNGO .
```

### DatatypeProperty
A datatype property links an entity to a literal value (string, integer, date, decimal).

```turtle
:Kenya  :iso3  "KEN" .
:KakumaCamp  :populationFigure  185000 .
:IATI-XK-2024  :transactionValue  1000000.00 .
```

### Inverse properties
Most key relationships have declared inverses, so you can traverse the graph in either direction without redundant data:

```turtle
:locatedIn  owl:inverseOf  :contains .
:funds      owl:inverseOf  :fundedBy .
:assignedTo owl:inverseOf  :filledBy .
```

### N-ary relations
Where a relationship itself carries attributes (e.g., an organisation's *role* in an IATI activity), an intermediate node is used:

```turtle
:activity01  :hasParticipation  :p01 .
:p01  :participationOrg      :UNHCR .
:p01  :participationRoleCode "1" .   # Funding
```

---

## Deploying as a Neo4j property graph

| OWL construct | Neo4j equivalent |
|---------------|-----------------|
| Class | Node label (apply most-specific + all ancestor labels) |
| Subclass | Multiple labels on the same node |
| ObjectProperty | Relationship type (e.g., `LOCATED_IN`, `FUNDS`) |
| DatatypeProperty | Node property |
| Inverse property | Traverse the single stored direction in reverse; `owl:inverseOf` is documentation only |
| Transitive property | Query with `*` in Cypher; not enforced at DB level |
| N-ary class (Participation) | Intermediate node with two directional relationships |

---

## Source catalogue — IATI-registered UNHCR knowledge sources

The following 15 sources are registered in UNHCR's IATI publication and serve as the primary targets for automated scraping and ingestion into the knowledge graph.

| Code | Source | URL | Domain(s) | Ingestion round |
|------|--------|-----|-----------|-----------------|
| A01 | UNHCR Microdata Library | https://microdata.unhcr.org | C / H | 2 |
| A06 | UNHCR Contract Awards (UNGM) | https://www.ungm.org/Public/ContractAward?agencyEnglishAbbreviation=UNHCR | D / F | 3 |
| A07 | UNHCR Evaluations Library | https://www.unhcr.org/evaluation | H | 3 |
| A10 | UNHCR Tender Notices (UNGM) | https://www.ungm.org/Public/Notice?agencyEnglishAbbreviation=UNHCR | D / F | 3 |
| A12 | Operations Website | http://reporting.unhcr.org/operations | D | 1 |
| B02 | UNHCR Strategic Directions 2022–26 | https://intranet.unhcr.org/en/about/strategic-directions.html | E | 1 |
| B16 | UNHCR Population Data | https://www.unhcr.org/population-data.html | C / A | 1 |
| B16 | Figures at a Glance | https://www.unhcr.org/figures-at-a-glance.html | C | 1 |
| B16 | UNHCR Main Website | https://www.unhcr.org/ | G / E | 1 |
| B16 | UNHCR IATI Overview | http://reporting.unhcr.org/iati | F / D | 2 |
| B16 | Help.UNHCR | https://help.unhcr.org/ | E / C | 1 |
| B16 | UNHCR Arabic | http://www.unhcr.org/ar/ | B / C | 2 |
| B16 | UNHCR French | http://www.unhcr.org/fr/ | B / C | 2 |
| B16 | UNHCR Spanish | http://www.unhcr.org/es/ | B / C | 2 |
| B16 | UNHCR Russian | http://www.unhcr.ru/ | B / C | 2 |
| B17 | Refugee Funding Tracker | http://refugee-funding-tracker.org/ | F | 2 |

---

## Web scraping and ingestion strategy

### Core principle

Build the graph **bottom-up**: index stable master data first. A document ingested against an empty graph creates orphan literals. The same document ingested against a populated graph creates connected triples that are immediately retrievable and resolvable.

```
Round 1  →  Round 2  →  Round 3
(anchors)   (context)   (evidence & transactions)
```

---

### Round 1 — Reference and master data  *(index first)*

These sources change rarely and form the stable foundation every other document references.

#### A — Geographic anchors

**Sources:** Operations Website (A12), Population Data (B16)  
**Target classes:** `Country` (ISO-3), `Region` / `Settlement`, `OperationalZone`, `Border`

**Scraping approach:**

```
A12: reporting.unhcr.org/operations
  → Crawl the per-operation index page
  → For each operation: extract country code (ISO-3 from URL slug or metadata)
  → Mint :Country, :OperationalZone nodes
  → Link :Operation to :Country via :locatedIn

B16: unhcr.org/population-data.html
  → Parse the downloadable statistics tables (CSV or embedded JSON)
  → Extract country × population-group × year triples
  → Bind to existing :Country nodes; create :PopulationGroup stubs
```

**Priority:** highest — every subsequent entity depends on a resolved `:Country` or `:GeographicEntity`.

---

#### E — Policy, legal, and normative frameworks

**Sources:** Strategic Directions (B02), Main Website (B16), Help.UNHCR (B16)  
**Target classes:** `LegalFramework`, `Policy`, `SOP`, `StandardIndicator`, `PledgeCommitment`

**Scraping approach:**

```


B16: unhcr.org/  (legal instruments section)
  → Convert PDF to text (pdftotext or Docling)
  → Extract as :Policy node; policyCode = 'SD2022-2026'
  → Parse strategic goal headings → :StandardIndicator nodes
  → Extract commitments → :PledgeCommitment nodes
  → Crawl /refworld/ and /legal/ subsections
  → Each instrument: title, date, instrument type → :LegalFramework node
  → Map instrument type to :DocumentTypeScheme concept (e.g., DT-LEGAL)

B16: help.unhcr.org
  → Crawl country-specific guidance pages
  → Extract :SOP nodes linked to :Country; bind :protectedBy to :LegalFramework
```

---

#### G — Stakeholders and organisations

**Sources:** Main Website (B16), Operations Website (A12)  
**Target classes:** `Organisation` subtypes, `UNAgency`, `NGOPartner`, `GovernmentAuthority`, `Donor`

**Scraping approach:**

```
B16: unhcr.org/partners/
  → Parse partner directory: name, type, country presence
  → Classify each org → apply most specific :Organisation subclass
  → Deduplicate against IATI organisation register (use IATI org-id as :identifier)

A12: reporting.unhcr.org/operations/<iso3>/
  → Each operation page lists implementing partners
  → Create :ImplementingPartner nodes; :coordinatesWith links to :UNAgency nodes
```

**Note:** Organisations are master data. Mint new IRIs only if no existing match on IATI org-id or name. Record source URI in named graph metadata.

---

#### C — Population aggregate statistics

**Sources:** Population Data (B16), Figures at a Glance (B16)  
**Target classes:** `PopulationGroup` (top-level stubs), `RegistrationCohort` (skeleton)

**Scraping approach:**

```
B16: unhcr.org/figures-at-a-glance.html
  → Parse headline statistics table or the UNHCR Data API equivalent
  → Endpoint: https://api.unhcr.org/population/v1/population/
  → Extract rows: country × population type × year → :PopulationGroup aggregate node
  → groupType property → bind to :InterventionCategoryScheme concept (IC-PROT etc.)
```

---

### Round 2 — Operational context  *(index second)*

These sources are only fully resolvable once Round 1 nodes exist in the graph.

#### B — Situation and context

**Sources:** Operations Website (A12), multilingual sites (B16 ar/fr/es/ru)  
**Target classes:** `Situation`, `DisplacementEvent`, `ConflictEvent`, `HazardEvent`, `AccessConstraint`

**Scraping approach:**

```
A12: reporting.unhcr.org/operations/<iso3>/
  → Parse the situation narrative section of each operation page
  → Run NER + relation extraction to identify:
      - named conflict events → :ConflictEvent nodes
      - displacement triggers → :DisplacementEvent; :triggeredBy → :ConflictEvent
      - access constraints → :AccessConstraint; :constrainsAccessTo → :Region

B16 ar/fr/es/ru:
  → These sites carry regionally relevant situation narratives not always present in EN
  → Scrape in parallel; deduplicate by canonical URL + publication date
  → Store as additional :ContentChunk nodes on the same :DocumentVersion
  → Use skos:altLabel on entity nodes for multilingual label variants
```

**Key rule:** deduplicate across language variants before minting nodes. One canonical node per real-world entity; language labels go to `skos:altLabel`.

---

#### C — Population detail (household and vulnerability)

**Sources:** Microdata Library (A01), multilingual sites (B16)  
**Target classes:** `HouseholdProfile`, `VulnerabilityProfile`, `CommunityStructure`, `RegistrationCohort`

**Scraping approach:**

```
A01: microdata.unhcr.org — DDI-compliant catalog API
  Endpoint: https://microdata.unhcr.org/index.php/api/catalog/search
  → Iterate pages; for each dataset entry extract:
      - country (iso3), year, survey type, producing org, variables list
  → Map: survey type → :Assessment subclass
          variables    → :Indicator codes
          country      → resolve to existing :Country node
  → Household-level records → :HouseholdProfile; :hostedBy → :Settlement
  → Collection tags (PRM, SENS, VUL) → bind :programmeType or :InterventionType
```

---

#### D — Operations and programmes

**Sources:** Operations Website (A12), IATI Overview (B16)  
**Target classes:** `Operation`, `Programme`, `Project`, `Activity`, `IATIActivity`, `ImplementingPartner`

**Scraping approach:**

```
A12: reporting.unhcr.org/operations/<iso3>/
  → Operation slug → :operationCode; link :Operation to :Country
  → Programme sections → :Programme nodes; :partOf → :Operation
  → Partner list → resolve against existing :Organisation nodes from Round 1

B16: reporting.unhcr.org/iati  (machine-readable IATI XML)
  IATI XML endpoint: http://reporting.unhcr.org/iati/activities.xml
  → Parse each <iati-activity>:
      iati-identifier          → :hasIATIIdentifier
      <participating-org>      → :Participation N-ary node; participationRoleCode
      <transaction>            → :IATITransaction; :transactionProviderOrg → :Donor
      <sector> (DAC vocab)     → :Sector; :hasSector from :IATIActivity
      <recipient-country>      → resolve :Country (ISO-3)
  → :representsOperation: fuzzy-match activity title against known :Operation nodes
    (use iso3 code as primary key, then string similarity on title)
```

**IATI XML is the most structured source available — parse directly, no NLP required.**

---

#### F — Financial flows (aggregate)

**Sources:** IATI Overview (B16), Refugee Funding Tracker (B17)  
**Target classes:** `FundingAppeal`, `Budget` (aggregate), `IATITransaction` (summary), `FundingInstrument`

**Scraping approach:**

```
B17: refugee-funding-tracker.org
  → Access the embedded Power BI API or CSV export endpoint
  → Response plan rows → :FundingAppeal; :requestedIn from :Budget
  → Funding contribution rows → :FundingInstrument; :funds → :Project or :Operation
  → Donor column → resolve against :Donor master list from Round 1 (G domain)
```

---

### Round 3 — Evidence and transactional data  *(index last)*

These sources consume the full graph and close the knowledge loop. They point back at programmes, activities, donors, and geographic contexts established in Rounds 1–2.

#### H — Knowledge and evidence

**Sources:** Evaluations Library (A07), Microdata Library (A01)  
**Target classes:** `Evaluation`, `EvidenceFinding`, `LessonsLearned`, `EffectivenessMetric`, `Indicator`

**Scraping approach:**

```
A07: unhcr.org/evaluation
  → Crawl the evaluation catalog; for each report:
      - Fetch PDF → convert to text → create :DocumentVersion (with SHA-256 hash)
      - Top-level document → :Evaluation; :evaluates → :Programme or :Operation
      - Section headings → :Section nodes; paragraphs → :ContentChunk nodes
      - Findings section → :EvidenceFinding; :produces from :Evaluation
      - Recommendations → :LessonsLearned; :generatedFrom → :EvidenceFinding
      - Create :ExtractionRun record linking all produced :Claim nodes
  → Store chunk-level embeddings; anchor each chunk to its :EvidenceFinding node
```

---

#### F — Finance transactional detail

**Sources:** Contract Awards (A06), Tender Notices (A10)  
**Target classes:** `Expenditure`, `IATITransaction` (line-level), `FundingInstrument`, `Participation`

**Scraping approach:**

```
A06: ungm.org/Public/ContractAward?agencyEnglishAbbreviation=UNHCR
  → Parse HTML award table: date, supplier name, value, description, UNCCS code
  → Contract award → :Expenditure; :spentOn → :Activity (match via description + country)
  → Supplier → resolve or create :ImplementingPartner; :implementedBy from :Project

A10: ungm.org/Public/Notice?agencyEnglishAbbreviation=UNHCR
  → Tender notice → :FundingInstrument intent
  → On award confirmation (cross-reference A06): promote to :Expenditure
  → UNCCS commodity code → map to :InterventionCategoryScheme concept
```

---

### Source-specific technical notes

#### A01 — UNHCR Microdata Library

The catalog API returns DDI-compliant XML. Each dataset entry provides: country, year, survey type, variable list, and producing organisation. Map `survey_type` to `:Assessment` subclasses; variables to `:Indicator` codes; `country` to `:Country` via ISO-3.

#### A06 / A10 — UNGM Contract Awards and Tender Notices

HTML tables. Fields: award date, supplier, value (USD), description, UNCCS commodity code. Commodity codes provide a reliable bridge to `:InterventionType` nodes. Reconcile supplier names against the organisation master list from Round 1 before minting new IRIs.

#### A07 — UNHCR Evaluations Library

PDF reports with standard sections (background, methodology, findings, recommendations). Use Docling or pdftotext for extraction. Each PDF becomes one `:DocumentVersion`. Apply sentence-level chunking for `:ContentChunk` nodes; preserve section structure in `:Section` nodes for retrieval context.

#### A12 — Operations Website

Per-operation pages are the primary seed for Domain D and Domain B. The URL slug (`/operations/<iso3>`) provides the ISO-3 country code for geographic resolution. Situation narrative text is the richest source of `:Situation` and `:DisplacementEvent` nodes.

#### B02 — Strategic Directions 2022–2026

Intranet PDF. Fetch once; treat as immutable until the next planning cycle. Index as a single `:Policy` node with `policyCode = 'SD2022-2026'`. Strategic goals map to `:StandardIndicator` nodes that anchor results framework alignment across evaluations.

#### B16 — IATI XML feed

The most structurally clean source. Parse `<iati-activity>` elements directly without NLP. Use `<iati-identifier>` as the globally unique key for `:IATIActivity` nodes. Reconcile `<recipient-country>` ISO-2 codes against the ISO-3 `:Country` master list (maintain a mapping table).

#### B17 — Refugee Funding Tracker

Power BI dashboard with an embedded API. The CSV export option is more stable than the API for batch extraction. Donor column values must be fuzzy-matched against the `:Donor` master list; do not create duplicate organisation nodes.

---

## Graph quality rules

Apply these checks at every ingestion step to prevent graph degradation.

| Check | Rule | Remediation |
|-------|------|-------------|
| **Orphan prevention** | Before minting a new entity node, query for existing matches on ISO-3, IATI identifier, or operation code | Link to the existing node; mint a new IRI only if no match found |
| **Provenance tagging** | Every triple must carry a `:createdAt` timestamp and a source URI in named-graph metadata | Reject triples lacking provenance; quarantine to a review graph |
| **Round gate** | Round N sources must not reference entity types seeded exclusively by Round N+1 | Validate against the ontology dependency matrix before loading each batch |
| **Language deduplication** | Arabic / French / Spanish / Russian sites carry duplicate content | Deduplicate by canonical URL + publication date; one node, `skos:altLabel` per language |
| **IATI reconciliation** | Every `:IATIActivity` `:representsOperation` link must resolve to an existing `:Operation` node | Unresolved activities enter a reconciliation queue; review weekly |
| **Evaluation linkage** | Every `:Evaluation` must link to at least one `:Programme` or `:Operation` before being indexed | Block indexing until the mandatory link is supplied by the metadata enrichment step |
| **Claim verification** | Every `:Claim` must carry a `:claimVerificationStatus` from `:VerificationStateScheme` | Default to `:vsUnverified` on extraction; update after curator review |
| **Conflict detection** | Before promoting a `:Claim` to `:CanonicalFact`, query for contradicting claims on the same subject | If found, create a `:ConflictRecord`; assign a `:ReviewTask` with appropriate `:severity` |

---

## Prefixes

```turtle
@prefix :        <https://proposalgen.unhcr.org/ontology/hko#> .
@prefix rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix owl:     <http://www.w3.org/2002/07/owl#> .
@prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:     <http://www.w3.org/2001/XMLSchema#> .
@prefix dc:      <http://purl.org/dc/elements/1.1/> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix skos:    <http://www.w3.org/2004/02/skos/core#> .
@prefix geo:     <http://www.w3.org/2003/01/geo/wgs84_pos#> .
@prefix foaf:    <http://xmlns.com/foaf/0.1/> .
```


