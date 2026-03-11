# Metamorph FastAPI Backend

This directory will house the FastAPI (Python 3.11) source code for the Metamorph API. `docker-compose` mounts it into the `fastapi` service, so keep your application entrypoint (e.g., `app/main.py`) and dependency files (`pyproject.toml`, `requirements.txt`) here.

During development the service runs with live reload, and in production it builds a static image from this context.
