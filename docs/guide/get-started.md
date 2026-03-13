# 🚀 Get Started with Metamorph (Developer Quickstart)

Welcome! This guide walks you through getting Metamorph running locally with a full knowledge pipeline—either with Docker containers (recommended) or without Docker, for native developer workflows, full hot-reload, and custom environments.

---

## 🛠️ Prerequisites
- Computer: Linux, Mac, or Windows
- Python 3.10+
- Node.js 18+
- Git
- (Optional, but recommended): Poetry or pipenv for backend
def
- Docker Desktop (for one-command bringup, but you can run services locally instead)

---

## 🗄️ 1. Database and Services (Local or Docker)
### Option A: Use Docker Compose (quickest, see below)
### Option B: Run Everything Natively (no Docker)

If you wish to develop and run Metamorph outside containers, start each service yourself:

#### 1. PostgreSQL
- Install locally (`brew install postgresql` or your OS method)
- Create the database:
  ```bash
  createdb metamorph
  psql metamorph < scripts/init_db.sql
  ```
- Enable pgvector extension:
  ```bash
  psql -d metamorph -c "CREATE EXTENSION IF NOT EXISTS vector;"
  ```

#### 2. Neo4j
- Download from https://neo4j.com/download or use Desktop app.
- Run with:
  ```bash
  neo4j console --home-dir $NEO4J_HOME --config-dir $NEO4J_HOME/conf
  ```
- Set initial password.
- Default bolt URL is `bolt://localhost:7687`.
- To bootstrap the ontology, see below.

#### 3. Redis (for Celery and cache)
- Install with `brew install redis` or OS package manager.
- Start: `redis-server`

#### 4. MinIO (object storage, optional for dev/test)
- Download from https://min.io/download (run `minio server /tmp/minio` with test credentials)
- Or replace S3 storage config with local dirs for dev only.

---

## 📝 2. Environment Variables
- Copy `.env.example` → `.env` in repo root and backend as needed
- Set DB=postgres URIs, NEO4J, REDIS, and S3/MINIO envs to your local services (not Docker container names!).
- Example for local Postgres:
  ```env
  POSTGRES_DSN=postgresql://localhost:5432/metamorph
  ```
  See README.md for the full variable set.

---

## 🐍 3. Backend (FastAPI)
- Create a Python 3.10+ virtual environment (venv, poetry, or pipenv)
- Install dependencies:
  ```bash
  poetry install  # or pip install -r requirements.txt
  ```
- Run the API (with auto-reload):
  ```bash
  poetry run uvicorn app.main:app --reload
  # or uvicorn app.main:app --reload
  ```
- API runs by default at http://localhost:8000; docs at `/docs` endpoint.

---

## 🖥️ 4. Frontend (React/Vite/TypeScript)
- Navigate to frontend directory:
  ```bash
  cd frontend
  npm install
  npm run dev
  ```
- Frontend runs by default at http://localhost:3000
- Configure VITE_ or NEXT_PUBLIC_ variables in `.env` if applicable for proxying to your API/backend.

---

## 📊 5. Knowledge Graph Ontology and Pipeline Bootstrap
- Ontology bootstrapping (Neo4j):
  ```bash
  python scripts/bootstrap_knowledge_graph.py --ontology docs/ontology/unhcr-knowledge-ontology.ttl --neo4j-url bolt://localhost:7687
  ```
- Progressive graph build, per round:
  ```bash
  python scripts/build_graph_round.py --round 1
  python scripts/build_graph_round.py --round 2
  python scripts/build_graph_round.py --round 3
  ```
- These steps are identical in both Docker and native workflows; just ensure your `NEO4J_URI` matches your local instance.

---

## 🏃 6. Running Tests and QA
- Backend: `pytest` OR `poetry run pytest`
- Frontend: `npm test` or `npx playwright test`
- In both, use local URLs/credentials for API and database access.
- Both sides support hot reload; you can attach debuggers, run Playwright/E2E, and test increments as you build.

---

## 🧩 7. Troubleshooting
- If services fail to connect, check `.env` for local addresses, not Docker hostnames.
- Make sure each database/service is running and has been initialized.
- Logs from API (`uvicorn`), frontend, and DB/graph/redis will all show on your standard out.
- For more details, see README.md, DATABASE.md, and API.md for full config, and check the relevant issues or docs for the specific service you’re operating outside of Docker.

---

## 🗄️ Alternative: Docker Compose Full Bring-Up
Running everything in Docker remains the fastest onboarding. If you wish to return to it, just:
```bash
docker compose up --build
```
This will start all services, with all network/config/database persistence handled by Docker. See original documentation above for details!

---

## 🎉 Congratulations!
You can now develop, run, test, and QA Metamorph locally—inside Docker containers or outside, with all the benefits of local dev, hot reload, IDE integration, isolated services, and rapid TDD.

For next steps, service-specific docs, or detailed configuration, see README.md and other docs in docs/guide.