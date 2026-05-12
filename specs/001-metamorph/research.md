# Metamorph Research Notes

**Spec ID:** 001-metamorph  
**Version:** 1.0  
**Status:** Draft  
**Date:** 2026-04-12

---

## Overview

This document captures research findings, technical decisions, and reference materials for the Metamorph project. It serves as a knowledge base for implementation decisions and a reference for future development.

---

## 📚 Technology Research

### Document Parsing Libraries

#### Docling
- **Website:** https://github.com/DS4SD/Docling
- **License:** Apache 2.0
- **Capabilities:**
  - Supports PDF, Word, HTML, plain text
  - Advanced layout analysis
  - Table extraction
  - Figure extraction
  - Mathematical formula extraction
- **Pros:**
  - Open source
  - Actively maintained
  - High accuracy for standard documents
  - Good support for scientific papers
- **Cons:**
  - May require tuning for complex humanitarian documents
  - Limited support for some proprietary formats
- **Decision:** ✅ Selected for standard document parsing

#### MinerU
- **Website:** https://github.com/wirelesscosmos/mineru
- **License:** MIT
- **Capabilities:**
  - Specialized for complex document layouts
  - Handles tables, forms, multi-column layouts
  - Rule-based extraction
  - Custom template support
- **Pros:**
  - Excellent for structured forms and reports
  - Highly configurable
  - Good for UN/NGO documents with specific formats
- **Cons:**
  - Less mature than Docling
  - Requires more configuration
- **Decision:** ✅ Selected for complex document layouts

#### Combined Approach
- Use Docling as primary parser for standard documents
- Use MinerU for complex layouts and forms
- Implement fallback mechanism: Docling → MinerU → Manual
- Create unified interface to abstract parser differences

---

### Graph Databases

#### Neo4j
- **Website:** https://neo4j.com
- **License:** GPL (Community), Commercial (Enterprise)
- **Type:** Native Graph Database
- **Query Language:** Cypher
- **Pros:**
  - Mature and production-ready
  - Excellent Cypher query language
  - Good performance for complex traversals
  - Strong community and ecosystem
  - Full-text search integration
  - ACID compliant
- **Cons:**
  - Resource intensive
  - Learning curve for Cypher
  - Enterprise features require license
- **Decision:** ✅ Primary choice for graph storage

#### Amazon Neptune
- **Website:** https://aws.amazon.com/neptune
- **License:** AWS Service
- **Type:** Managed Graph Database
- **Pros:**
  - Fully managed
  - Scalable
  - Supports multiple graph models (Property Graph, RDF)
  - Integrates with AWS ecosystem
- **Cons:**
  - Vendor lock-in
  - Cost at scale
  - Less flexible for customization
- **Decision:** ⚠️ Backup option if cloud deployment needed

#### JanusGraph
- **Website:** https://janusgraph.org
- **License:** Apache 2.0
- **Type:** Scalable Graph Database
- **Pros:**
  - Open source
  - Scalable
  - Supports multiple storage backends
  - TinkerPop3 stack
- **Cons:**
  - Less mature than Neo4j
  - Smaller community
  - More complex setup
- **Decision:** ❌ Not selected - Neo4j preferred for simplicity

#### ArangoDB
- **Website:** https://www.arangodb.com
- **License:** Apache 2.0
- **Type:** Multi-model Database
- **Pros:**
  - Supports documents, graphs, and key-value
  - Single query language (AQL)
  - Good performance
- **Cons:**
  - Multi-model adds complexity
  - Less graph-specific optimization
- **Decision:** ❌ Not selected - Pure graph database preferred

---

### API Frameworks

#### FastAPI
- **Website:** https://fastapi.tiangolo.com
- **License:** MIT
- **Pros:**
  - Modern, fast (high-performance)
  - Easy to use
  - Type hints and automatic validation
  - Automatic OpenAPI/Swagger documentation
  - Async support
- **Cons:**
  - Relatively new (but stable)
  - Smaller ecosystem than Django/Flask
- **Decision:** ✅ Selected for API layer

#### GraphQL (Strawberry/Ariadne)
- **Website:** https://graphql.org
- **License:** Various
- **Pros:**
  - Flexible querying
  - Single endpoint for all requests
  - Strong typing
  - Good for complex data relationships
- **Cons:**
  - More complex to implement
  - Performance considerations for complex queries
  - Caching challenges
- **Decision:** ⚠️ Optional - Can be added later if needed

#### Django REST Framework
- **Website:** https://www.django-rest-framework.org
- **License:** BSD
- **Pros:**
  - Mature and stable
  - Batteries included
  - Strong ecosystem
  - Good admin interface
