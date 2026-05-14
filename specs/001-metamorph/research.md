# Research: Metamorph Website-to-Knowledge System

**Date**: 2026-05-12 | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

This document resolves all "NEEDS CLARIFICATION" items from the Technical Context and provides research-based decisions for the Metamorph implementation.

---

## 1. Testing Framework

**Decision**: pytest for backend, Jest/React Testing Library for frontend

**Rationale**:
- **Backend (Python/FastAPI)**: pytest is the de facto standard for Python testing, with excellent FastAPI integration and rich plugin ecosystem
- **Frontend (React/TypeScript)**: Jest provides comprehensive testing (unit, integration, snapshot) while React Testing Library enables user-centric component testing
- **Consistency**: Both frameworks support modern testing practices (mocking, fixtures, async/await)
- **Ecosystem**: Strong community support, documentation, and integration with CI/CD pipelines

**Alternatives Considered**:
- Backend: unittest (built-in but less feature-rich), hypothesis (property-based testing)
- Frontend: Cypress (E2E focused), Vitest (faster but newer ecosystem)

**Implementation Plan**:
- Backend: pytest with pytest-asyncio, pytest-cov, pytest-mock
- Frontend: Jest with @testing-library/react, @testing-library/jest-dom, jest-fetch-mock
- CI Integration: Test coverage reporting and quality gates

---

## 2. CI/CD Pipeline Requirements

**Decision**: GitHub Actions with multi-stage workflow

**Rationale**:
- **Integration**: Native GitHub integration with repository events
- **Flexibility**: Supports matrix builds, caching, and complex workflows
- **Cost**: Free for public repositories, generous free tier for private
- **Ecosystem**: Rich marketplace of actions for common tasks

**Pipeline Stages**:
1. **Lint & Format**: ESLint, Prettier, Black, isort
2. **Unit Tests**: Backend and frontend unit tests in parallel
3. **Integration Tests**: API contract tests, frontend integration tests
4. **Build**: Docker image build for backend, frontend build optimization
5. **E2E Tests**: Playwright for end-to-end testing
6. **Security Scan**: Snyk or Dependabot for vulnerability detection
7. **Deploy**: Environment-specific deployment (dev/staging/prod)

**Alternatives Considered**:
- GitLab CI/CD (if using GitLab)
- CircleCI, Jenkins (more complex setup)
- Azure Pipelines (if in Microsoft ecosystem)

---

## 3. Monitoring/Observability Stack

**Decision**: Prometheus + Grafana + OpenTelemetry

**Rationale**:
- **Standards-based**: OpenTelemetry provides vendor-neutral instrumentation
- **Comprehensive**: Metrics, logs, and traces in one ecosystem
- **Scalable**: Prometheus handles time-series data efficiently
- **Visualization**: Grafana dashboards for operational insights
- **Alerting**: Prometheus Alertmanager for incident notification

**Components**:
- **Metrics**: Prometheus with FastAPI instrumentation
- **Logging**: ELK stack (Elasticsearch, Logstash, Kibana) or Loki
- **Tracing**: Jaeger or Zipkin for distributed tracing
- **Frontend**: Sentry for error tracking and performance monitoring

**Key Metrics to Track**:
- Website crawling: pages/sec, files discovered, crawl duration
- File ingestion: files processed, parse success rate, ingestion latency
- API: response times, error rates, request volume
- System: CPU, memory, disk I/O, Neo4j query performance

**Alternatives Considered**:
- Datadog, New Relic (commercial solutions)
- AWS CloudWatch (if on AWS)
- Custom solution (too maintenance-heavy)

---

## 4. Deployment Strategy

**Decision**: Docker containers with Kubernetes orchestration

**Rationale**:
- **Portability**: Containerization ensures consistent environments
- **Scalability**: Kubernetes provides auto-scaling for website crawling workloads
- **Resilience**: Self-healing capabilities for failed pods
- **Management**: Rolling updates, canary deployments, blue-green deployments
- **Ecosystem**: Rich tooling for monitoring, logging, and networking

**Architecture**:
```text
Backend: FastAPI in Docker container
Frontend: React static files served via Nginx
Database: Neo4j in dedicated container or managed service
Ingress: Nginx or Traefik for routing
Storage: Persistent volumes for Neo4j data
```

