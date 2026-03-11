

# 1. Class

Plain‑language meaning: A class is a category of things in your world.
Think of classes as folders that group similar items.
Examples in your ontology

Country → a class for all countries
PopulationGroup → a class for groups of people
Operation → a class for UNHCR operations
IATITransaction → a class for transactions from IATI

Analogy
A “class” is like saying:

“This is the type of thing we are talking about.”

Why classes matter
They help the knowledge graph understand what kind of things exist.

#  2. Subclass
Plain‑language meaning:
A subclass is a more specific version of another class.
It’s how you say:

“This thing is a special kind of that thing.”

Examples in your ontology

Region is a subclass of Entity
Donor is a subclass of Organisation
IATILocation is a subclass of Settlement

Analogy
If Fruit is a class, then
Apple is a subclass of Fruit.
Why subclasses matter
They allow the ontology to structure knowledge from general → specific, which improves:

classification
search
querying
consistency


#  3. ObjectProperty
Plain‑language meaning:
An object property expresses a relationship between two entities.
It connects one thing → to another thing.

Examples in your ontology

locatedIn

Settlement → Region


fundedBy

Any Entity → Donor


hasSector

Activity → Sector


hasTransaction

IATIActivity → IATITransaction


participationOrg

Participation → Organisation



Analogy
A relationship like:

“Geneva is located in Switzerland.”

In TTL:
Turtle:Geneva :locatedIn :Switzerland .Show more lines
Why object properties matter
They build the graph structure.
Without them, the graph would just be a list of disconnected items.

# 4. DatatypeProperty
Plain‑language meaning:
A datatype property connects an entity to a literal value such as:

text
number
date
boolean

It describes the attributes or details of things.
Examples in your ontology

iso3

Country → "AFG"


population_figure

Settlement → 450000


operation_code

Operation → "SSD24"


transactionValue

IATITransaction → 1000000.00


sectorCode

Sector → "720"



Analogy
Think of a table:


CountryISO3KenyaKEN
This corresponds in TTL to:
Turtle:Kenya :iso3 "KEN" .Show more lines


Why datatype properties matter
They allow you to store details like:

names
dates
codes
coordinates
financial amounts

They make the knowledge graph useful for analysis.



https://microdata.unhcr.org 
UNHCR Microdata Library
            <category code="A01"/>
            <language code="en"/>


https://www.ungm.org/Public/ContractAward?agencyEnglishAbbreviation=UNHCR
UNHCR Contract Awards - UN Global Marketplace
            <category code="A06"/>
            <language code="en"/>


https://www.unhcr.org/evaluation
UNHCR Evaluations Library
            <category code="A07"/>
            <language code="en"/>


https://www.ungm.org/Public/Notice?agencyEnglishAbbreviation=UNHCR
UNHCR Tender Notices - UN Global Marketplace
            <category code="A10"/>
            <language code="en"/>


http://reporting.unhcr.org/operations
Operation Website
            <category code="A12"/>
            <language code="en"/>


https://intranet.unhcr.org/en/about/strategic-directions.html
UNHCR Strategic Directions 2022-2026
            <category code="B02"/>
            <language code="en"/>


http://www.unhcr.org/ar/
المفوضية السامية للأمم المتحدة لشؤون اللاجئين
            <category code="B16"/>
            <language code="ar"/>

https://help.unhcr.org/
Information for Refugees, Asylum-seekers and Stateless People
            <category code="B16"/>
            <language code="en"/>

https://www.unhcr.org/population-data.html
Population Data
            <category code="B16"/>
            <language code="en"/>

https://www.unhcr.org/figures-at-a-glance.html
UNHCR - Figures at a glance
            <category code="B16"/>
            <language code="en"/>

https://www.unhcr.org/
UNHCR - The UN Refugee Agency
            <category code="B16"/>
            <language code="en"/>

