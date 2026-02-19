# 🚀 COPILOT INSTRUCTION GUIDE: The Path to Level 5 Autonomy

## Context for Copilot

You are upgrading the "Dark Factory" — a massively parallel, AI-driven software swarm managed by
`nexus.py` and planned by `backend/factory/chief_agent.py`. Currently, the system is at **Level 4**
(Parallel Execution + Shared Context via `specs/strategy/master_plan.md` — the Spine). The Chief
already reads the Master Plan on every cycle via `get_project_state()`, giving every agent a
globally consistent vocabulary and Table of Contents.

Your objective is to upgrade the factory to **Level 5 (Autonomous Self-Correcting Systems)**. This
requires implementing Agentic TDD, strict API contract enforcement, and Vector-Hydrated Memory.

Execute the following phases strictly in order. Do not proceed to the next phase until the current
one is tested and committed.

---

## Architecture Context (The Librarian Model)

The system uses a three-level Hierarchical Library:

| Level                 | Asset                                                        | Purpose                                                                                  |
| --------------------- | ------------------------------------------------------------ | ---------------------------------------------------------------------------------------- |
| **1 — The Spine**     | `specs/strategy/master_plan.md`                              | Ubiquitous Language, Business Goals, Table of Contents. Injected into every Chief cycle. |
| **2 — The Chapters**  | `specs/interface/`, `specs/data_pipeline/`, `specs/01_data/` | Domain specs — one per feature/domain. Builders read only the relevant chapter.          |
| **3 — The Librarian** | `backend/factory/chief_agent.py`                             | Reads the Spine; dynamically routes agents to the exact chapters they need, no more.     |

**The Spine is Law.** If a feature request conflicts with `master_plan.md`, the Chief must refuse or
flag it before scheduling any implementation tasks.

---

## Phase 1: Agentic Test-Driven Development (TDD)

**Goal:** Agents must write tests _before_ implementation. The Watchdog must run actual test files —
not just syntax checks — and loop the Builder back in on failure.

### Step 1.1: Upgrade the Watchdog Agent

- **File:** `backend/factory/watchdog_agent.py` (or the equivalent Watchdog implementation in `nexus.py`)
- **Action:** Extend the Watchdog to detect and execute test suites, not just compilation.
- **Logic:**
  - If `backend/tests/test_*.py` files exist → run `pytest` and capture stdout/stderr.
  - If `frontend/tests/**/*.test.ts` files exist → run `pnpm test --run` (Vitest) or `playwright test`.
  - If tests fail, capture the exact failure output and pass it back to the Chief as a
    `FAILURE REPORT` so it queues a `heal` cycle targeting the specific failing file.
  - **Never mark a task as SUCCESS if tests are failing.**

### Step 1.2: Upgrade the Chief's Planning Logic

- **File:** `backend/factory/chief_agent.py` — update `SYSTEM_PROMPT`
- **Action:** Prepend a `design (test)` task before every `implement` task for new features.
- **Logic:** The Chief must treat test-writing as a first-class task, not an afterthought.
  - Queue order for new features: `design (spec)` → `design (test file)` → `implement` → `watchdog (run tests)`.
  - For bug fixes: `heal` → `reflect` (existing pattern is correct).

---

## Phase 2: Strict API Contract Enforcement

**Goal:** Prevent frontend/backend integration bugs by forcing the `steerer` agent to publish a
binding API contract before any Builder writes integration code.

### Step 2.1: Define the Contract Tool

- **File:** `backend/factory/steerer_agent.py`
- **Action:** When the Steerer operates inside a `task_force`, its _only_ deliverable is a strict
  API contract file saved to `specs/contracts/<feature_name>.schema.ts` (TypeScript) or
  `specs/contracts/<feature_name>.openapi.json`.
- **Logic:**
  - The contract must define: endpoint path, HTTP method, request body type, response type.
  - The Steerer must emit this file before any Builder task is queued.
  - Example output: `specs/contracts/jit_intelligence.schema.ts`

### Step 2.2: Enforce Contracts on Builders

- **File:** `backend/factory/builder_agent.py` — update context-gathering preamble
- **Action:** Before writing or editing any file that involves an API call, the Builder must scan
  `specs/contracts/` for a matching contract.
- **Logic:**
  - If a contract exists for the domain → load it and strictly follow its types/endpoints.
  - If the Builder deviates, the Phase 1 Watchdog tests will catch it.
  - Add this scan to `context_discovery.py` if a common context-gathering module exists.

---

## Phase 3: Vector-Hydrated Lore (RAG for Agents)

**Goal:** `docs/LEARNED_GUIDELINES.md` will exceed useful context-window size as it grows. We need
to inject only _relevant_ past lessons — not the entire file — into each agent's prompt.

### Step 3.1: Implement Semantic Lore Retrieval

- **File:** `backend/factory/agent_core.py`
- **Action:** Add `get_relevant_lore(task_description: str) -> str`.
- **Logic (using Gemini Embedding API — already available via `google-genai`):**

