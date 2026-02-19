#!/usr/bin/env bash
# =============================================================================
# NIGHT SHIFT — Halilit Dark Factory | Autonomous Improvement Protocol
# =============================================================================
# Runs the full self-improvement cycle:
#   1. STEER   — Strategist generates next-priority specs
#   2. HEAL    — Watchdog scans → Builder fixes → re-scans (up to 3 cycles)
#   3. DOC     — Scribe refreshes docs/ARCHITECTURE.md from current code
#
# Usage:
#   ./night_shift.sh                  # full protocol
#   ./night_shift.sh --heal-only      # skip steer and doc
#   ./night_shift.sh --max-cycles 5   # override heal cycle cap
#
# Requires GEMINI_API_KEY (or GOOGLE_API_KEY) to be set.
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FACTORY_PY="$SCRIPT_DIR/factory.py"

# ── Defaults ──────────────────────────────────────────────────────────────────
MAX_CYCLES=3
SKIP_STEER=false
SKIP_DOC=false

# ── Argument Parsing ──────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --heal-only)
            SKIP_STEER=true
            SKIP_DOC=true
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

# ── Step 1: STRATEGIST ────────────────────────────────────────────────────────
if [[ "$SKIP_STEER" == "false" ]]; then
    echo "🧭 [1/3] Running Strategist (steer)..."
    python3 "$FACTORY_PY" steer || echo "⚠️  Steer step encountered an error (non-fatal)"
    echo ""
fi

# ── Step 2: SELF-HEALING LOOP ─────────────────────────────────────────────────
echo "🚑 [2/3] Running Self-Healing Loop (heal, max $MAX_CYCLES cycles)..."
python3 "$FACTORY_PY" heal "$MAX_CYCLES" || echo "⚠️  Heal step encountered an error (non-fatal)"
echo ""

# ── Step 3: DOCUMENTATION REFRESH ────────────────────────────────────────────
if [[ "$SKIP_DOC" == "false" ]]; then
    echo "📝 [3/3] Refreshing Documentation (doc)..."
    python3 "$FACTORY_PY" doc || echo "⚠️  Doc step encountered an error (non-fatal)"
    echo ""
fi

END_TS=$(date +%s)
ELAPSED=$((END_TS - START_TS))

echo ""
echo "☀️  ============================================="
echo "☀️  Night Shift Complete — ${ELAPSED}s elapsed"
echo "☀️  $(date '+%Y-%m-%d %H:%M')"
echo "☀️  ============================================="
echo ""
