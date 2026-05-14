<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan:

**Implementation Plan**: `/specs/001-metamorph/plan.md`

**Key Documents**:
- **Feature Specification**: `/specs/001-metamorph/spec.md`
- **Research Findings**: `/specs/001-metamorph/research.md`
- **Data Model**: `/specs/001-metamorph/data-model.md`
- **API Contracts**: `/specs/001-metamorph/contracts/api-contracts.md`
- **Quickstart Guide**: `/specs/001-metamorph/quickstart.md`

**Technical Stack**:
- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: React with TypeScript
- **Database**: Neo4j (Labeled Property Graph)
- **Document Parsing**: Docling, MinerU
- **Website Crawling**: Python with requests, BeautifulSoup, Playwright
- **Testing**: pytest (backend), Jest (frontend)
- **CI/CD**: GitHub Actions
- **Deployment**: Docker + Kubernetes
- **Monitoring**: Prometheus + Grafana + OpenTelemetry

**Key Features**:
- Website crawling and file discovery
- Automatic ingestion pipeline
- Knowledge graph with provenance tracking
- Six knowledge card types (KC-1 to KC-6)
- Three-surface curation model
- Validation card workflows
- Discussion threads with consensus model
- WCAG 2.1 AA compliant interfaces

**Project Structure**:
```text
backend/
├── app/
│   ├── api/v1/endpoints/
│   ├── core/
│   ├── database.py
│   ├── main.py
│   └── models/
├── tests/
└── requirements.txt

frontend/
├── public/
├── src/
│   ├── components/
│   ├── pages/
│   ├── services/
│   ├── App.tsx
│   └── main.tsx
└── tests/

specs/001-metamorph/
├── plan.md              # Implementation plan
├── research.md          # Research findings
├── data-model.md        # Comprehensive data model
├── contracts/           # API contracts
│   └── api-contracts.md  # Complete API specification
└── quickstart.md        # Setup and usage guide
```

**Current Phase**: Implementation planning complete. Ready for task generation.
<!-- SPECKIT END -->
=======
