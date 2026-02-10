#!/bin/bash
#
# Startup Script for Halilit Support Center v8.2 Infrastructure
#
# Usage:
#   ./backend/scripts/setup_infrastructure.sh              # Full setup (Redis + PostgreSQL + Workers)
#   ./backend/scripts/setup_infrastructure.sh --services   # Only services (no workers)
#   ./backend/scripts/setup_infrastructure.sh --workers    # Only start workers
#   ./backend/scripts/setup_infrastructure.sh --stop       # Stop all services
#
# Requirements:
#   - Docker & Docker Compose
#   - Python 3.11+
#   - redis-cli (optional, for verification)

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🚀 Halilit Support Center v8.2 - Infrastructure Setup${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Parse arguments
SETUP_SERVICES=true
SETUP_WORKERS=false
STOP_SERVICES=false
SERVICES_ONLY=false
WORKERS_ONLY=false

for arg in "$@"; do
    case "$arg" in
        --services)
            SERVICES_ONLY=true
            SETUP_WORKERS=false
            ;;
        --workers)
            WORKERS_ONLY=true
            SETUP_SERVICES=false
            ;;
        --stop)
            STOP_SERVICES=true
            SETUP_SERVICES=false
            ;;
    esac
done

# Function to check command availability
check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo -e "${RED}❌ $1 not found${NC}"
        echo "   Install: $2"
        exit 1
    fi
    echo -e "${GREEN}✅ $1 available${NC}"
}

# Function to wait for service
wait_for_service() {
    local service=$1
    local timeout=${2:-30}
    local elapsed=0
    
    echo -e "${YELLOW}⏳ Waiting for $service...${NC}"
    
    while [ $elapsed -lt $timeout ]; do
        if "$3"; then
            echo -e "${GREEN}✅ $service is ready${NC}"
            return 0
        fi
        sleep 1
        elapsed=$((elapsed + 1))
    done
    
    echo -e "${RED}❌ Timeout waiting for $service${NC}"
    return 1
}

# Check if we need to stop
if [ "$STOP_SERVICES" = true ]; then
    echo -e "${YELLOW}🛑 Stopping services...${NC}"
    cd "$PROJECT_ROOT"
    docker-compose down
    echo -e "${GREEN}✅ Services stopped${NC}"
    exit 0
fi

# =========================================================================
# Phase 1: Check Prerequisites
# =========================================================================
if [ "$SETUP_SERVICES" = true ]; then
    echo -e "${YELLOW}📋 Checking prerequisites...${NC}"
    echo ""
    
    check_command "docker" "https://docs.docker.com/get-docker/"
    check_command "docker-compose" "https://docs.docker.com/compose/install/"
    
    echo ""
fi

# =========================================================================
# Phase 2: Start Docker Services
# =========================================================================
if [ "$SETUP_SERVICES" = true ] && [ "$WORKERS_ONLY" = false ]; then
    echo ""
    echo -e "${YELLOW}🐳 Starting Docker services (Redis, PostgreSQL, Flower)...${NC}"
    echo ""
    
    cd "$PROJECT_ROOT"
    
    # Check if .env exists, if not create from template
    if [ ! -f .env ]; then
        echo -e "${YELLOW}⚠️  .env not found, creating from .env.example${NC}"
        if [ -f .env.example ]; then
            cp .env.example .env
            echo -e "${GREEN}✅ Created .env (update with your values before running workers)${NC}"
        fi
    fi
    
    # Start services (detached)
    echo -e "${BLUE}docker-compose up -d redis postgres flower${NC}"
    docker-compose up -d redis postgres flower
    
    echo ""
    echo -e "${YELLOW}⏳ Waiting for services to be healthy...${NC}"
    
    # Wait for Redis
    wait_for_service "Redis" 30 "redis-cli -u redis://localhost:6379/0 ping &>/dev/null || docker exec halilit_redis redis-cli ping &>/dev/null"
    
    # Wait for PostgreSQL
    wait_for_service "PostgreSQL" 30 "docker exec halilit_postgres pg_isready -U halilit_user &>/dev/null || PGPASSWORD=secure_password_change_me psql -h localhost -U halilit_user -d halilit_tasks -c 'SELECT 1' &>/dev/null"
    
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ Services Started Successfully!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "📱 Service Endpoints:"
    echo "  • Redis:       redis://localhost:6379"
    echo "  • PostgreSQL:  postgresql://halilit_user@localhost:5432/halilit_tasks"
    echo "  • Flower:      http://localhost:5555 (admin / flower_password_change_me)"
    echo ""
fi

# =========================================================================
# Phase 3: Install Python Dependencies
# =========================================================================
if [ "$SERVICES_ONLY" = false ] || [ "$WORKERS_ONLY" = true ]; then
    echo ""
    echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"
    
    cd "$PROJECT_ROOT"
    
    if [ ! -d "venv" ]; then
        echo -e "${BLUE}Creating virtual environment...${NC}"
        python3 -m venv venv
    fi
    
    echo -e "${BLUE}Activating virtual environment...${NC}"
    source venv/bin/activate || . venv/Scripts/activate
    
    echo -e "${BLUE}Installing packages...${NC}"
    pip install -q -r backend/requirements.txt
    
    echo -e "${GREEN}✅ Dependencies installed${NC}"
    echo ""
fi

# =========================================================================
# Phase 4: Start Celery Workers
# =========================================================================
if [ "$SERVICES_ONLY" = false ]; then
    echo ""
    echo -e "${YELLOW}👷 Starting Celery Workers...${NC}"
    echo ""
    
    # Check if Redis is available first
    if command -v redis-cli &> /dev/null; then
        if ! redis-cli -u redis://localhost:6379/0 ping &>/dev/null; then
            echo -e "${RED}❌ Redis is not available${NC}"
            echo "   Start Redis with: docker-compose up -d redis"
            exit 1
        fi
    fi
    
    cd "$PROJECT_ROOT"
    
    # Source .env if it exists
    if [ -f .env ]; then
        set -a
        source .env
        set +a
    fi
    
    # Make scripts executable
    chmod +x backend/scripts/start_workers.sh
    
    # Execute the worker startup script
    exec bash backend/scripts/start_workers.sh
fi

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Update .env with your configuration"
echo "  2. Start workers: ./backend/scripts/start_workers.sh"
echo "  3. Start API: uvicorn backend.server:app --reload"
echo "  4. Monitor: http://localhost:5555 (Flower)"
echo ""
