# Halilit Support Center — Operator Console

JIT (Just-in-Time) product intelligence platform for musical instruments. Catalog + product graph from the Conductor pipeline; on-demand AI intelligence via Gemini 2.0 Flash.

**Workflow:** Dark Factory. Specs in `specs/` are the **input**; code is the **output**. The AI implements specs exactly. See [docs/](docs/) and `.cursorrules` (Dark Factory Protocol). Run the supervisor: `PYTHONPATH=. python3 backend/factory_supervisor.py [--rebuild]`.

---

## Quick Start

```bash
# First time: install
python3 -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
cd frontend && (pnpm install || npm install) && cd ..

# Run the app
./factory_reset.sh
```

- **Backend:** http://localhost:8000  
- **Frontend:** http://localhost:5173  

If you see "No catalog artifact found", run once: `./factory_reset.sh --rebuild`

Full steps: **[docs/QUICK_START.md](docs/QUICK_START.md)**

---

## Documentation

| Doc | Purpose |
|-----|---------|
| [docs/README.md](docs/README.md) | Index of all docs |
| [docs/QUICK_START.md](docs/QUICK_START.md) | Install and run |
| [docs/WORKFLOW.md](docs/WORKFLOW.md) | Spec-driven workflow, Level 5, Factory Owner |
| [docs/SPEC_DRIVEN_DEVELOPMENT.md](docs/SPEC_DRIVEN_DEVELOPMENT.md) | How to write specs and prompt the AI |
| [docs/FACTORY_PIPELINE.md](docs/FACTORY_PIPELINE.md) | Conductor commands, rebuild, validation |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System layers, API, Operator Console views |
| [OPERATOR_CONSOLE_SPEC.md](OPERATOR_CONSOLE_SPEC.md) | What the console must do; compliance |

Specs (source of truth for UI and data): **[specs/](specs/)**

---

## Tech Stack

- **Frontend:** React 18, TypeScript, Vite, Zustand, React Query, Tailwind
- **Backend:** Python 3.11+, FastAPI, Conductor CLI (ingest, sync, rebuild-catalog)
- **Data:** Catalog from `backend/data`; product graph (families, relationships); JIT per product

---

**Operator Console** · Spec-driven · [docs/](docs/)
