#!/bin/bash
set -euo pipefail  # Exit on error, undefined vars, pipe failures
# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
# Logging configuration
ROOT_DIR="$(pwd)"
LOG_DIR="$ROOT_DIR/logs"
LOG_FILE="$LOG_DIR/startup_$(date '+%Y%m%d_%H%M%S').log"
ERROR_LOG="$LOG_DIR/error_$(date '+%Y%m%d_%H%M%S').log"
mkdir -p "$LOG_DIR"
# Logging functions
log_info() {
    local msg="$1"
    echo -e "${GREEN}[INFO]${NC} $msg" | tee -a "$LOG_FILE"
}
log_warning() {
    local msg="$1"
    echo -e "${YELLOW}[WARN]${NC} $msg" | tee -a "$LOG_FILE"
}
log_error() {
    local msg="$1"
    echo -e "${RED}[ERROR]${NC} $msg" | tee -a "$LOG_FILE" | tee -a "$ERROR_LOG"
}
log_debug() {
    local msg="$1"
    if [[ "${DEBUG:-false}" == "true" ]]; then
        echo -e "${BLUE}[DEBUG]${NC} $msg" | tee -a "$LOG_FILE"
    fi
}
command_exists() {
    command -v "$1" >/dev/null 2>&1
}
# Check ports
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 1
    else
        return 0
    fi
}
cleanup() {
  log_info "Received termination, shutting down child processes"
  pkill -P $$
  exit 0
}
trap cleanup SIGTERM SIGINT

log_info "\U1F4A1 Starting Metamorph platform - logs at $LOG_FILE"
# Pre-run checks
log_info "\U1F4CB Checking prerequisites..."
for req in python3 npm uvicorn; do
    if ! command_exists $req; then
        log_error "$req is not installed, please install it."
        exit 1
    fi
done
log_info "All required commands found."
# Check and build frontend
FRONTEND_DIR="frontend"
BACKEND_DIR="backend"
log_info "\U1F527 Building frontend..."
cd "$FRONTEND_DIR"
npm install &>> "$LOG_FILE"
npm run build &>> "$LOG_FILE"
cd ..
# Backend deps
log_info "\U1F527 Installing backend dependencies..."
cd "$BACKEND_DIR"
if [ ! -d .venv ]; then python3 -m venv .venv; fi
source .venv/bin/activate
pip install -r requirements.txt &>> "$LOG_FILE"
cd ..
log_info "\u2705 Installations done."
# Check for .env
if [ ! -f "backend/.env" ]; then
    log_warning "backend/.env missing - app may not have secrets! (You can continue for testing)"
fi
# Static asset env for FastAPI
export FRONTEND_BUILD_DIR="$(pwd)/frontend/dist"
log_info "\U1F680 Starting FastAPI + UI server..."
export PYTHONPATH="$ROOT_DIR/backend"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-config backend/logging.ini 2>&1 | tee -a "$LOG_FILE"
