# 🚀 Get Started with Metamorph (Local Developer Quickstart)

Welcome! This guide will walk you step-by-step through getting Metamorph running on your laptop for learning, development, and safe experimentation.

---

## 🛠️ **1. What you'll need**
- A computer running Windows, Mac, or Linux
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (highly recommended!)
- [Python 3.10+](https://www.python.org/downloads/) (for backend/scraper)
- [Node.js 18+](https://nodejs.org/en/) (for the frontend Wiki/curation dashboard)
- [Git](https://git-scm.com/downloads) (to download the codebase)
- (Optional) [Poetry](https://python-poetry.org/) or [pipenv] — if you want to manage Python envs

**No prior backend or frontend experience required—this guide is purposefully detailed!**

---

## 🧑‍💻 **2. Clone the repo**
```bash
git clone https://github.com/edouard-legoupil/metamorph.git
cd metamorph
```

---

## 🗃️ **3. Set Up Environment Variables**

Copy `.env.example` in both `/` and `/backend/` to `.env`, then edit. Basic local setup (add strong random strings for keys):

```bash
cp .env.example .env
cd backend && cp .env.example .env && cd ..
```

**Set at least these:**
- `FASTAPI_INGEST_URL=http://localhost:8000/ingest`
- `MCP_API_KEY=superlocalkey` (for agent/Bot API access)

_Credentials for Cloudflare/UNHCR-protected content fetches are OPTIONAL for local testing._

---

## 🐳 **4. Start All Services with Docker Compose**

1. Ensure Docker Desktop is running.
2. From the repo root, run:
```bash
docker compose up --build
```
This starts the backend API, database, Redis, the frontend, MinIO (S3 for file cache), Celery, etc.

3. After a while, visit:
- [http://localhost:8000/docs](http://localhost:8000/docs) — backend API docs
- [http://localhost:3000/](http://localhost:3000/) — frontend UI

4. (Optional): In another terminal:
```bash
make logs
```

**Common issues:**
- Backend or DB service not starting? Run `docker compose ps` and check logs with `docker compose logs backend` or `... logs postgres`.
- Port in use? Stop any services using 8000, 3000, or 5432 and retry.
- "FastAPI /ingest unreachable": Confirm Docker is running and your `.env` is correct.

---

## 🐍 **5. Developer (Non-Docker) Start**
If you want to run backend or frontends directly (outside Docker):

### Backend (Python/FastAPI)
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (React/Vite)
```bash
cd frontend
npm install
npm run dev  # Starts UI at http://localhost:3000/
```

**Common issues:**
- "No module named ...": Run `pip install -r requirements.txt` again inside your venv.
- Frontend stuck at splash/blank screen: Check `npm ls`, fix any reported errors with `npm install`, check for proxy issues.

---

## 🚨 **6. Test the App**

- API explorer: [http://localhost:8000/docs](http://localhost:8000/docs)
- Scraper test:
    ```bash
    cd scraper
    python -m scraper run --round 1
    python -m scraper status
    ```
- Frontend: Visit [http://localhost:3000/](http://localhost:3000/) — try viewing cards, submit a new one, open the curation dashboard, verify a block.
- Run backend unit tests (if desired):
    ```bash
    cd backend
    pytest
    ```
- Try agent tool:
    ```bash
    python -m mcp.agent_sdk  # or use the Python SDK to call MCP endpoints with your key
    ```

---

## 🧹 **7. Debug/Reset**

- Wipe all cached fetches: `python -m scraper cache --clear`
- View Docker service logs: `docker compose logs -f`
- Kill and restart entire stack: `docker compose down && docker compose up`
- Problems with file cache: delete `./data/raw/` and retry (will not destroy the DB)

---

## 🌟 Congratulations!
You now have the complete platform running locally. All developer, devops, curator and agentic interfaces are ready for safe experimentation.

---

### 💡 **If Something Goes Wrong**
- Use the command line to check logs: `docker compose logs [service]`, `python -m scraper status`, or `pytest` for backend errors.
- If a web page “doesn’t load”: hard-refresh your browser. Clear cache if things look weird. Run `npm run dev` anew if React fails.
- Backend or API errors: make sure all required `.env` variables are set, and the database is up (`docker compose logs postgres` to see if it's stuck).
- Still stuck? Run `pip install -r requirements.txt` and `npm install` again from a clean terminal. Check versions!

---

## 🛠 Support
- For new contributors: read `docs/README.md`, `docs/DEVELOPER.md`.
- For API docs: see `docs/API_AUTO.md` (auto-generated) and `docs/CLI.md`.
- Security: see `docs/SECURITY.md`. For curation/agent use: see `docs/CURATION.md` and `docs/AGENT.md`.
