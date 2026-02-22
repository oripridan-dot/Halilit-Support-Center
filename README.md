# Halilit Support Center — Operator Console `v9.7.6 · Level 6`

JIT (Just-in-Time) product intelligence platform for musical instruments. Catalog + product graph from the Conductor pipeline; on-demand AI intelligence via Gemini 2.0 Flash.

**Architecture:** Algorithmic Biology — Dark Factory powered by DNA Genomes, Ribosome interpreter, and a Mutation Engine (Genetic Feedback Loop). Specs in `specs/genomes/` define organism fitness goals; the Ribosome generates Synthesis Directives; the Builder materialises code; the Mutation Engine evolves agent DNA via OODA cycles.

**Workflow:** Dark Factory. Specs in `specs/` are the **input**; code is the **output**. The AI implements specs exactly. See [docs/](docs/). Run the master controller: `python factory.py start`.

---

## Quick Start

```bash
# First time: install
python3 -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
cd frontend && (pnpm install || npm install) && cd ..

# Run the app (preferred — Master Factory Controller)
export GEMINI_API_KEY="your-key"
python factory.py start          # backend (8000) + frontend (5173)

# Or legacy
./factory_reset.sh
```

- **Backend:** http://localhost:8000
- **Frontend:** http://localhost:5173

If you see "No catalog artifact found", run once: `./factory_reset.sh --rebuild`

Full steps: **[docs/QUICK_START.md](docs/QUICK_START.md)**

---

## 🔌 TooLoo Integration — Autonomous AI Orchestrator

This repository is now connected to **TooLoo Core**, a repository-agnostic autonomous AI engine that can work on ANY client project. The **Umbilical Cord** pattern allows Halilit to leverage external AI intelligence without embedding TooLoo code.

### Usage

**Option 1: Use the launcher script (recommended)**
```bash
# Give TooLoo a mandate
./start-tooloo.sh "Implement the user dashboard component"

# View morning briefing without acting
./start-tooloo.sh "briefing"

# Dry-run: see plan without executing
./start-tooloo.sh --dry-run "Fix the catalog sync bug"
```

**Option 2: Direct invocation**
```bash
# Invoke TooLoo directly with --target pointing here
python /workspaces/tooloo-core/nexus.py --target . "Your mandate"

# Or relative to parent:
python ../tooloo-core/nexus.py --target . "Your mandate"
```

### How It Works

1. `.tooloo.config` — Configuration file that tells TooLoo how to operate on Halilit
2. `start-tooloo.sh` — Launcher that connects to the external TooLoo engine via the Umbilical Cord
3. **Nexus orchestrator** — Dispatches Swarm agents (Chief, TechLead, RepoAgent, Builder, Watchdog)
4. **Agents execute** — Code generation, testing, commits, documentation updates

### Architecture

- **TooLoo Core** (`/workspaces/tooloo-core/`) — Standalone AI orchestrator (pure logic, no client code)
- **Halilit** (this repo) — Client project with `.tooloo.config` pointing to TooLoo
- **Umbilical Cord** — `--target` CLI argument that makes TooLoo repository-agnostic

The separation means TooLoo can work on ANY repository—not just Halilit. See [.tooloo.config](.tooloo.config) for Halilit-specific settings.

---

## Documentation

| Doc                                                                | Purpose                                      |
| ------------------------------------------------------------------ | -------------------------------------------- |
| [docs/README.md](docs/README.md)                                   | Index of all docs                            |
| [docs/QUICK_START.md](docs/QUICK_START.md)                         | Install and run                              |
| [docs/WORKFLOW.md](docs/WORKFLOW.md)                               | Spec-driven workflow, Level 5, Factory Owner |
| [docs/SPEC_DRIVEN_DEVELOPMENT.md](docs/SPEC_DRIVEN_DEVELOPMENT.md) | How to write specs and prompt the AI         |
| [docs/FACTORY_PIPELINE.md](docs/FACTORY_PIPELINE.md)               | Conductor commands, rebuild, validation      |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)                       | System layers, API, Operator Console views   |
| [OPERATOR_CONSOLE_SPEC.md](OPERATOR_CONSOLE_SPEC.md)               | What the console must do; compliance         |

Specs (source of truth for UI and data): **[specs/](specs/)**

---

## Tech Stack

- **Frontend:** React 18, TypeScript, Vite, Zustand, React Query, Tailwind
- **Backend:** Python 3.11+, FastAPI, Conductor CLI (ingest, sync, rebuild-catalog)
- **Data:** Catalog from `backend/data`; product graph (families, relationships); JIT per product
- **AI:** Gemini 2.0 Flash (`gemini-2.0-flash`) via `google-genai`; Gemini 2.0 Flash Lite for fast ops

---

## Bio-Swarm — Algorithmic Biology (v9.7.4)

| Component           | File                                 | Purpose                                                                                                     |
| ------------------- | ------------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| **Genome specs**    | `specs/genomes/*.yaml`               | DNA — define States, Traits, Fitness goals, Phenotype Assertions                                            |
| **Ribosome**        | `backend/factory/ribosome.py`        | Genome interpreter — loads YAML, resolves `extends`, generates Synthesis Directives, runs PhenotypeVerifier |
| **Mutation Engine** | `backend/factory/mutation_engine.py` | OODA cycle — scans factory_logs, updates FitnessLedger, evolves agent DNA into `docs/LEARNED_GUIDELINES.md` |
| **OODA loop**       | `nexus.py`                           | Fires `_run_ooda_mutation_cycle()` automatically after every successful swarm batch                         |

```bash
# Genome workflow
python factory.py synthesize specs/genomes/product_explorer.yaml   # generate Synthesis Directive
python factory.py build specs/temp/synthesis_genome_*.md           # materialise code
python factory.py mutate                                            # run OODA mutation cycle
python factory.py fitness                                           # view FitnessLedger
```

Current VIABLE genomes: `base_cell`, `product_explorer` (100/100), `inventory_grid`

---

**Operator Console** · Spec-driven · Bio-Swarm v9.7.4 · [docs/](docs/)
