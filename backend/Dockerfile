# syntax=docker/dockerfile:1
FROM node:18 as frontend
WORKDIR /frontend
COPY ./frontend/package*.json ./
RUN npm install
COPY ./frontend .
RUN npm run build

FROM python:3.11-slim as backend
WORKDIR /app
COPY ./backend/pyproject.toml ./backend/poetry.lock ./
RUN pip install poetry && poetry config virtualenvs.create false \
    && poetry install --only main --no-root
COPY ./backend /app
COPY --from=frontend /frontend/dist /app/frontend_dist
RUN pip install gunicorn[uvloop]

# Tell FastAPI where to find the frontend static files
ENV FRONTEND_BUILD_DIR=/app/frontend_dist

CMD ["gunicorn", "app.main:app", "--bind", "0.0.0.0:8000", "--worker-class", "uvicorn.workers.UvicornWorker", "--workers", "4", "--timeout", "60"]