**Deployment Environments**:
- **Development**: Local Docker Compose for individual development
- **Staging**: Kubernetes cluster for integration testing
- **Production**: Managed Kubernetes service (EKS, GKE, AKS) with auto-scaling

**Alternatives Considered**:
- Serverless (AWS Lambda, Azure Functions) - not suitable for long-running crawling
- Bare metal/VMs - harder to scale horizontally
- Heroku - limited scaling options for enterprise needs

---

## 5. Database Backup and Recovery Strategy

**Decision**: Automated daily backups with point-in-time recovery

**Rationale**:
- **Data Criticality**: Knowledge graph contains irreplaceable curated knowledge
- **Compliance**: Meets organizational requirements for data preservation
- **Recovery**: Enables restoration from accidental deletion or corruption

**Implementation**:

**Neo4j Backup Strategy**:
- **Daily Full Backups**: Complete database dump using `neo4j-admin dump`
- **Incremental Backups**: Transaction log backups every 6 hours
- **Retention**: 30 days of daily backups, 12 months of monthly backups
- **Storage**: Cloud storage (S3, GCS, Azure Blob) with versioning
- **Encryption**: AES-256 encryption for backups at rest

**Recovery Procedures**:
- **Point-in-Time Recovery**: Restore to specific transaction using transaction logs
- **Disaster Recovery**: Cross-region backup replication
- **Testing**: Quarterly backup restoration tests

**Monitoring**:
- Backup success/failure alerts
- Backup size growth monitoring
- Recovery time objective (RTO) tracking

**Alternatives Considered**:
- Continuous replication only (no point-in-time recovery)
- Manual backup process (error-prone)
- No backup strategy (unacceptable for production)

---

## 6. Additional Research: Website Crawling Best Practices

**Decision**: Respectful crawling with adaptive rate limiting

**Rationale**:
- **Ethical**: Respect website owners' resources and policies
- **Legal**: Comply with robots.txt and terms of service
- **Practical**: Avoid IP blocking and rate limiting

**Implementation**:
- **Robots.txt**: Parse and respect crawl-delay, disallow directives
- **Rate Limiting**: Adaptive based on server response times
- **User-Agent**: Identify as Metamorph with contact information
- **Concurrency**: Limit parallel requests per domain
- **Retry Logic**: Exponential backoff for failed requests
- **Session Management**: Handle cookies and authentication properly

**Standards Compliance**:
- Follow REP (Robots Exclusion Protocol)
- Implement sitemap.xml parsing
- Support canonical URLs to avoid duplicates

---

## 7. Document Parsing Research

**Decision**: Dual-engine approach with fallback logic

**Rationale**:
- **Coverage**: Handle both standard and complex document layouts
- **Reliability**: Fallback when primary parser fails
- **Quality**: Different engines may extract different quality metadata

**Implementation Strategy**:
```text
Input Document
       ↓
Docling (Primary Parser)
       ↓
Success? → Store in graph
       ↓  No
MinerU (Complex Layout Parser)
       ↓
Success? → Store in graph
       ↓  No
Manual Review Queue
```

**Parser Selection Logic**:
- Use Docling for standard PDFs, Word docs, simple layouts
- Use MinerU for complex layouts, scanned documents, unusual formats
- Track parser success rates for continuous improvement

---

## 8. Knowledge Graph Schema Design

**Decision**: Labeled Property Graph with semantic triplets

**Rationale**:
- **Flexibility**: Schema can evolve without migration pain
- **Performance**: Graph queries for relationship traversal
- **Semantics**: Natural representation of knowledge relationships

**Core Schema Elements**:

**Nodes**:
- `Website` (url, domain, title, description, robots_txt)
- `DiscoveredFile` (url, file_type, file_name, size, last_modified)
- `Document` (original_url, parse_date, extracted_text, metadata)
- `Entity` (type, name, description) - people, organizations, locations
- `Event` (type, date, description)
- `KnowledgeCard` (card_type, validity_period, status)
- `WikiBlock` (content, verification_state, provenance)

**Relationships**:
- `DISCOVERED_FROM` (DiscoveredFile → Website)
- `INGESTED_FROM` (Document → DiscoveredFile)
- `PARSED_USING` (Document → ParserType)
- `CONTAINS_ENTITY` (Document → Entity)
- `MENTIONS_EVENT` (Document/Entity → Event)
- `HAS_CARD` (Entity/Event → KnowledgeCard)
- `HAS_BLOCK` (KnowledgeCard → WikiBlock)
- `TRACEABLE_TO` (WikiBlock → Document/DiscoveredFile/Website)

