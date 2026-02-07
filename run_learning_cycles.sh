#!/bin/bash
# 🚀 Agent Learning Continuation Guide
# Run your Trinity Swarm agents through additional learning cycles

set -e

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║   🚀 AGENT LEARNING CONTINUATION GUIDE                          ║"
echo "║                                                                  ║"
echo "║   Trinity Swarm: CommercialScout, OfficialVerifier,             ║"
echo "║   ExternalValidator                                            ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Set Python path
WORKSPACE="/workspaces/Halilit-Support-Center"
export PYTHONPATH="${WORKSPACE}:${PYTHONPATH}"
PYTHON="${WORKSPACE}/.venv/bin/python"

echo -e "${YELLOW}Current Status:${NC}"
echo "  • Current Accuracy: 35.5%"
echo "  • Target Accuracy: 98.0%"
echo "  • Cycles Completed: 30/85"
echo "  • Phase: Phase 1 (50.7% complete)"
echo ""

# Function to run cycles
run_cycles() {
    local num_cycles=$1
    local description=$2
    
    echo -e "${GREEN}Running $num_cycles learning cycles...${NC}"
    echo "Description: $description"
    echo ""
    
    cd "${WORKSPACE}"
    
    $PYTHON -c "
import sys
sys.path.insert(0, '${WORKSPACE}')

from backend.unified_learning_system_v73 import run_enhanced_training
import logging

logging.basicConfig(level=logging.WARNING)

cycles, accuracies = run_enhanced_training(num_cycles=${num_cycles})

print()
print('✅ Training Complete!')
if accuracies:
    print(f'Final Accuracy: {accuracies[-1]:.1f}%')
    print(f'Improvement: +{(accuracies[-1] - accuracies[0]):.1f}%')
" 2>&1 | grep -v "Failed to parse"
    
    echo ""
    echo -e "${GREEN}✨ Cycle batch complete!${NC}"
    echo ""
}

# Check command line argument
if [ $# -eq 0 ]; then
    echo -e "${YELLOW}Usage:${NC}"
    echo "  $0 <option>"
    echo ""
    echo -e "${YELLOW}Options:${NC}"
    echo "  quick      Run 10 cycles (reach ~46% accuracy)"
    echo "  phase1     Run 30 cycles (reach ~65% accuracy)"  
    echo "  phase2     Run 55 cycles (reach 70% Phase 1 target)"
    echo "  full       Run 85 cycles (reach 98% target - FULL JOURNEY)"
    echo "  custom N   Run N cycles (custom number)"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0 quick"
    echo "  $0 phase1"
    echo "  $0 custom 20"
    echo ""
    exit 0
fi

case "$1" in
    quick)
        run_cycles 10 "Quick learning burst - target: 46% accuracy"
        ;;
    phase1)
        run_cycles 30 "Phase 1 progression - target: 65% accuracy"
        ;;
    phase2)
        run_cycles 55 "Complete Phase 1 - target: 70% (Phase 2 start)"
        ;;
    full)
        run_cycles 85 "FULL JOURNEY - target: 98% perfection"
        ;;
    custom)
        if [ -z "$2" ]; then
            echo "Error: custom option requires a number"
            echo "Usage: $0 custom <number>"
            exit 1
        fi
        run_cycles "$2" "Custom training - $2 cycles"
        ;;
    *)
        echo "Unknown option: $1"
        echo "Use: $0 quick|phase1|phase2|full|custom N"
        exit 1
        ;;
esac

echo -e "${BLUE}"
echo "═════════════════════════════════════════════════════════════"
echo ""
echo "🎯 Next Steps:"
echo "  • Check progress: curl http://localhost:8000/api/learning/manifest | jq"
echo "  • View detailed report: cat LEARNING_PROGRESS_REPORT.md"
echo "  • Run more cycles: $0 <option>"
echo ""
echo "═════════════════════════════════════════════════════════════"
echo -e "${NC}"