- **Cons:**
  - Heavier than FastAPI
  - Less async support
  - More boilerplate
- **Decision:** ❌ Not selected - FastAPI preferred for performance

---

### Agentic Systems

#### Mistral Vibe CLI
- **Website:** https://mistral.ai
- **Capabilities:**
  - Multi-model support
  - Local execution
  - Tool integration
  - Custom workflows
- **Decision:** ✅ Primary agentic system

#### Claude Code
- **Website:** https://claude.ai
- **Capabilities:**
  - Code generation
  - Code review
  - Natural language understanding
- **Decision:** ✅ Supported for multi-model approach

#### LlamaIndex / LangChain
- **Website:** https://llamaindex.ai, https://python.langchain.com
- **Capabilities:**
  - Document indexing
  - Query engines
  - Agent orchestration
- **Decision:** ⚠️ Consider for complex workflows

---

## 🏗️ Architecture Decisions

### Decision 1: Microservices vs Monolith
**Decision:** Start with Modular Monolith, evolve to Microservices

**Rationale:**
- Faster development in early phases
- Easier to understand and debug
- Can extract services as they mature
- Team size (4-5 developers) suits monolith

**Migration Path:**
1. Phase 1-2: Monolithic FastAPI application
2. Phase 3: Extract Ingestion service
3. Phase 4: Extract Graph service
4. Phase 5: Extract API Gateway

### Decision 2: Database Strategy
**Decision:** Single Neo4j database with logical separation

**Rationale:**
- Simpler to manage
- Good performance for our scale
- Logical separation via labels/properties
- Can shard later if needed

**Schema Strategy:**
- Use Neo4j labels for entity types
- Use properties for attributes
- Use relationships for connections
- Index all frequently queried properties

### Decision 3: Frontend Framework
**Decision:** React with TypeScript

**Rationale:**
- Strong ecosystem
- Good TypeScript support
- Component-based architecture
- Large talent pool
- Mature routing and state management

**Alternative Considered:**
- Vue.js: Similar benefits, slightly simpler
- Svelte: Emerging, less ecosystem
- Angular: Too heavy for our needs

---

## 📊 Knowledge Domain Research

### Geographic Domain
- **Sources:** UN OCHA, UNHCR, World Bank, CIA World Factbook
- **Key Entities:** Countries, Regions, Cities, Coordinates
- **Key Relationships:** contains, borders, adjacent_to, part_of
- **Challenges:**
  - Changing geopolitical boundaries
  - Multiple naming conventions
  - Historical vs current data

### Crisis Domain
- **Sources:** UN OCHA, ACAPS, ReliefWeb
- **Key Entities:** Crises, Conflicts, Disasters, Emergencies
- **Key Relationships:** affects, caused_by, related_to, escalated_from
- **Challenges:**
  - Rapidly changing information
  - Multiple conflicting reports
  - Sensitivity of information

### Demographics Domain
- **Sources:** UNICEF, World Bank, National Statistics
- **Key Entities:** Population, Age Groups, Gender, Ethnic Groups
- **Key Relationships:** belongs_to, affected_by, located_in
- **Challenges:**
  - Data privacy concerns
  - Sampling methodologies vary
  - Outdated information common

### Programming Domain
- **Sources:** UNHCR, WFP, UNICEF program documents
- **Key Entities:** Programs, Projects, Activities, Budgets
- **Key Relationships:** implements, funded_by, targets, operates_in
- **Challenges:**
  - Complex hierarchies
  - Budget tracking across time
  - Impact measurement

### Policy Domain
- **Sources:** UN Resolutions, National Laws, NGO Policies
- **Key Entities:** Policies, Regulations, Guidelines, Standards
- **Key Relationships:** governs, complies_with, conflicts_with, supersedes
- **Challenges:**
  - Legal language complexity
  - Jurisdictional variations
  - Version tracking

### Finance Domain
- **Sources:** UN Financial Reports, Donor Reports
- **Key Entities:** Funding, Budgets, Expenditures, Donors
- **Key Relationships:** funds, allocated_to, spent_on, reported_by
- **Challenges:**
  - Multiple currencies
  - Fiscal year variations
  - Audit requirements

### Human Resources Domain
- **Sources:** UN Staff Directories, NGO Reports
- **Key Entities:** Staff, Roles, Skills, Organizations
- **Key Relationships:** employed_by, manages, reports_to, assigned_to
- **Challenges:**
  - Staff turnover
  - Confidentiality requirements
  - Organizational restructuring

### Knowledge Assets Domain
- **Sources:** UN Libraries, Research Institutions
- **Key Entities:** Reports, Studies, Databases, Methodologies
- **Key Relationships:** cites, based_on, supports, contradicts
- **Challenges:**
  - Access restrictions
  - Quality variation
  - Citation tracking

