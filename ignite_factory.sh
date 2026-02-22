#!/usr/bin/env bash
# ignite_factory.sh — Halilit Support Center factory ignition script
# Starts backend, frontend dev server, and optional MCP warden in parallel.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

log() { echo "[ignite] $*"; }

log "Starting Halilit Support Center..."

# ── Backend ──────────────────────────────────────────────────────────────────
log "Launching FastAPI backend on :8000"
cd "$ROOT"
uvicorn backend.server:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# ── Frontend ─────────────────────────────────────────────────────────────────
log "Launching Vite frontend on :5173"
cd "$ROOT/frontend"
pnpm run dev &
FRONTEND_PID=$!

# ── Warden (optional) ────────────────────────────────────────────────────────
if [ "${WARDEN_ENABLED:-false}" = "true" ]; then
    log "Launching Warden loop"
    cd "$ROOT"
    python -m local_autonomy.warden &
    WARDEN_PID=$!
fi

log "All processes started. Press Ctrl-C to stop."
wait $BACKEND_PID $FRONTEND_PID