**Properties**:
- Provenance: source_website, source_file, source_url, extraction_date
- Temporal: created_at, updated_at, valid_from, valid_until
- State: status, verification_state, confidence_score

---

## 9. Error Handling and Recovery Patterns

**Decision**: Comprehensive error handling with retry and escalation

**Rationale**:
- **Resilience**: Website crawling is prone to network issues
- **User Experience**: Clear error communication and recovery options
- **Operational**: Reduce manual intervention requirements

**Error Categories and Handling**:

**Crawling Errors**:
- **Network Timeout**: Retry with exponential backoff (max 3 attempts)
- **HTTP 429 (Too Many Requests)**: Respect Retry-After header
- **HTTP 403 (Forbidden)**: Log and skip (may indicate robots.txt violation)
- **Invalid URL**: Validate URLs before crawling, skip malformed ones
- **SSL Certificate**: Use certificate verification, allow override for internal sites

**Parsing Errors**:
- **Unsupported Format**: Log file type, skip with notification
- **Corrupt File**: Validate checksums, retry download once
- **Parser Failure**: Fallback to alternative parser, then manual review
- **Memory Limits**: Stream large files, implement size limits

**Ingestion Errors**:
- **Database Connection**: Retry with backoff, alert on persistent failures
- **Constraint Violation**: Validate data before insertion, provide clear error
- **Duplicate Detection**: Use content hashing to avoid duplicates
- **Timeout**: Implement transaction timeouts, rollback on failure

**User Error Handling**:
- **Dedicated Error Panel**: Show all errors with timestamps and context
- **Retry Options**: Allow users to retry failed operations
- **Error Export**: Enable download of error logs for support
- **Notifications**: Email alerts for critical failures

---

## 10. Security Considerations

**Decision**: Defense-in-depth security approach

**Rationale**:
- **Data Sensitivity**: Knowledge may include sensitive humanitarian information
- **Compliance**: UN data policies and GDPR requirements
- **Trust**: System must be trusted by curators and proposal writers

**Security Measures**:

**Authentication & Authorization**:
- JWT-based authentication with short expiration
- Role-based access control (RBAC)
- OAuth2/OIDC integration for enterprise SSO
- Password policies and multi-factor authentication

**Data Protection**:
- Encryption at rest (AES-256) for sensitive data
- Encryption in transit (TLS 1.2+)
- Data masking for PII in logs and UIs
- Secure disposal of temporary files

**API Security**:
- Input validation and sanitization
- Rate limiting and request throttling
- CORS configuration with strict origins
- CSRF protection for state-changing operations

**Infrastructure Security**:
- Regular vulnerability scanning
- Container image signing
- Network segmentation
- Security patch management

**Compliance**:
- Audit logging for all sensitive operations
- Data retention policies
- Right to erasure implementation
- Security training for developers

---

## Summary of Research Findings

| Area | Decision | Status |
|------|----------|--------|
| Testing Framework | pytest (backend), Jest (frontend) | ✅ Resolved |
| CI/CD Pipeline | GitHub Actions | ✅ Resolved |
| Monitoring | Prometheus + Grafana + OpenTelemetry | ✅ Resolved |
| Deployment | Docker + Kubernetes | ✅ Resolved |
| Backup Strategy | Daily full + incremental backups | ✅ Resolved |
| Crawling Approach | Respectful with adaptive rate limiting | ✅ Resolved |
| Parsing Strategy | Dual-engine with fallback | ✅ Resolved |
| Graph Schema | Labeled Property Graph | ✅ Resolved |
| Error Handling | Comprehensive with retry logic | ✅ Resolved |
| Security | Defense-in-depth approach | ✅ Resolved |

**All NEEDS CLARIFICATION items have been resolved.** The implementation can proceed to Phase 1 (Design & Contracts) with confidence.

---

## Next Steps

1. **Phase 1: Design & Contracts** - Generate data-model.md, contracts/, and quickstart.md
2. **Update Agent Context** - Modify AGENTS.md to reference this plan
3. **Re-evaluate Constitution Check** - Ensure all principles still satisfied post-design
4. **Proceed to Task Generation** - Run `/speckit.tasks` to create tasks.md

**Suggested Command:**
```bash
/speckit.tasks
```