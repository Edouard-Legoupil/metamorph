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