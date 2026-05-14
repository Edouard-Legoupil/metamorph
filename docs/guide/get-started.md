# 🚀 Get Started with Metamorph (Developer Quickstart)

Welcome! This guide walks you through getting Metamorph running locally with a full knowledge pipeline—either with Docker containers (recommended) or without Docker, for native developer workflows, full hot-reload, and custom environments.

---

## 🛠️ Prerequisites
- Computer: Linux, Mac, or Windows
- Python 3.10+
- Node.js 18+
- Git
- Docker Desktop (recommended for easiest setup)
- (Optional): Poetry or pipenv for backend dependency management

---

## 🗄️ Quick Start with Docker (Recommended)

### 1. Clone the Repository
```bash
git clone https://github.com/edouard-legoupil/metamorph.git
cd metamorph
```

### 2. Start Services with Docker
```bash
# Start Neo4j and MinIO containers
docker run -d -p 7687:7687 -p 7474:7474 -e NEO4J_AUTH=neo4j/password --name neo4j neo4j:5
docker run -d -p 9000:9000 -p 9001:9001 -e MINIO_ROOT_USER=minioadmin -e MINIO_ROOT_PASSWORD=minioadmin --name minio minio/minio server /data --console-address ":9001"
```

### 3. Create MinIO Bucket
```bash
# Install MinIO client and create bucket
docker exec minio mc alias set local http://localhost:9000 minioadmin minioadmin
docker exec minio mc mb local/metamorph-documents
```

### 4. Install Backend Dependencies
```bash
cd backend
uv venv --python 3.13
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 5. Start Backend Server
```bash
# From backend directory
uvicorn app.main:app --reload
```

### 6. Install Frontend Dependencies
```bash
cd frontend
npm install
npx playwright install  # Install browsers for testing
```

### 7. Build Frontend
```bash
npm run build
```

### 8. Start Frontend Development Server
```bash
npm run dev
```

### 9. Access the Application
- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:5173
- **Neo4j Browser**: http://localhost:7474 (user: neo4j, password: password)
- **MinIO Console**: http://localhost:9001 (user: minioadmin, password: minioadmin)

---

## 🧪 Running Tests

### Backend Tests
```bash
cd backend
source .venv/bin/activate
python -m pytest tests/unit/ -v --tb=short
```

**Expected Results:**
- ✅ 35 tests passing (100% success)
- ⚠️ Deprecation warnings (non-critical)
- Tests cover: API endpoints, extraction, reconciliation, graph operations, ingestion, integration, edge cases

### Frontend Tests
```bash
cd frontend
npm test
```

**Note:** Playwright tests require browsers installed via `npx playwright install`

---

## 🔧 Development Workflow

### Backend Development
```bash
cd backend
source .venv/bin/activate
# Run with hot reload
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm run dev  # Hot reload at http://localhost:5173
```

### Common Commands
```bash
# Lint backend
cd backend && source .venv/bin/activate && pylint app/

# Format backend
cd backend && source .venv/bin/activate && black app/

# Lint frontend
cd frontend && npm run lint

# Format frontend
cd frontend && npm run format
```

---

## 🐳 Docker Alternative (Full Stack)

If you prefer Docker for everything:

```bash
# Build and start all services
docker-compose -f docker-compose.open-source.yml up -d

# Wait for services to initialize (check logs)
docker-compose -f docker-compose.open-source.yml logs -f

# Run backend tests inside container
docker exec metamorph-api python -m pytest tests/unit/ -v
```

---

## 📚 Key Files and Directories

### Backend
- `backend/app/main.py` - FastAPI application entry
- `backend/app/services/` - Core business logic
- `backend/tests/unit/` - Unit tests (35 tests)
- `backend/requirements.txt` - Python dependencies

### Frontend
- `frontend/src/` - React source code
- `frontend/src/pages/` - Main page components
- `frontend/tests/` - Playwright end-to-end tests
- `frontend/package.json` - Node.js dependencies

### Configuration
- `.env.example` - Environment variables template
- `docker-compose.yml` - Docker service definitions
- `docker-compose.open-source.yml` - Full open-source stack

---

## 🔍 Troubleshooting

### Common Issues

**1. Pydantic Import Error**
```
ImportError: BaseSettings has been moved to pydantic-settings
```
**Fix:** Install pydantic-settings
```bash
pip install pydantic-settings
```

**2. Playwright Browser Missing**
```
Error: Executable doesn't exist at /home/user/.cache/ms-playwright/
```
**Fix:** Install browsers
```bash
npx playwright install
```

**3. Neo4j Connection Failed**
```
ServiceUnavailable: Couldn't connect to localhost:7687
```
**Fix:** Start Neo4j container
```bash
docker start <neo4j-container-id>
```

**4. MinIO Connection Failed**
```
EndpointConnectionError: Could not connect to localhost:9000
```
**Fix:** Start MinIO container and create bucket
```bash
docker start <minio-container-id>
docker exec minio mc mb local/metamorph-documents
```

---

## 🎯 Next Steps

1. **Explore the API**: http://localhost:8000/docs
2. **Try the frontend**: http://localhost:5173
3. **Run tests**: Verify everything works
4. **Start developing**: Add new features or fix issues

---

## 📞 Support

- **Documentation**: See `/docs` directory
- **Architecture**: `docs/guide/ARCHITECTURE.md`
- **Ontology**: `docs/ontology/unhcr-knowledge-ontology.ttl`
- **Issues**: Check GitHub issues for known problems

---

🎉 **You're ready to go!** The Metamorph knowledge pipeline is now running locally.
