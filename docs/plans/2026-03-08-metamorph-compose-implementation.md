I'm using the writing-plans skill to create the implementation plan.

# Metamorph Compose Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Deliver a production-ready Docker Compose stack, supporting Metamorph’s FastAPI, PostgreSQL+pgvector, Redis/Celery, React, Wiki.js, LiteLLM proxy, and the requested helper files.

**Architecture:** A single `docker-compose.yml` declares all services sharing a network, volumes for persistence, and health checks, with profiles distinguishing production vs development mounts, while the Makefile wraps orchestrated commands.

**Tech Stack:** Docker Compose v3+, FastAPI 3.11, PostgreSQL 15+pgvector, Redis 7, React (Node 18), Wiki.js, LiteLLM proxy, Makefile.

---

### Task 1: Scaffold backend/frontend folders with README

**Files:**
- Create: `backend/README.md`, `frontend/README.md`, `backend/.gitkeep`, `frontend/.gitkeep`

**Step 1: Document expectations**
Draft minimal README text describing the future FastAPI backend and React frontend responsibilities.

**Step 2: Create folders + placeholders**
Create `backend/` and `frontend/` directories, add `.gitkeep` files, and paste README content for each.

**Step 3: Validate structure**
Run `ls backend frontend` to confirm both directories contain `.gitkeep` and README.
Expected: both directories list the two files.

**Step 4: Review README details**
Open each README to ensure they mention Docker mounts and future entrypoints for FastAPI/React.

**Step 5: Stage and commit**
Run `git add backend frontend` and `git commit -m "chore: add backend and frontend scaffolds"` to capture the placeholders.

### Task 2: Craft docker-compose.yml with required services, volumes, profiles

**Files:**
- Create: `docker-compose.yml`

**Step 1: Outline services in comments**
List each service, associated ports, env dependencies, volumes, and health checks on a scratch note to avoid omissions.

**Step 2: Implement base Compose**
Write `docker-compose.yml` defining fastapi, postgres (with pgvector), redis, frontend, wiki, litellm services. Add named volumes (postgres_data, wiki_data, uploads maybe), shared network, environment from `.env`, and healthcheck commands (e.g., `curl` for HTTP, `pg_isready` for Postgres, `redis-cli ping`).

**Step 3: Add LiteLLM config mount and provider env**
Include a volume mount for `litellm-config.yaml` and `environment` entries for OpenAI/Anthropic/Ollama keys. Ensure the litellm service exposes a single port and points backend/frontend requests to it.

**Step 4: Introduce profiles**
Use `profiles` blocks (default `production`, plus `dev`) so dev profile mounts `./backend`/`./frontend`, sets reload flags, and exposes additional ports (e.g., 5173). Verify `network_mode`/`depends_on`. Re-run `docker compose config` to validate YAML.
Expected: outputs combined service list with no errors.

**Step 5: Stage and commit**
`git add docker-compose.yml` then `git commit -m "feat: add docker compose stack"`.

### Task 3: Provide .env.example listing env variables

**Files:**
- Create: `.env.example`

**Step 1: Enumerate vars**
From Compose references, list all required vars: Postgres creds, Redis URL, LiteLLM port/endpoint, API keys, FastAPI/CD config, Wiki.js secrets, dev flags.

**Step 2: Create template file**
Write `.env.example` with commented sections for database, cache, liteLLM, wiki, and frontend/backends to guide users.

**Step 3: Cross-check variable usage**
Run `rg -o "\$\{[A-Z0-9_]+\}" docker-compose.yml | sort | uniq` to ensure each referenced var appears in `.env.example` and that there are no mismatches.
Expected: all keys listed, nothing missing.

**Step 4: Mention required defaults**
Document default ports (e.g., FASTAPI_PORT=8000) and clarify when they differ between profiles.

**Step 5: Stage and commit**
`git add .env.example` + `git commit -m "docs: add env example for compose"`.

### Task 4: Add Makefile with helper commands

**Files:**
- Create: `Makefile`

**Step 1: Plan commands**
List commands (up, down, logs, migrate, shell-backend, shell-frontend) with their docker compose invocations, including optional PROFILE env.

**Step 2: Implement Makefile**
Write rules that call `docker compose --env-file .env` and pass `${PROFILE??production}` as needed; ensure `migrate` runs `poetry run alembic upgrade head` or similar inside backend container.

**Step 3: Validate command syntax**
Run `make -n up` to ensure make expands to valid docker compose commands.
Expected: prints `docker compose ...` without executing.

**Step 4: Add comments**
Add short comments describing each target’s purpose for future maintainers.

**Step 5: Stage and commit**
`git add Makefile` + `git commit -m "chore: add makefile"`.

### Task 5: Configure LiteLLM proxy support files

**Files:**
- Create: `litellm-config.yaml`

**Step 1: Draft config**
Define providers (OpenAI, Anthropic, Ollama) referencing env vars for keys/URLs, include general settings (listen port, default context), and document `litellm` port.

**Step 2: Save config with placeholders**
Write YAML with `${OPENAI_API_KEY}` style placeholders so Compose can inject values via env file or envsubst run before container start.

**Step 3: Reference config in Compose and README**
Ensure `docker-compose.yml` mounts this file into the LiteLLM container and that README or `.env.example` describes where to put API keys.

**Step 4: Verify Docker config includes litellm service**
`docker compose config --services` should list `litellm`; re-run to ensure config changes are reflected.
Expected: service list includes litellm.

**Step 5: Stage and commit**
`git add litellm-config.yaml docker-compose.yml .env.example` (if needed after tweaks) and `git commit -m "feat: configure litellm proxy"`.

---

Plan complete and saved to `docs/plans/2026-03-08-metamorph-compose-implementation.md`. Two execution options:

1. **Subagent-Driven (this session)** - use superpowers:subagent-driven-development with fresh subagents per task and review checkpoints.
2. **Parallel Session (separate)** - start a new session running superpowers:executing-plans with this plan file.

Which approach?