```python
import json
from pathlib import Path
import google.generativeai as genai

LEARNED_GUIDELINES_PATH = Path(__file__).resolve().parent.parent.parent / "docs" / "LEARNED_GUIDELINES.md"
_LORE_CACHE: list[dict] | None = None   # { "chunk": str, "embedding": list[float] }

def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = sum(x**2 for x in a) ** 0.5
    mag_b = sum(x**2 for x in b) ** 0.5
    return dot / (mag_a * mag_b + 1e-9)

def get_relevant_lore(task_description: str, top_k: int = 3) -> str:
    """Return the top_k most relevant lessons from LEARNED_GUIDELINES.md."""
    global _LORE_CACHE
    text = LEARNED_GUIDELINES_PATH.read_text(encoding="utf-8") if LEARNED_GUIDELINES_PATH.exists() else ""
    if not text.strip():
        return ""

    # Chunk by H2/H3 headings or double newlines (whichever is finer)
    chunks = [c.strip() for c in text.split("\n\n") if len(c.strip()) > 40]

    if _LORE_CACHE is None or len(_LORE_CACHE) != len(chunks):
        embeddings = [
            genai.embed_content(model="models/text-embedding-004", content=c)["embedding"]
            for c in chunks
        ]
        _LORE_CACHE = [{"chunk": c, "embedding": e} for c, e in zip(chunks, embeddings)]

    query_emb = genai.embed_content(model="models/text-embedding-004", content=task_description)["embedding"]
    scored = sorted(_LORE_CACHE, key=lambda x: _cosine(query_emb, x["embedding"]), reverse=True)
    return "\n\n---\n\n".join(item["chunk"] for item in scored[:top_k])
```

### Step 3.2: Hydrate Builder and Watchdog Prompts

- **Files:** `backend/factory/builder_agent.py`, `backend/factory/watchdog_agent.py`
- **Action:** Call `get_relevant_lore(task_description)` at the start of each agent execution and
  prepend the result to the agent's system prompt under a `## RELEVANT PAST LESSONS` header.
- **Why:** Only semantically relevant lessons are injected — not the whole history — keeping token
  cost low while preventing repeated mistakes.

---

## Phase 4: The Closed-Loop Swarm (Autonomous Mode)

**Goal:** Allow the swarm to execute a full queue without the Operator confirming every batch.
Human oversight kicks in only on hard, repeated failure.

### Step 4.1: Add Auto-Pilot to Nexus

- **File:** `nexus.py`
- **Action:** Add an `--auto` CLI flag.
- **Logic:**
  - `python nexus.py --auto` bypasses the `input("Authorize Swarm? [Y/n]")` prompt.
  - The swarm executes the full queue automatically.
  - On task failure → feed the failure report back to the Chief for a recovery plan and execute it.
  - **Kill Switch:** If the same task fails **3 times in a row**, halt and request human intervention
    with a clear summary of what failed and why. Log to `factory_logs/autopilot_halt.log`.

### Step 4.2: Add a Dry-Run Mode

- **File:** `nexus.py`
- **Action:** Add a `--dry-run` flag that prints the full queue plan without executing anything.
- **Why:** Allows the Operator to audit the Chief's plan before committing to an auto-pilot run.

---

## Acceptance Criteria for Level 5

The factory is considered at Level 5 when:

- [ ] `nexus.py --auto` can execute a complete feature request end-to-end (spec → test → implement → verify → commit) without human prompts.
- [ ] A failing Playwright or Pytest test causes the Watchdog to loop — not pass.
- [ ] The Builder references `specs/contracts/` before writing any API-boundary code.
- [ ] `get_relevant_lore()` returns targeted lessons in < 500 ms using cached embeddings.
- [ ] The auto-pilot halts and notifies the Operator after 3 consecutive failures on the same task.

---

## Glossary (Ubiquitous Language)

| Term              | Definition                                                                                           |
| ----------------- | ---------------------------------------------------------------------------------------------------- |
| **The Spine**     | `specs/strategy/master_plan.md` — injected into every Chief cycle as global context.                 |
| **The Librarian** | The Chief Agent's role: reads the Spine, routes Builders to specific Chapters only.                  |
| **The Chapter**   | Any single spec file in `specs/` — the atomic unit of product knowledge.                             |
| **Contract**      | A TypeScript schema or OpenAPI JSON file in `specs/contracts/` defining a frontend↔backend boundary. |
| **Lore**          | Past lessons in `docs/LEARNED_GUIDELINES.md`, retrieved semantically via embeddings.                 |
| **Kill Switch**   | The 3-failure halt in auto-pilot mode that returns control to the Operator.                          |
| **Level 4**       | Current state: Parallel swarm execution + shared Spine context.                                      |
| **Level 5**       | Target state: Autonomous self-correcting loops — tests drive implementation, not the reverse.        |

---

_Copilot: Start with Phase 1.1. Read `nexus.py` and the existing Watchdog implementation to understand the current test-execution surface before proposing changes._