http://reporting.unhcr.org/iati
UNHCR IATI Overview
            <category code="B16"/>
            <language code="en"/>

http://www.unhcr.org/es/
ACNUR La Agencia de la ONU para los Refugiados
            <category code="B16"/>
            <language code="es"/>

http://www.unhcr.org/fr/
UNHCR L'Agence des Nations Unies pour les réfugiés
            <category code="B16"/>
            <language code="fr"/>

http://www.unhcr.ru/
Агентство ООН по делам беженцев
            <category code="B16"/>
            <language code="ru"/>

http://refugee-funding-tracker.org/
Refugee Response Financial Tracking Dashboards
            <category code="B17"/>
            <language code="en"/>

## Document Ingestion Strategy

for RAG ingestion to work well, we build the graph bottom-up so that when we index a document, its entities can resolve against already-existing nodes rather than creating orphans.  A document indexed against an empty graph creates orphan literals; a document indexed against a populated graph creates connected triples. H is intentionally last because Evaluation and EvidenceFinding point back at Programme, Activity, Situation, Policy — they need those nodes to already exist to be meaningful.

Here's the strategic indexing orderg:

Round 1 — Reference/Master Data (stable, shared anchors)

A — Geographic first: countries, regions, settlements are the most universal anchors. Nearly every document references a place.
E — Policy, Legal & Normative next: conventions, frameworks, SOPs are frequently cited and rarely change. They anchor document provenance.
G — Stakeholders / Organisations third: donors, UN agencies, NGOs, government authorities — again stable master data that most documents reference.


Round 2 — Operational Context (situational backbone)

B — Situation & Context: displacement events, conflict events, hazards. These give documents their why.
C — Population & Beneficiaries: population groups, registration cohorts, vulnerability profiles. These give documents their who.
D — Operational & Programmatic: operations, programmes, projects, activities, IATI activities. These give documents their what is being done.


Round 3 — Financial & Evidence Layer (dependent on round 2)

F — Finance & Resources: budgets, expenditures, IATI transactions — only meaningful once operations and donors exist in the graph.
H — Knowledge & Information: indicators, evidence findings, lessons learned, evaluations — these consume all prior domains and close the loop.

**UNHCR Knowledge Graph**

Document Indexing Pipeline

Strategic Ingestion Plan — v1.0

March 2026

# **Overview**

This document defines the strategic order and operating procedures for indexing UNHCR published documents into the UNHCR Knowledge Graph (HKO ontology v0.2). The core principle is: index stable master data first, so that when transactional documents are ingested, their entities resolve against existing graph nodes rather than generating orphan literals.

Fifteen authoritative UNHCR source systems have been catalogued and assigned to one of three ingestion rounds, each mapped to the eight ontology domains (A–H).

# **Source Catalogue**

All 15 identified UNHCR source systems are listed below with their assigned ontology domain(s) and ingestion round. Round colours: green = Round 1, blue = Round 2, amber = Round 3.

<table>
  <tr>
   <td>

**Code**

</td>
   <td>

**Source**

</td>
   <td>

**URL**

</td>
   <td>

**Domain**

</td>
   <td>

**Round**

</td>
  </tr>
  <tr>
   <td>

**A01**

</td>
   <td>

UNHCR Microdata Library

</td>
   <td>

