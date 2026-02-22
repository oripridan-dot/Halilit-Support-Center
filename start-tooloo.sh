#!/bin/bash

###############################################################################
# 🔌 HALILIT SUPPORT CENTER — TooLoo Startup Script
# 
# This script attaches the external TooLoo engine (repository-agnostic AI 
# orchestrator) to this Halilit repository via the Umbilical Cord.
#
# Usage:
#   ./start-tooloo.sh "Your mandate here"
#   ./start-tooloo.sh --auto "Build the system"
#   ./start-tooloo.sh --dry-run "Review plan"
#   ./start-tooloo.sh --briefing
#
###############################################################################

set -e

# Colors
CYAN='\033[96m'
GREEN='\033[92m'
YELLOW='\033[93m'
RED='\033[91m'
BOLD='\033[1m'
RESET='\033[0m'

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLOO_PATH="${SCRIPT_DIR}/../tooloo-core"
NEXUS_PATH="${TOOLOO_PATH}/nexus.py"

# Verify TooLoo exists
if [ ! -f "$NEXUS_PATH" ]; then
    echo -e "${RED}${BOLD}❌ ERROR: TooLoo Core not found at ${TOOLOO_PATH}${RESET}"
    echo "Make sure tooloo-core is cloned in the parent directory:"
    echo "  cd .. && git clone https://github.com/oripridan-dot/tooloo-core.git"
    exit 1
fi

# Display header
echo -e "${CYAN}${BOLD}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  🔌 HALILIT SUPPORT CENTER — TooLoo Umbilical Cord     ║"
echo "║  Attaching external AI orchestrator to local repository  ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${RESET}"

echo -e "${CYAN}[NEXUS]${RESET} Initializing TooLoo Core..."
echo -e "${CYAN}[TARGET]${RESET} Repository: ${SCRIPT_DIR}"
echo ""

# Verify Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ ERROR: Python 3 is required but not found.${RESET}"
    exit 1
fi

# Execute nexus with target pointing to Halilit
# Pass all script arguments to nexus.py
python3 "$NEXUS_PATH" --target "$SCRIPT_DIR" "$@"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ TooLoo cycle completed successfully.${RESET}"
else
    echo -e "${RED}❌ TooLoo cycle exited with code: $EXIT_CODE${RESET}"
fi

exit $EXIT_CODE