---

## 🔬 Extraction Patterns Research

### Named Entity Recognition (NER)
- **Approach:** Use spaCy with custom models
- **Models:**
  - `en_core_web_lg` (base)
  - `en_core_web_trf` (transformer-based, higher accuracy)
- **Customization:**
  - Train on humanitarian domain text
  - Add custom entity types (8 domains)
  - Fine-tune for UN terminology

### Relationship Extraction
- **Approach:** Rule-based + ML-based hybrid
- **Rule-based:**
  - Pattern matching for common relationships
  - Dependency parsing
  - POS tag patterns
- **ML-based:**
  - Transformer models for complex relationships
  - Fine-tuned on humanitarian text

### Semantic Triplet Extraction
- **Approach:** OpenIE (Open Information Extraction)
- **Tools:**
  - Stanford OpenIE
  - AllenNLP OpenIE
  - Custom implementation
- **Challenges:**
  - Triple completeness
  - Confidence scoring
  - Redundancy elimination

### Confidence Scoring
- **Factors:**
  - Parser confidence: 0-1
  - Source reliability: 0-1 (trusted=1, unverified=0.5, untrusted=0.1)
  - Extraction method: rule-based=0.9, ML=0.7, manual=1.0
  - Corroboration: number of sources (1=1, 2=0.95, 3+=0.98)
  - Freshness: days since publication (0-30=1, 31-90=0.9, 91-180=0.7, 181+=0.5)
- **Formula:**
  ```
  confidence = (parser_confidence * 0.3 + 
                source_reliability * 0.25 + 
                extraction_method * 0.2 + 
                corroboration * 0.15 + 
                freshness * 0.1)
  ```

---

## 🎯 Trust Routing Research

### Confidence Thresholds
- **Auto-Accept:** confidence >= 0.9
- **Pending/Review:** 0.7 <= confidence < 0.9
- **Escalation:** confidence < 0.7

### Sensitivity Classification
- **Low:** Non-controversial, public information
  - Examples: Geographic coordinates, population statistics
  - Routing: Auto-accept if confidence high
- **Medium:** Potentially controversial, operational information
  - Examples: Program effectiveness, local politics
  - Routing: Require review by Tier 1
- **High:** Highly sensitive, protection concerns
  - Examples: Individual identities, security incidents, legal issues
  - Routing: Escalate to Tier 3, require HQ approval

### Source Reliability Indicators
- **Trusted:**
  - UN official documents
  - Government reports
  - Academic publications (peer-reviewed)
  - Established NGOs with track record
- **Unverified:**
  - News articles (mainstream)
  - NGO reports (lesser known)
  - Social media (verified accounts)
- **Untrusted:**
  - Social media (unverified)
  - Rumors
  - Anonymous sources

### Contradiction Detection
- **Types:**
  1. **Factual Accuracy:** Different values for same fact
  2. **Source Reliability:** Trusted vs untrusted sources disagree
  3. **Temporal Mismatch:** Information valid for different time periods
  4. **Quantitative Mismatch:** Different numbers for same metric
  5. **Classification Mismatch:** Different categories assigned
  6. **Scope Mismatch:** Different geographic/operational scope
  7. **Geographic Mismatch:** Different locations referenced
  8. **Structural Mismatch:** Different relationships/structure
  9. **Normative Disagreement:** Different interpretations/perspectives
  10. **Policy Conflict:** Contradicts established policy
  11. **Sensitive Domain:** Involves protected/sensitive information
  12. **Duplicate Entity:** Same entity appears with different IDs
  13. **Graph Relationship Conflict:** Conflicting relationships in graph

---

## 📈 Performance Benchmarks

### Parsing Performance
| Document Type | Pages | Average Size | Target Parse Time | Current Parse Time |
|---------------|-------|--------------|-------------------|--------------------|
| PDF Standard | 10 | 500KB | <5 seconds | TBD |
| PDF Complex | 50 | 5MB | <30 seconds | TBD |
| Word Document | 20 | 1MB | <10 seconds | TBD |
| HTML Page | 1 | 200KB | <3 seconds | TBD |

### Graph Query Performance
| Query Type | Complexity | Target Response Time | Current Response Time |
|------------|------------|----------------------|-----------------------|
| Simple node lookup | Low | <10ms | TBD |
| Node with relationships | Medium | <100ms | TBD |
| Path traversal (3 hops) | Medium | <500ms | TBD |
| Complex aggregation | High | <1 second | TBD |
| Full-text search | Medium | <200ms | TBD |

