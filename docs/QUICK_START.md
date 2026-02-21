# Quick Start — Halilit Support Center (v9.7.6)

---

## Prerequisites

- Python 3.11+, Node.js 18+, pnpm
- `GEMINI_API_KEY` (or `GOOGLE_API_KEY`) — required for intelligence features

```bash
export GEMINI_API_KEY="your-key-here"
```

---

## One-Command Launch (Recommended)

```bash
source .venv/bin/activate
python factory.py start
```

This starts:
- **Backend** (FastAPI) on http://localhost:8000
- **Frontend** (Vite) on http://localhost:5173

---

## First-Time Setup

```bash
# 1. Clone and enter the repo
git clone <repo-url>
cd Halilit-Support-Center

# 2. Create Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install Python dependencies
pip install -r backend/requirements.txt

# 4. Install frontend dependencies
cd frontend && pnpm install && cd ..

# 5. Set your Gemini API key
export GEMINI_API_KEY="your-key-here"

# 6. Check system status
python factory.py status

# 7. Launch
python factory.py start
```

---

## Alternative Launch Methods

```bash
# Legacy / direct
PYTHONPATH=. python backend/conductor_main.py dev   # Backend + frontend
PYTHONPATH=. python backend/server.py               # Backend only (port 8000)
cd frontend && pnpm dev                             # Frontend only (port 5173)

# Force rebuild catalog cache
python factory.py start --rebuild
```

---

## Interactive AI Console (Nexus)

```bash
source .venv/bin/activate
python nexus.py
```

Connects you to the full AI swarm: Chief, Builder, Tech Lead, Product Manager, Darwin, Sonar.

---

## Build a Feature (Spec-Driven)

```bash
# 1. Generate a spec (Architect Agent)
python factory.py design "Add price history chart to ProductDetail"

# 2. Materialise spec → code (Builder Agent + Tech Lead review)
python factory.py build specs/interface/<generated-spec>.md

# 3. Verify in browser → amend spec if needed → repeat
```

---

## Diagnose & Heal

```bash
python factory.py diagnose    # Scan errors, no changes
python factory.py heal        # Auto-repair errors (up to 3 cycles)
```

---

## Commit

```bash
python factory.py commit      # Stage all changes + semantic git commit
```

---

## Key URLs

| URL | Purpose |
|-----|---------|
| http://localhost:5173 | Operator Console (React SPA) |
| http://localhost:8000/docs | FastAPI Swagger UI |
| http://localhost:8000/api/health | Liveness check |
| http://localhost:8000/api/health/deep | Deep organ check |
| http://localhost:8000/api/conductor/catalog | Product catalog JSON |
