#!/bin/bash
set -euo pipefail

# Colors for output
echo -e "\n\033[1;36m🧠 Metamorph Local Dev Bootstrap\033[0m\n"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ROOT_DIR="$(pwd)"
LOG_DIR="$ROOT_DIR/logs"
LOG_FILE="$LOG_DIR/startup_$(date '+%Y%m%d_%H%M%S').log"
ERROR_LOG="$LOG_DIR/error_$(date '+%Y%m%d_%H%M%S').log"
mkdir -p "$LOG_DIR"

log_info()   { echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"; }
log_warning(){ echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"; }
log_error()  { echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE" | tee -a "$ERROR_LOG"; }
log_debug()  { [ "${DEBUG:-false}" = "true" ] && echo -e "${BLUE}[DEBUG]${NC} $1" | tee -a "$LOG_FILE"; }
command_exists() { command -v "$1" >/dev/null 2>&1; }
check_port() { lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; }

cleanup() {
  log_info "Received termination, shutting down child processes"
  pkill -P $$
  exit 0
}
trap cleanup SIGTERM SIGINT

log_info "🚦 Checking system prerequisites..."
for req in python3 npm uvicorn psql redis-cli; do
    if ! command_exists $req; then
        log_error "$req is not installed. Please install it."
        exit 1
    fi
done

for svc in "PostgreSQL:5432" "Neo4j:7687" "Redis:6379"; do
  PORT="${svc#*:}"
  NAME="${svc%%:*}"
  if ! check_port $PORT; then
    log_error "$NAME at port $PORT not listening. Please start $NAME."
    MISSING=true
  else
    log_info "$NAME on port $PORT detected."
  fi
done

if ! check_port 9000; then
  log_warning "MinIO (port 9000) not found. If using local dev for object storage, make sure to configure S3-like endpoint or update .env."
fi

# Check required env vars
ENV_OK=true
log_info "🔎 Checking back-end environment (.env)..."
if [ ! -f "backend/.env" ]; then
  log_warning "backend/.env missing — secrets/environment are required for some operations! (You can continue for testing, but this may break DB/graph connection)"
  ENV_OK=false
fi
REQUIRED_VARS=(POSTGRES_DSN NEO4J_URI REDIS_URL)
for VAR in "${REQUIRED_VARS[@]}"; do
  if ! grep -q -E "^$VAR=" backend/.env 2>/dev/null; then
    log_warning "$VAR missing from backend/.env. Set this for full connectivity."
    ENV_OK=false
  fi
done

export $(grep -v '^#' backend/.env | xargs 2>/dev/null || true)

# Check DB connection
if ! PGPASSWORD="${PGPASSWORD:-}" psql "$POSTGRES_DSN" -c '\q' &>/dev/null; then
  log_error "Could not connect to Postgres: $POSTGRES_DSN"
  MISSING=true
else
  log_info "Connected to PostgreSQL successfully."
fi
# Check Neo4j
if command_exists cypher-shell && [ -n "${NEO4J_URI:-}" ]; then
  if ! cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" "RETURN 1;" &>/dev/null; then
    log_error "Could not connect to Neo4j: $NEO4J_URI"
    MISSING=true
  else
    log_info "Connected to Neo4j successfully."
  fi
else
  log_warning "cypher-shell not installed or NEO4J_URI missing. Skipping Neo4j check."
fi
# Check Redis
if ! redis-cli -u "${REDIS_URL:-redis://localhost:6379}" ping | grep -q PONG; then
  log_error "Redis is not responding at $REDIS_URL"
  MISSING=true
else
  log_info "Redis connection OK."
fi

if [ "${MISSING:-false}" = true ]; then
  log_error "One or more core services are missing or down. Abort."
  exit 2
else
  log_info "All base services (DB, Graph, Redis) available."
fi

# Build/rebuild frontend and backend
log_info "🔨 Building frontend (npm run build)..."
cd frontend && npm install && npm run build &>> "$LOG_FILE" && cd ..
log_info "🔨 Installing backend dependencies (venv/poetry/pip)..."
cd backend
if [ ! -d .venv ]; then python3 -m venv .venv; fi
source .venv/bin/activate
pip install -r requirements.txt &>> "$LOG_FILE"
cd ..
log_info "✅ Build steps complete."

# Set up static asset env for FastAPI
export FRONTEND_BUILD_DIR="$ROOT_DIR/frontend/dist"
export PYTHONPATH="$ROOT_DIR/backend"
log_info "🚀 Starting FastAPI with UI..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-config backend/logging.ini 2>&1 | tee -a "$LOG_FILE"