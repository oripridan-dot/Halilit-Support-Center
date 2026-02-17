#!/usr/bin/env bash
# Start Halilit Support Center: backend + frontend, then open app in browser.
# Run from project root: ./start.sh
#
# Robust startup: kills stale processes, waits for backend health before frontend.

set -e
cd "$(dirname "$0")"

# Use project venv if it exists
if [ -d ".venv" ]; then
  source .venv/bin/activate
  echo "Using Python from .venv"
fi

echo "Starting Halilit Support Center..."
echo ""

# 1. Kill any processes on 8000 (backend) and 5173 (frontend)
kill_port() {
  local port=$1
  local pids
  pids=$(lsof -ti ":$port" 2>/dev/null || true)
  if [ -n "$pids" ]; then
    echo "  Stopping process on port $port (PIDs: $pids)"
    echo "$pids" | xargs kill -9 2>/dev/null || true
    sleep 1
  fi
}
kill_port 8000
kill_port 5173
sleep 1

# 2. Start backend in background
echo "  Starting backend on http://localhost:8000..."
PYTHONPATH=. python3 -m uvicorn backend.server:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# 3. Wait for backend to respond to /api/health (max 45 seconds)
echo "  Waiting for backend to be ready..."
MAX_WAIT=45
ELAPSED=0
while [ $ELAPSED -lt $MAX_WAIT ]; do
  if curl -sf http://127.0.0.1:8000/api/health >/dev/null 2>&1; then
    echo "  Backend ready."
    break
  fi
  sleep 2
  ELAPSED=$((ELAPSED + 2))
  echo "  ... still waiting (${ELAPSED}s)"
done

if ! curl -sf http://127.0.0.1:8000/api/health >/dev/null 2>&1; then
  echo ""
  echo "ERROR: Backend did not start. Check for errors above."
  kill $BACKEND_PID 2>/dev/null || true
  exit 1
fi

# 4. Open browser after frontend is up
(sleep 8 && open "http://localhost:5173" 2>/dev/null || true) &
echo ""
echo "  Starting frontend on http://localhost:5173..."
echo "  Keep this terminal open. To stop: press Ctrl+C."
echo ""

# 5. Start frontend in foreground
cd frontend
if command -v pnpm &>/dev/null; then
  exec pnpm dev
else
  exec npm run dev
fi
