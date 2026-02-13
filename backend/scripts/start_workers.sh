#!/bin/bash
#
# Start Celery Workers Locally (Development)
#
# Usage:
#   ./backend/scripts/start_workers.sh
#   ./backend/scripts/start_workers.sh --debug
#   ./backend/scripts/start_workers.sh --single-worker
#
# Environment:
#   CELERY_BROKER_URL - Redis broker URL (default: redis://localhost:6379/0)
#   CELERY_RESULT_BACKEND - Result backend URL (default: redis://localhost:6379/1)

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Configuration
BROKER_URL="${CELERY_BROKER_URL:-redis://localhost:6379/0}"
RESULT_BACKEND="${CELERY_RESULT_BACKEND:-redis://localhost:6379/1}"
LOG_LEVEL="${LOG_LEVEL:-info}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🚀 Halilit Support Center v8.5 - Celery Worker Startup${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Parse arguments
SINGLE_WORKER=false
DEBUG=false

for arg in "$@"; do
    case "$arg" in
        --single-worker)
            SINGLE_WORKER=true
            ;;
        --debug)
            DEBUG=true
            LOG_LEVEL="debug"
            ;;
    esac
done

# Check Redis connectivity
echo -e "${YELLOW}🔍 Checking Redis connectivity...${NC}"
if ! redis-cli -u "$BROKER_URL" ping &>/dev/null; then
    echo -e "${RED}❌ Redis not available at $BROKER_URL${NC}"
    echo "   Start Redis with: docker-compose up redis"
    exit 1
fi
echo -e "${GREEN}✅ Redis is available${NC}"
echo ""

# Check Python environment
echo -e "${YELLOW}🐍 Checking Python environment...${NC}"
cd "$PROJECT_ROOT"
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
python3 -c "import backend.tasks; print('✅ Tasks module loadable')" || {
    echo -e "${RED}❌ Cannot load tasks module${NC}"
    echo "   Install dependencies: pip install -r backend/requirements.txt"
    exit 1
}
echo ""

# Start workers based on mode
if [ "$SINGLE_WORKER" = true ]; then
    echo -e "${YELLOW}🎯 Starting SINGLE combined worker (all queues)...${NC}"
    echo -e "${BLUE}Worker PID: $$${NC}"
    echo ""
    
    celery -A backend.tasks worker \
        --loglevel="$LOG_LEVEL" \
        --concurrency=4 \
        --queues=harvest,enrich,validate,learn,feedback,default \
        --time-limit=3600 \
        --soft-time-limit=3400 \
        --max-tasks-per-child=100 \
        -n combined_worker@%h
else
    echo -e "${YELLOW}🎯 Starting SPECIALIZED workers (separate processes)...${NC}"
    echo ""
    
    # Create a temporary directory for PIDs
    TMPDIR=$(mktemp -d)
    trap "rm -rf $TMPDIR; kill $(jobs -p) 2>/dev/null || true" EXIT
    
    # Function to start a worker
    start_worker() {
        local queue=$1
        local concurrency=$2
        local name=$3
        
        echo -e "${BLUE}📦 Starting $name worker (concurrency=$concurrency)...${NC}"
        
        celery -A backend.tasks worker \
            --loglevel="$LOG_LEVEL" \
            --concurrency="$concurrency" \
            --queues="$queue" \
            --time-limit=3600 \
            --soft-time-limit=3400 \
            --max-tasks-per-child=100 \
            -n "${queue}_worker@%h" \
            > "$TMPDIR/${queue}.log" 2>&1 &
        
        echo $! > "$TMPDIR/${queue}.pid"
        echo -e "${GREEN}✅ $name worker started (PID: $(cat $TMPDIR/${queue}.pid))${NC}"
    }
    
    # Start specialized workers
    start_worker "harvest" "2" "🌾 HARVEST (CommercialScout)"
    start_worker "enrich" "3" "📖 ENRICH (OfficialVerifier)"
    start_worker "validate" "2" "🔍 VALIDATE (ExternalValidator)"
    start_worker "learn" "1" "📚 LEARN (Learning System)"
    
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ All workers started! Monitoring...${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "🔗 Celery Flower (monitoring): http://localhost:5555"
    echo "📊 Broker: $BROKER_URL"
    echo ""
    echo "Press Ctrl+C to stop all workers..."
    echo ""
    
    # Monitor workers
    wait
fi
