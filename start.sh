#!/usr/bin/env bash
# Start Halilit Support Center: backend + frontend, then open app in browser.
# Run from project root: ./start.sh   (or: bash start.sh)

set -e
cd "$(dirname "$0")"

# Use project venv if it exists (so uvicorn and deps are available)
if [ -d ".venv" ]; then
  source .venv/bin/activate
  echo "Using Python from .venv"
fi

echo "Starting Halilit Support Center..."
echo ""

# Start backend in background (port 8000)
PYTHONPATH=. python3 -m uvicorn backend.server:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "  Backend starting (PID $BACKEND_PID) on http://localhost:8000"

# Give backend a moment to bind
sleep 3

# Open browser in a few seconds (so frontend is up)
(sleep 6 && open "http://localhost:5173" 2>/dev/null || true) &
echo "  Browser will open at http://localhost:5173 in a few seconds."
echo ""

# Start frontend in foreground (port 5173) — keeps this script running
echo "  Starting frontend..."
echo "  Keep this terminal open. To stop: press Ctrl+C."
echo ""
cd frontend
if command -v pnpm &>/dev/null; then
  exec pnpm dev
else
  exec npm run dev
fi
