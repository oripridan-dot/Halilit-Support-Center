#!/bin/bash
# =============================================================================
# start_console.sh — Legacy alias for the TooLoo startup entrypoint.
# Delegates to start-tooloo.sh (the canonical entry point).
# See docs/WORKFLOW.md for the full TooLoo PR loop.
# =============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/../start-tooloo.sh" "$@"
