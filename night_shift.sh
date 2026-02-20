#!/usr/bin/env bash
# =============================================================================
# NIGHT SHIFT — Halilit Dark Factory | Autonomous Improvement Protocol
# =============================================================================
# Runs the full end-to-end self-improvement cycle:
#   0. GRAND TASK FORCE — Chief-driven catalog + UI autonomous polish (DAG)
#         Phases: rebuild catalog → Steerer audit → Visual QA → Builder fix → commit
#   1. STEER   — Strategist generates next-priority specs
#   2. HEAL    — Watchdog scans → Builder fixes → re-scans (up to 3 cycles)
#   3. DOC     — Scribe refreshes docs/ARCHITECTURE.md from current code
#   4. COMMIT  — Repo Agent: semantic commit + push
#
# Usage:
#   ./night_shift.sh                  # full protocol (incl. Grand Task Force)
#   ./night_shift.sh --heal-only      # skip steer, doc, and grand task force
#   ./night_shift.sh --max-cycles 5   # override heal cycle cap
#
# Requires GEMINI_API_KEY (or GOOGLE_API_KEY) to be set.
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FACTORY_PY="$SCRIPT_DIR/factory.py"

# ── Load .env if present ──────────────────────────────────────────────────────
if [[ -f "$SCRIPT_DIR/.env" ]]; then
    set -a
    # shellcheck disable=SC1091
    source "$SCRIPT_DIR/.env"
    set +a
fi

# ── Activate venv if present and not already active ───────────────────────────
if [[ -z "${VIRTUAL_ENV:-}" && -f "$SCRIPT_DIR/.venv/bin/activate" ]]; then
    # shellcheck disable=SC1091
    source "$SCRIPT_DIR/.venv/bin/activate"
fi

# ── Defaults ──────────────────────────────────────────────────────────────────
MAX_CYCLES=3
SKIP_STEER=false
SKIP_DOC=false
SKIP_GTF=false

# ── Argument Parsing ──────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --heal-only)
            SKIP_STEER=true
            SKIP_DOC=true
            SKIP_GTF=true
            shift ;;
        --max-cycles)
            MAX_CYCLES="$2"
            shift 2 ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--heal-only] [--max-cycles N]"
            exit 1 ;;
    esac
done

# ── Preflight ─────────────────────────────────────────────────────────────────
if [[ -z "${GEMINI_API_KEY:-}" && -z "${GOOGLE_API_KEY:-}" ]]; then
    echo "❌ GEMINI_API_KEY (or GOOGLE_API_KEY) is not set. Night Shift aborted."
    exit 1
fi

echo ""
echo "🌙 ============================================="
echo "🌙  NIGHT SHIFT  —  $(date '+%Y-%m-%d %H:%M')"
echo "🌙 ============================================="
echo ""

START_TS=$(date +%s)

# ── Phase 0: GRAND TASK FORCE — Catalog + UI Autonomous Polish ───────────────
if [[ "$SKIP_GTF" == "false" ]]; then
    echo "🏭 [0/4] Grand Task Force — Catalog & UI autonomous polish..."
    python3 "$FACTORY_PY" grand_task_force || echo "⚠️  Grand Task Force encountered an error (non-fatal)"
    echo ""
fi

# ── Step 1: STRATEGIST ────────────────────────────────────────────────────────
if [[ "$SKIP_STEER" == "false" ]]; then
    echo "🧭 [1/4] Running Strategist (steer)..."
    python3 "$FACTORY_PY" steer || echo "⚠️  Steer step encountered an error (non-fatal)"
    echo ""
fi

# ── Step 2: SELF-HEALING LOOP ─────────────────────────────────────────────────
echo "🚑 [3/4] Running Self-Healing Loop (heal, max $MAX_CYCLES cycles)..."
python3 "$FACTORY_PY" heal "$MAX_CYCLES" || echo "⚠️  Heal step encountered an error (non-fatal)"
echo ""

# ── Step 3: DOCUMENTATION REFRESH ────────────────────────────────────────────
if [[ "$SKIP_DOC" == "false" ]]; then
    echo "📝 [4/4] Refreshing Documentation (doc)..."
    python3 "$FACTORY_PY" doc || echo "⚠️  Doc step encountered an error (non-fatal)"
    echo ""
fi

END_TS=$(date +%s)
ELAPSED=$((END_TS - START_TS))

# ── Step 4: COMMIT & PUSH ─────────────────────────────────────────────────────
echo "📦 [Final] Committing and pushing progress..."
python3 "$FACTORY_PY" commit || echo "⚠️  Commit step encountered an error (non-fatal)"
echo ""

# ── Heartbeat: Catalog delta scan + HEARTBEAT.md ─────────────────────────────
echo "🫀 [Heartbeat] Running catalog delta scan and writing HEARTBEAT.md..."
python3 backend/factory/heartbeat_daemon.py || echo "⚠️  Heartbeat daemon encountered an error (non-fatal)"
echo ""

echo ""
echo "☀️  ============================================="
echo "☀️  Night Shift Complete — ${ELAPSED}s elapsed"
echo "☀️  $(date '+%Y-%m-%d %H:%M')"
echo "☀️  ============================================="
echo ""