[https://microdata.unhcr.org](https://microdata.unhcr.org)

</td>
   <td>

C / H

</td>
   <td>

**2**

</td>
  </tr>
  <tr>
   <td>

**A06**

</td>
   <td>

UNHCR Contract Awards (UNGM)

</td>
   <td>

[https://www.ungm.org/Public/ContractAward?…](https://www.ungm.org/Public/ContractAward?agency=UNHCR)

</td>
   <td>

D / F

</td>
   <td>

**3**

</td>
  </tr>
  <tr>
   <td>

**A07**

</td>
   <td>

UNHCR Evaluations Library

</td>
   <td>

[https://www.unhcr.org/evaluation](https://www.unhcr.org/evaluation)

</td>
   <td>

H

</td>
   <td>

**3**

</td>
  </tr>
  <tr>
   <td>

**A10**

</td>
   <td>

UNHCR Tender Notices (UNGM)

</td>
   <td>

[https://www.ungm.org/Public/Notice?agency=…](https://www.ungm.org/Public/Notice?agency=UNHCR)

</td>
   <td>

D / F

</td>
   <td>

**3**

</td>
  </tr>
  <tr>
   <td>

**A12**

</td>
   <td>

Operations Website

</td>
   <td>

[http://reporting.unhcr.org/operations](http://reporting.unhcr.org/operations)

</td>
   <td>

D

</td>
   <td>

**1**

</td>
  </tr>
  <tr>
   <td>

**B02**

</td>
   <td>

UNHCR Strategic Directions 2022-26

</td>
   <td>

[https://intranet.unhcr.org/en/about/strate…](https://intranet.unhcr.org/en/about/strategic-directions.html)

</td>
   <td>

E

</td>
   <td>

**1**

</td>
  </tr>
  <tr>
   <td>

**B16**

</td>
   <td>

UNHCR Population Data

</td>
   <td>

[https://www.unhcr.org/population-data.html](https://www.unhcr.org/population-data.html)

</td>
   <td>

C / A

</td>
   <td>

**1**

</td>
  </tr>
  <tr>
   <td>

**B16**

</td>
   <td>

Figures at a Glance

</td>
   <td>

[https://www.unhcr.org/figures-at-a-glance.…](https://www.unhcr.org/figures-at-a-glance.html)

</td>
   <td>

C

</td>
   <td>

**1**

</td>
  </tr>
  <tr>
   <td>

**B16**

</td>
   <td>

UNHCR Main Website

</td>
   <td>

[https://www.unhcr.org/](https://www.unhcr.org/)

</td>
   <td>

G / E

</td>
   <td>

**1**

</td>
  </tr>
  <tr>
   <td>

**B16**

</td>
   <td>

UNHCR IATI Overview

</td>
   <td>

[http://reporting.unhcr.org/iati](http://reporting.unhcr.org/iati)

</td>
   <td>

F / D

</td>
   <td>

**2**

</td>
  </tr>
  <tr>
   <td>

**B16**

</td>
   <td>

UNHCR Arabic Site

</td>
   <td>

[http://www.unhcr.org/ar/](http://www.unhcr.org/ar/)

</td>
   <td>

B / C

</td>
   <td>

**2**

</td>
  </tr>
  <tr>
   <td>

**B16**

</td>
   <td>

Help.UNHCR (Refugees/Stateless)

</td>
   <td>

[https://help.unhcr.org/](https://help.unhcr.org/)

</td>
   <td>

E / C

</td>
   <td>

**1**

</td>
  </tr>
  <tr>
   <td>

**B16**

</td>
   <td>

UNHCR Spanish Site

</td>
   <td>

[http://www.unhcr.org/es/](http://www.unhcr.org/es/)

</td>
   <td>

B / C

</td>
   <td>

**2**

</td>
  </tr>
  <tr>
   <td>

**B16**

</td>
   <td>

UNHCR French Site

</td>
   <td>

[http://www.unhcr.org/fr/](http://www.unhcr.org/fr/)

</td>
   <td>

B / C

</td>
   <td>

**2**

</td>
  </tr>
  <tr>
   <td>

**B16**

</td>
   <td>

UNHCR Russian Site

</td>
   <td>

[http://www.unhcr.ru/](http://www.unhcr.ru/)

</td>
   <td>

B / C

</td>
   <td>

**2**

</td>
  </tr>
  <tr>
   <td>

**B17**

</td>
   <td>

Refugee Funding Tracker

</td>
   <td>

[http://refugee-funding-tracker.org/](http://refugee-funding-tracker.org/)

</td>
   <td>

F

</td>
   <td>

**2**

</td>
  </tr>
</table>

# **Three-Round Ingestion Plan**

The three rounds follow a dependency graph: later rounds consume entities created by earlier rounds. Ingesting out of order produces orphan literals that degrade retrieval quality.

## **Round 1 — Reference & Master Data  (index first)**

Goal: populate the stable, shared anchors that virtually every document references. These nodes change rarely and should be treated as controlled vocabulary.

<table>
  <tr>
   <td>

**Domain**

</td>
   <td>

**Source (Code)**

</td>
   <td>

**Entity Types Extracted**

</td>
   <td>

**Notes**

</td>
  </tr>
  <tr>
   <td>

**A — Geographic**

</td>
   <td>

Operations Website (A12) Population Data (B16)

</td>
   <td>

Country (ISO-3)

Region / Settlement

OperationalZone

Border

</td>
   <td>

Foundation layer. All other entities hang off geography.

</td>
  </tr>
  <tr>
   <td>

**E — Policy / Legal**

</td>
   <td>

Strategic Directions (B02) Main Website (B16) Help.UNHCR (B16)

</td>
   <td>

LegalFramework

Policy / SOP

StandardIndicator

PledgeCommitment

</td>
   <td>

Conventions, protocols, ExCom conclusions. Cite-targets for most docs.

</td>
  </tr>
  <tr>
   <td>

**G — Stakeholders**

</td>
   <td>

Main Website (B16) Operations Website (A12)

</td>
   <td>

Organisation subtypes

UNAgency / NGOPartner

GovernmentAuthority

Donor

</td>
   <td>

Stable master list. Required before D and F can link implementing/funding orgs.

</td>
  </tr>
  <tr>
   <td>

**C — Population (aggregate only)**

</td>
   <td>

Population Data (B16) Figures at a Glance (B16)

</td>
   <td>

PopulationGroup (top-level)

groupType vocab

RegistrationCohort skeleton

</td>
   <td>

Aggregate statistics only at this stage. Individual household profiles come in Round 2.

</td>
  </tr>
</table>

## **Round 2 — Operational Context  (index second)**

Goal: add the situational and programmatic backbone. These documents are only fully resolvable once geography, legal frameworks, and organisations exist in the graph.

<table>
  <tr>
   <td>

**Domain**

</td>
   <td>

**Source (Code)**

</td>
   <td>

**Entity Types Extracted**

</td>
   <td>

**Notes**

</td>
  </tr>
  <tr>
   <td>

**B — Situation & Context**

</td>
   <td>

Operations Website (A12) Arabic/FR/ES sites (B16)

</td>
   <td>

Situation

DisplacementEvent

ConflictEvent / HazardEvent

AccessConstraint

</td>
   <td>

The 'why' layer. Links population movements to causal events.

</td>
  </tr>
  <tr>
   <td>

**C — Population (detailed)**

</td>
   <td>

Microdata Library (A01) Arabic/FR/ES sites (B16)

</td>
   <td>

HouseholdProfile

VulnerabilityProfile

CommunityStructure

RegistrationCohort (full)

</td>
   <td>

Micro-level data from survey datasets. A01 provides DDI-structured metadata for clean extraction.

</td>
  </tr>
  <tr>
   <td>

**D — Operational & Programmatic**

</td>
   <td>

Operations Website (A12) IATI Overview (B16)

</td>
   <td>

Operation / Programme / Project

Activity / IATIActivity

ImplementingPartner

ServicePoint

</td>
   <td>

The 'what is done' layer. IATI data gives machine-readable activity XML; ops site gives narrative context.

</td>
  </tr>
  <tr>
   <td>

**F — Finance (overview)**

</td>
   <td>

IATI Overview (B16) Funding Tracker (B17)

</td>
   <td>

FundingAppeal

Budget (aggregate)

IATITransaction (summary)

FundingInstrument

</td>
   <td>

High-level financial flows. Transaction-level detail comes in Round 3 via contract/tender data.

</td>
  </tr>
</table>

## **Round 3 — Evidence & Transactional Data  (index last)**

Goal: close the knowledge loop. These sources depend on the full graph being populated — they point back at programmes, activities, donors, and geographic contexts established in Rounds 1–2.

<table>
  <tr>
   <td>

**Domain**

</td>
   <td>

**Source (Code)**

</td>
   <td>

**Entity Types Extracted**

</td>
   <td>

**Notes**

</td>
  </tr>
  <tr>
   <td>

**H — Knowledge & Evidence**

</td>
   <td>

Evaluations Library (A07) Microdata Library (A01)

</td>
   <td>

Evaluation / EvidenceFinding

LessonsLearned

EffectivenessMetric

Indicator (measured)

</td>
   <td>

Consume all prior domains. An evaluation points at Programme, Situation, PopulationGroup, LegalFramework — all must pre-exist.

</td>
  </tr>
  <tr>
   <td>

**F — Finance (transactional)**

</td>
   <td>

Contract Awards (A06) Tender Notices (A10)

</td>
   <td>

Expenditure / IATITransaction (line)

FundingInstrument (detail)

Participation (role-coded)

ImplementingPartner links

</td>
   <td>

Line-level procurement and contract data. Requires ImplementingPartner and Project nodes from Round 2.

</td>
  </tr>
</table>

# **Source-Specific Extraction Notes**

## **A01 — UNHCR Microdata Library**

Structure: DDI-compliant metadata (XML) + tabular microdata. Each dataset has a catalog entry with: country, year, survey type, variables list, and producing organisation.

* Extract metadata via the catalog API: https://microdata.unhcr.org/index.php/api/catalog/search

* Map survey type to :Assessment subclass; variables to :Indicator codes; country to :Country (iso3).

* Household-level records → :HouseholdProfile nodes, linked via :hostedBy to :Settlement.

* Collection tags (PRM, SENS, VUL, FDS) → bind to :InterventionType or :programmeType values.

## **A06 / A10 — UNGM Contract Awards & Tender Notices**

Structure: HTML tables with fields for award date, supplier, value, description, and UNCCS commodity code.

* Contract award → :Expenditure (or :IATITransaction if IATI-coded) linked :spentOn → :Activity.

* Supplier → :ImplementingPartner or :Organisation; link :implementedBy from :Project.

* Tender notice → :FundingInstrument intent; update to :Expenditure on award confirmation.

## **A07 — UNHCR Evaluations Library**

Structure: PDF reports with standard sections (background, methodology, findings, recommendations). Each report has metadata: operation, year, type (joint/thematic/country).

* Top-level document → :Evaluation node; :evaluates → :Programme or :Operation.

* Each finding section → :EvidenceFinding; :produces from :Evaluation.

* Recommendations → :LessonsLearned; :generatedFrom → :EvidenceFinding.

* Use chunk-level embeddings; anchor each chunk to its :EvidenceFinding node for retrieval.

## **A12 — Operations Website**

Structure: per-operation pages with situation overview, population figures, key programmes, and partners. Primary source for D and B domain seeding.

* Operation page → :Operation node (operationCode from URL slug).

* Situation narrative → :Situation; :respondsTo link from :Operation.

* Partner list → :Organisation nodes; :coordinatesWith links.

## **B02 — Strategic Directions 2022–2026**

Structure: intranet PDF. Single authoritative policy document. Index once, treat as immutable until next cycle.

* Document → :Policy node; :policyCode = 'SD2022-2026'.

* Each strategic goal → :StandardIndicator with :measuredAgainst links to result framework indicators.

* Commitments → :PledgeCommitment nodes; :committedTo → relevant :Operation type.

## **B16 — IATI Overview (reporting.unhcr.org/iati)**

Structure: machine-readable IATI XML feed. Most structured source available — parse directly without NLP.

* Each <iati-activity> → :IATIActivity; :hasIATIIdentifier from iati-identifier element.

* <participating-org> elements → :Participation N-ary nodes with participationRoleCode.

* <transaction> elements → :IATITransaction; link :transactionProviderOrg to existing :Donor nodes.

* Map <sector> codes (DAC vocabulary) to :Sector nodes; :hasSector from activity.

* :representsOperation link: match activity title/description against known :Operation nodes (fuzzy string match + iso3 country code).

## **B17 — Refugee Funding Tracker**

Structure: Power BI dashboard (inter-agency financial tracking). Data accessible via embedded API or CSV export.

* Response plan → :FundingAppeal; :requestedIn from :Budget nodes.

* Funding contribution rows → :FundingInstrument; :funds link to :Project or :Operation.

* Donor column → resolve against :Donor master list from Round 1 (G domain).

# **Graph Quality Rules**

Apply these checks at each ingestion step to prevent graph degradation.

<table>
  <tr>
   <td>

**Check**

</td>
   <td>

**Rule**

</td>
   <td>

**Remediation**

</td>
  </tr>
  <tr>
   <td>

**Orphan prevention**

</td>
   <td>

Before creating a new entity node, query the graph for existing matches (iso3, IATI id, operation code).

</td>
   <td>

If match found, link to existing node. Only mint a new IRI if no match exists.

</td>
  </tr>
  <tr>
   <td>

**Provenance tagging**

</td>
   <td>

Every triple must carry a :createdAt timestamp and a source URI in named graph metadata.

</td>
   <td>

Reject triples lacking provenance. Quarantine to a review graph.

</td>
  </tr>
  <tr>
   <td>

**Round gate**

</td>
   <td>

Round N sources may not reference entity types that are exclusively seeded by Round N+1.

</td>
   <td>

Validate against ontology dependency matrix before loading each batch.

</td>
  </tr>
  <tr>
   <td>

**Language deduplication**

</td>
   <td>

Arabic / French / Spanish / Russian sites carry duplicate content. Deduplicate by canonical URL + publication date.

</td>
   <td>

Retain one canonical node; add skos:altLabel for each language variant.

</td>
  </tr>
  <tr>
   <td>

**IATI reconciliation**

</td>
   <td>

IATIActivity :representsOperation must resolve to an existing :Operation node.

</td>
   <td>

Unresolved activities go to a reconciliation queue; reviewed weekly.

</td>
  </tr>
  <tr>
   <td>

**Evaluation linkage**

</td>
   <td>

Every :Evaluation must link to at least one :Programme or :Operation before indexing.

</td>
   <td>

Block indexing until mandatory link is supplied by metadata enrichment step.

</td>
  </tr>
</table>




practical considerations when translating an OWL ontology into a Neo4j property graph:

    Node labels → become Neo4j labels (e.g., :Country, :PopulationGroup). Multiple inheritance (e.g., :Policy is also a :DocumentaryArtifact) can be represented by applying both labels.

    Object properties → become relationship types (e.g., :FUNDS, :LOCATED_IN). Transitive and symmetric properties are implemented in application logic or via graph algorithms, not as built‑in Neo4j features. For transitive properties, you can still query using * in Cypher.

    Datatype properties → become node properties (e.g., iso3, populationFigure). The ontology’s property domains and ranges guide where they are attached.

    Subclass hierarchies → can be exploited in queries by using multiple labels or by storing the class hierarchy in a separate taxonomy node (optional). For simplicity, applying the most specific label plus all ancestor labels works well.

    Inverse properties → you only need to store one direction; Neo4j can traverse relationships in reverse. The ontology’s owl:inverseOf is documented but does not need to be enforced at the database level.

    N‑ary relations (like :Participation) are handled as intermediate nodes with relationships, exactly as the ontology models them.