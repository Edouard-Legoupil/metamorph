Create a production-ready Docker Compose setup for a full-stack Python/React application called "Metamorph" - a platform that converts PDFs to AI-friendly Markdown wikis.

Requirements:
- Docker Compose with services for:
  - FastAPI backend (Python 3.11)
  - PostgreSQL 15 (with pgvector for future embeddings)
  - Redis 7 (for Celery)
  - React frontend (Node 18)
  - Wiki.js (latest) - pre-configured with PostgreSQL
  - LiteLLM proxy (latest) for AI provider abstraction

The docker-compose.yml should:
- Use environment variables for all configuration
- Include health checks for all services
- Set up proper networking between services
- Mount volumes for persistence (DB, uploads, wiki data)
- Include a .env.example file with all required variables
- Have development vs production profiles

Also create a Makefile with common commands: up, down, logs, migrate, shell-backend, shell-frontend

The LiteLLM proxy should be configured to support OpenAI, Anthropic, and local models via Ollama, with API keys read from environment.

Include as well S3/MinIO, static nginx, Celery worker containers

want Gunicorn/workers (for FastAPI)


Build a full-stack Metamorph developer environment with a FastAPI backend (Python 3.11+), React frontend (Node 18+), PostgreSQL 15 (pgvector enabled), Neo4j for knowledge graph, Redis (for queue and caching), MinIO for object storage, and Wiki.js for human curation workflow. Orchestrate all infrastructure using Docker Compose, with clear .env-based configuration for all services, volumes for persistence, and health checks so each container can be verified as "ready". Provide a Makefile with commands for up, down, build, migrate, and shell access to backend/frontend. Document all service endpoints and credentials for dev/production, and ensure onboarding docs are complete with troubleshooting and extension steps for future contributors.

Verification & Test Guidance
- [ ] Confirm docker-compose.yml defines all listed services and uses environment variables for configuration and secrets.
- [ ] Service logs or Docker healthchecks verify that each service (backend, frontend, DB, graph, cache, object store, wiki) launches and is available.
- [ ] Makefile contains targets for key workflows and works without requiring manual container names or IDs.
- [ ] .env and onboarding documentation describe how to set up/run the stack and what to expect from each service.
- [ ] Run Makefile and Docker Compose to bring up stack, then check all endpoints (API, UI, DB, graph, cache, objects, wiki) are accessible, persistent, and can be manually stopped/restarted without loss.
- [ ] For environments running outside Docker, docs explain how to override or connect to each containerized service.