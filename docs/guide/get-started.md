# 🚀 Get Started with Metamorph (Developer Quickstart)

Welcome! This guide walks you through getting Metamorph running locally with a full knowledge pipeline: database and knowledge graph bootstrapping, ingestion, and curation tools.

---

## 🛠️ Prerequisites
- Computer: Linux, Mac, or Windows
- Docker Desktop (recommended)
- Python 3.10+
- Node.js 18+
- Git
- (Optional) Poetry or pipenv

---

## 🗄️ 1. Database Initialization
### PostgreSQL
- Start local database with Docker Compose:
  ```bash
  docker compose up --build
  ```
- Then initialize all schemas:
  ```bash
  psql metamorph < scripts/init_db.sql
  ```
  (This will create all tables/indexes needed. See [DATABASE_BLUEPRINT.md](docs/guide/DATABASE_BLUEPRINT.md) for details.)

### MinIO, Redis, Neo4j
- All supporting services are started with Docker Compose as well.
- Neo4j default: [`bolt://localhost:7687`] (login: neo4j / password)

---

## 🌐 2. Knowledge Graph & Ontology Bootstrap
### Ontology Init
- Populate the main ontology into your graph database:
  ```bash
  python scripts/bootstrap_knowledge_graph.py --ontology docs/ontology/unhcr-knowledge-ontology.ttl --neo4j-url bolt://localhost:7687
  ```
  This script will create class nodes, property/relationship types, and controlled vocabularies in Neo4j based on the UNHCR ontology.

### Progressive Graph Building
- Apply progressive rounds as described in [docs/ontology/README.md](docs/ontology/README.md):
  - **Round 1** — Masterdata: country, region, org, population anchors
  - **Round 2** — Operational context: situations, partners, activities
  - **Round 3** — Evidence, transactions, claims
- For each round, run:
  ```bash
  python scripts/build_graph_round.py --round 1
  python scripts/build_graph_round.py --round 2
  python scripts/build_graph_round.py --round 3
  ```
  _Each script inserts only entities/relations relevant to its round; rounds must be run in order for the graph to resolve correctly._

---

## 📝 3. Environment Variables
- Copy `.env.example` → `.env` in both root and backend.
- Set credentials and URIs for Postgres, MinIO, and Neo4j.

---

## 🐳 4. Start All Services
  ```bash
  docker compose up --build
  ```
- Backend docs: http://localhost:8000/docs
- Frontend UI: http://localhost:3000/

---

## 🛠 5. Developer Tools
- Backend (optional): poetry or pipenv then `uvicorn app.main:app --reload`
- Frontend: `npm install` then `npm run dev`

---

## 🏗️ 6. Knowledge Pipeline QA
- Init DB:
  ```bash
  psql metamorph < scripts/init_db.sql
  ```
- Bootstrap ontology:
  ```bash
  python scripts/bootstrap_knowledge_graph.py --ontology docs/ontology/unhcr-knowledge-ontology.ttl
  ```
- Progressive build:
  ```bash
  python scripts/build_graph_round.py --round 1
  python scripts/build_graph_round.py --round 2
  python scripts/build_graph_round.py --round 3
  ```
- After each phase, use the Metamorph UI/dashboards to inspect, curate, and audit knowledge.

---

## 🧹 7. Troubleshooting & Support
- DB errors: Check container logs, rerun `init_db.sql` as needed.
- Graph/Neo4j/ontology errors: Ensure Python dependencies are installed, Neo4j is running, and credentials are correct.
- See [docs/ontology/README.md](docs/ontology/README.md) and [docs/guide/DATABASE_BLUEPRINT.md](docs/guide/DATABASE_BLUEPRINT.md) for more.

---

## 🎉 Done
You now have a bootstrapped, progressive, reproducible Metamorph deployment—everything from schema to knowledge graph to agentic curation tools is ready!

---

## 📖 Script Reference
- `scripts/init_db.sql` — Postgres schema
- `scripts/bootstrap_knowledge_graph.py` — Creates class/relationship/vocab structure from ontology
- `scripts/build_graph_round.py` — Progressive entity/relation builder per ontology rounds
- `docs/ontology/README.md` — Build details, data source mapping, graph best practices
- `docs/guide/DATABASE_BLUEPRINT.md` — All schema details
