#!/bin/bash
# =============================================================================
# start_console.sh — Legacy alias for the Dark Factory Ignition Sequence.
# Delegates to ignite_factory.sh (the canonical entry point since v9.7.1).
# =============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/ignite_factory.sh" "$@"