### System Scalability
| Metric | Target | Current |
|--------|--------|---------|
| Concurrent users | 100 | TBD |
| Documents stored | 100,000 | TBD |
| Nodes in graph | 1,000,000 | TBD |
| Relationships in graph | 10,000,000 | TBD |
| API requests/second | 100 | TBD |
| Data growth/month | 10GB | TBD |

---

## 🔒 Security Research

### Data Classification
- **Public:** Non-sensitive, can be shared openly
- **Internal:** For UN staff and partners only
- **Confidential:** Limited distribution, requires clearance
- **Secret:** Highly sensitive, strict access control

### Access Control Model
- **Role-Based Access Control (RBAC):**
  - Viewer: Read-only access to approved content
  - Curator: Read/write access to curated content, can approve/reject
  - Reviewer: Can participate in discussions, limited approval
  - Tier 1 Curator: Field/local level approval
  - Tier 2 Curator: Regional level approval
  - Tier 3 Curator: HQ/thematic level approval
  - Admin: Full system access
  - Super Admin: System configuration, user management

### Audit Requirements
- **What to log:**
  - All data access (who, what, when)
  - All data modifications (who, what, when, previous value)
  - All approval/rejection decisions (who, what, when, rationale)
  - All system configuration changes
  - All authentication events
- **Retention:** 7 years minimum
- **Immutability:** Audit logs cannot be modified or deleted
- **Access:** Audit logs accessible only to admins and auditors

### Encryption
- **At Rest:** AES-256 encryption for all sensitive data
- **In Transit:** TLS 1.3 for all communications
- **Field-Level:** Encryption for PII and sensitive fields

---

## 🌍 Humanitarian Context Research

### Key UN Organizations
- UNHCR: United Nations High Commissioner for Refugees
- OCHA: Office for the Coordination of Humanitarian Affairs
- WFP: World Food Programme
- UNICEF: United Nations Children's Fund
- UNDP: United Nations Development Programme

### Data Standards
- **IATI:** International Aid Transparency Initiative
- **HDX:** Humanitarian Data Exchange
- **UNHCR Data Portal:** Refugee data and statistics
- **OCHA Humanitarian Response Plans:** Coordination documents

### Common Document Types
1. **Situation Reports** (SitReps) - Regular updates on crises
2. **Needs Assessments** - Identification of needs and gaps
3. **Project Proposals** - Funding requests and plans
4. **Financial Reports** - Budget and expenditure tracking
5. **Evaluation Reports** - Program effectiveness analysis
6. **Protection Reports** - Sensitive information on protection concerns
7. **Market Assessments** - Economic and market analysis
8. **Coordination Meeting Minutes** - Meeting notes and action items

### Language Considerations
- **Primary:** English
- **Secondary:** French, Spanish, Arabic
- **Local:** Various local languages based on region
- **Approach:**
  - Primary extraction in English
  - Support for multilingual documents
  - Translation services integration (future)

---

## 📝 Open Questions

1. **Document Storage:**
   - Where to store original documents? (S3, local storage, document management system)
   - How to handle large documents (>100MB)?
   - What retention policy for original documents?

2. **Graph Database:**
   - Should we use Neo4j Aura (managed) or self-hosted?
   - What backup strategy for Neo4j?
   - How to handle graph schema migrations?

3. **API Design:**
   - Should we support both REST and GraphQL?
   - What authentication method? (OAuth2, JWT, API keys)
   - Should we rate limit by user or by organization?

4. **Agentic System:**
   - Which LLM providers to support initially?
   - How to handle API costs for LLM usage?
   - Should we cache LLM responses?

5. **Deployment:**
   - Cloud provider preference? (AWS, Azure, GCP, on-premise)
   - What regions to deploy in?
   - Disaster recovery strategy?

6. **Data Privacy:**
   - How to handle PII (Personally Identifiable Information)?
   - What data can be shared publicly?
   - GDPR compliance requirements?

---

## 📚 References

### Documentation
- [Docling Documentation](https://github.com/DS4SD/Docling)
- [MinerU Documentation](https://github.com/wirelesscosmos/mineru)
- [Neo4j Documentation](https://neo4j.com/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [spaCy Documentation](https://spacy.io)

### Standards
- [IATI Standard](https://iatistandard.org/)
- [HDX API](https://data.humdata.org/api)
- [UNHCR Data Standards](https://www.unhcr.org/data.html)

### Research Papers
- [Knowledge Graph Embeddings](https://arxiv.org/abs/2002.00388)
- [Information Extraction from Documents](https://arxiv.org/abs/1903.07602)
- [Contradiction Detection in Knowledge Bases](https://arxiv.org/abs/2106.00574)

---

## 🔄 Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2026-04-12 | Edouard Legoupil | Initial research document created |
