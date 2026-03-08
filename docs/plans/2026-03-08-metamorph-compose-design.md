# Metamorph Docker Compose Design

## Context
Metamorph is a Python/React platform that turns PDFs into AI-friendly Markdown wikis. The goal is a production-ready Docker Compose stack that covers FastAPI, PostgreSQL 15 with pgvector, Redis, Celery, React, Wiki.js, and LiteLLM proxy, while allowing a development profile with live code mounts.

## Services and Networking
- **fastapi**: Python 3.11 backend. Depends on Postgres, Redis, and LiteLLM proxy. Exposes HTTP/health endpoint. In dev profile it mounts `./backend` and enables reload. In prod it uses static image/build.
- **postgres**: PostgreSQL 15 + pgvector extension. Persists to `pgdata` volume. Health check via `pg_isready`. Exposes port only for `wiki` (not host). Credentials supplied via env.
- **redis**: Redis 7 for Celery; persistent volume if needed. Health check via `redis-cli ping`.
- **frontend**: React (Node 18). In dev profile runs `npm run dev` with host mount; in prod builds and serves static assets (e.g., via `npm run build` then `serve`). Depends on backend/LiteLLM as needed. Health check hitting `/` or `vite` status.
- **wiki**: Wiki.js latest image configured via env to use same Postgres data; data stored in `wiki_data` volume; health check via HTTP.
- **litellm**: Latest LiteLLM proxy configured through mounted `litellm-config.yaml` referencing OpenAI, Anthropic, and Ollama (local). Exposes a port for backend/frontend; reads API keys from env.
- Shared bridge network ensures services reach each other via hostnames.

## Environment
`.env.example` will list:
- Database credentials (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `PGVECTOR_DB` if needed)
- Redis password/port if used, or just URL
- LiteLLM provider keys (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `OLLAMA_URL`)
- FastAPI settings: `FASTAPI_PORT`, `LITELLM_PROXY_URL`, `CELERY_BROKER_URL`
- React build env and API endpoints
- Wiki.js env (db URL, secrets)
- Generic `APP_ENV` to toggle profile defaults

Each service draws its vars from Compose through `env_file` or `environment` entries referencing these env vars.

## Profiles
- Default profile (production) uses built images, no host mounts, and exposes only necessary ports for FastAPI, Wiki, LiteLLM, and optional frontend static server.
- `dev` profile mounts `./backend` and `./frontend`, runs dev servers (FastAPI with reload, React dev server), and may expose additional ports (e.g., 8000, 5173). Extra env toggles like `DEV_MODE=true` are set in Compose via `profiles: ["dev"]` sections.

## Volumes & Persistence
- `postgres_data` for Postgres data (with pgvector extension installed in Dockerfile/init).
- `wiki_data` for Wiki.js uploads/configuration.
- `frontend_build` and `backend_uploads` if needed for storing generated content between restarts.
- LiteLLM config mounted from repo (or generated from env at runtime).

## LiteLLM Configuration
A `litellm-config.yaml` template is stored in repo and references provider-specific env vars. Compose ensures the file has placeholders filled by env at runtime (via `env_file` or simple templating). LiteLLM listens on `LITELLM_PORT` and exposes HTTP endpoints used by backend/React.

## Makefile Commands
- `make up [profile=production]`: runs `docker compose --profile ${profile}` up -d
- `make down`: stops services
- `make logs SERVICE`: tails logs
- `make migrate`: execs into backend to run Alembic migrations
- `make shell-backend`: `docker compose exec fastapi /bin/sh`
- `make shell-frontend`: similar for frontend

## Next Steps
Once this design is approved, we will record it, then use the writing-plans skill to create an implementation plan before touching compose/Makefile files.
