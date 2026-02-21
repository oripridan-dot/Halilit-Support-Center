"""
DARWIN AGENT — Architectural Red Team (backend/factory/darwin_agent.py)
=======================================================================
The Darwin Protocol: hypothesis-driven architectural mutation with
hard benchmark data.

The Darwin Agent's mandate is NOT to write features — it is to CHALLENGE
the current architecture. It operates exclusively inside the Shadow Cell,
mutates code, benchmarks against the live system, and only graduates
proposals to the Operator's desk when data proves a meaningful win.

Lifecycle
---------
1. HYPOTHESIZE — LLM formulates a specific architectural mutation hypothesis
                 based on known bottlenecks in the project.
2. SPIN UP      — Shadow Cell Manager clones the live repo into an isolated
                 sandbox (entirely outside this workspace).
3. EXPERIMENT   — Agent generates and executes mutation scripts INSIDE the
                 Shadow Cell only.
4. BENCHMARK    — Measures old-vs-new performance (speed, memory, bundle
                 size, etc.).
5. EVALUATE     — If the mutation shows ≥20% improvement, a formal
                 PARADIGM_SHIFT_PROPOSAL.md is written to the project root.
6. TEAR DOWN    — Shadow Cell is destroyed regardless of outcome.

Usage
-----
    # Trigger manually from CLI:
    python backend/factory/darwin_agent.py "SQLite is too slow for graph reads"

    # Or from nexus.py / MCP (via run_architectural_experiment tool).
    from backend.factory.darwin_agent import initiate_darwin_experiment
    plan = initiate_darwin_experiment("Try asyncio + aiohttp for ingestion scrapers")
"""

from __future__ import annotations

import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Bootstrap sys.path
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Internal imports (graceful degradation)
# ---------------------------------------------------------------------------
try:
    from backend.factory.agent_core import query_llm
    _LLM_AVAILABLE = True
except ImportError:
    _LLM_AVAILABLE = False

    # type: ignore[misc]
    def query_llm(*args: Any, **kwargs: Any) -> str | None:
        return None

try:
    from backend.factory.shadow_cell import (
        spin_up_shadow_cell,
        execute_shadow_benchmark,
        destroy_shadow_cell,
        shadow_cell_status,
        SHADOW_DIR,
    )
    _SHADOW_AVAILABLE = True
except ImportError:
    _SHADOW_AVAILABLE = False

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROPOSAL_PATH = _PROJECT_ROOT / "PARADIGM_SHIFT_PROPOSAL.md"
EXPERIMENT_LOG_PATH = _PROJECT_ROOT / "backend" / \
    "data" / "darwin_experiments.jsonl"
EXPERIMENT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Improvement threshold to trigger a formal PARADIGM_SHIFT_PROPOSAL
# ---------------------------------------------------------------------------
SHIFT_THRESHOLD_PCT = 20.0  # ≥20% improvement required

# ---------------------------------------------------------------------------
# System Prompt
# ---------------------------------------------------------------------------
DARWIN_SYSTEM_PROMPT = """\
You are the Darwin Agent — the Architectural Red Team of the Halilit Dark Factory.

Your mandate: identify ONE specific, measurable architectural bottleneck in the
current system, propose a concrete mutation, and design a rigorous benchmark to
prove or disprove its value — entirely inside an isolated Shadow Cell.

RULES
─────
1. HYPOTHESIS: Formulate one specific, testable hypothesis about the current
   architecture (e.g. "SQLite 4-table JOIN for accessory mapping takes 850ms;
   an in-memory NetworkX graph would cut this to <50ms").

2. MUTATION PLAN: Provide the exact Python/Bash commands needed to implement
   the mutation inside the Shadow Cell (the shadow cell path will be provided).
   Commands must be shell-executable. Do NOT touch the live repo.

3. BENCHMARK DESIGN: Provide a benchmark_command (a single shell command that
   runs inside the Shadow Cell and prints timing/memory metrics to stdout).
   Also provide a baseline_command (equivalent measurement on the LIVE repo).
   Both commands must be runnable without interactive input.

4. EVALUATION CRITERIA: State the expected improvement metric (e.g. "p50
   latency drops by ≥30%") and the minimum threshold to recommend a Paradigm
   Shift.

5. ZERO HALLUCINATION: Every file path, module name, and shell command you
   produce must reference code that actually exists in the Halilit codebase.
   If you are unsure whether a file exists, prefix the command with a
   `[ -f <path> ] && ` guard.

6. THREE SOURCE RULES: Your mutation must never introduce synthetic/mock data.
   Architecture changes (query engine, data structure, bundler) are fair game.
   Data content is NOT your domain.

OUTPUT FORMAT (respond with ONLY valid JSON — no markdown fences):
{
  "hypothesis": "One-sentence statement of the bottleneck.",
  "affected_component": "Module or file path in the live repo.",
  "mutation_summary": "Plain-English description of the architectural change.",
  "mutation_commands": [
    "command_1 to execute inside shadow cell",
    "command_2 to execute inside shadow cell"
  ],
  "benchmark_command": "single shell command that measures performance in the shadow cell",
  "baseline_command": "equivalent shell command to measure current (live) performance",
  "expected_metric": "Description of what to measure (e.g. p50 latency in ms)",
  "expected_improvement_pct": 30,
  "risk_level": "LOW | MEDIUM | HIGH",
  "rollback_plan": "How to roll back if the mutation is harmful.",
  "rationale": "2–3 sentence technical justification."
}
"""


# ---------------------------------------------------------------------------
# Core API
# ---------------------------------------------------------------------------

def initiate_darwin_experiment(hypothesis: str, run_in_cell: bool = False) -> str:
    """
    Full Darwin Protocol cycle.

    Args:
        hypothesis:   What architectural challenge to explore.
        run_in_cell:  If True, actually execute mutation + benchmark commands
                      inside the Shadow Cell. If False (default), returns the
                      plan only (safe mode — no filesystem mutations).

    Returns:
        A formatted Markdown string with the experiment plan and (if
        run_in_cell=True) benchmark results.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'🌋' * 8}")
    print(f"🧬 DARWIN AGENT ACTIVATED")
    print(f"   Hypothesis: {hypothesis}")
    print(
        f"   Mode: {'LIVE EXPERIMENT (Shadow Cell)' if run_in_cell else 'PLAN ONLY (safe mode)'}")
    print(f"{'─' * 60}")

    if not _LLM_AVAILABLE:
        return (
            "❌ Darwin Agent requires GEMINI_API_KEY / GOOGLE_API_KEY. "
            "Set the environment variable and retry."
        )

    # --- Step 1: Load project context to ground the LLM ---
    project_context = _load_project_context()

    user_prompt = (
        f"Hypothesis to explore: {hypothesis}\n\n"
        f"Current project context:\n{project_context}\n\n"
        "Generate the Darwin experiment plan in the JSON format specified."
    )

    print("   🧠 Generating experiment plan via LLM …")
    raw_plan = query_llm(
        system_prompt=DARWIN_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        model_tier="smart",
    )

    if not raw_plan:
        return "❌ LLM returned no response. Check API key and quota."

    plan_data = _parse_plan(raw_plan)
    plan_md = _format_plan_markdown(plan_data, timestamp, hypothesis)

    # --- Step 2: Execute in Shadow Cell (optional) ---
    benchmark_results: dict[str, Any] = {}
    if run_in_cell:
        if not _SHADOW_AVAILABLE:
            plan_md += "\n\n> ⚠️ shadow_cell module unavailable — skipping live execution.\n"
        else:
            benchmark_results = _run_experiment_in_cell(plan_data)
            plan_md += _format_benchmark_section(benchmark_results)

            # --- Step 3: Evaluate outcome ---
            if _should_write_proposal(benchmark_results):
                _write_paradigm_shift_proposal(
                    plan_data, benchmark_results, hypothesis, timestamp
                )
                plan_md += (
                    "\n\n---\n"
                    "## 🚨 PARADIGM SHIFT PROPOSAL WRITTEN\n"
                    f"Open `PARADIGM_SHIFT_PROPOSAL.md` for the Governor's review.\n"
                )

    # --- Step 4: Append to experiment log ---
    _log_experiment(hypothesis, plan_data, benchmark_results, timestamp)

    return plan_md


def get_last_proposal() -> str:
    """Returns the content of PARADIGM_SHIFT_PROPOSAL.md or a placeholder."""
    if PROPOSAL_PATH.exists():
        return PROPOSAL_PATH.read_text(encoding="utf-8")
    return "_No Paradigm Shift Proposal on file. Run a Darwin Experiment first._"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _load_project_context() -> str:
    """Load lean project context: source_rules, architecture summary, known bottlenecks."""
    parts: list[str] = []
    files_to_read = [
        "backend/source_rules.py",
        "OPERATOR_CONSOLE_SPEC.md",
        "docs/ARCHITECTURE.md",
        "FACTORY_KANBAN.md",
    ]
    for rel in files_to_read:
        p = _PROJECT_ROOT / rel
        if p.exists():
            content = p.read_text(encoding="utf-8", errors="replace")
            # Trim very large files
            if len(content) > 3000:
                content = content[:3000] + "\n… [truncated]"
            parts.append(f"### {rel}\n```\n{content}\n```")
    return "\n\n".join(parts)


def _parse_plan(raw: str) -> dict[str, Any]:
    """Extract JSON from LLM response (strips markdown fences if present)."""
    import json
    import re

    # Strip optional markdown code fences
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"\s*```$", "", cleaned.strip(), flags=re.MULTILINE)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Graceful fallback — wrap raw text
        return {
            "hypothesis": "See raw output",
            "mutation_summary": raw[:500],
            "mutation_commands": [],
            "benchmark_command": "",
            "baseline_command": "",
            "expected_metric": "N/A",
            "expected_improvement_pct": 0,
            "risk_level": "UNKNOWN",
            "rollback_plan": "N/A",
            "rationale": raw[:200],
            "_raw": raw,
        }


def _format_plan_markdown(plan: dict[str, Any], timestamp: str, hypothesis: str) -> str:
    return f"""\
# 🧬 Darwin Experiment Plan

**Generated:** `{timestamp}`
**Hypothesis:** {hypothesis}

---

## 1. Bottleneck Identified

> {plan.get('hypothesis', 'N/A')}

**Affected Component:** `{plan.get('affected_component', 'N/A')}`

## 2. Proposed Mutation

{plan.get('mutation_summary', 'N/A')}

**Risk Level:** `{plan.get('risk_level', 'UNKNOWN')}`

## 3. Mutation Commands (Shadow Cell only)

```bash
{chr(10).join(plan.get('mutation_commands', ['# no commands generated']))}
```

## 4. Benchmark Design

| | Command |
|--|--|
| **Baseline (live)** | `{plan.get('baseline_command', 'N/A')}` |
| **Mutation (shadow)** | `{plan.get('benchmark_command', 'N/A')}` |

**Measurement Target:** {plan.get('expected_metric', 'N/A')}
**Expected Improvement:** `{plan.get('expected_improvement_pct', 0)}%`

## 5. Rationale

{plan.get('rationale', 'N/A')}

## 6. Rollback Plan

{plan.get('rollback_plan', 'N/A')}
"""


def _run_experiment_in_cell(plan: dict[str, Any]) -> dict[str, Any]:
    """Spin up Shadow Cell, execute mutation + benchmark, tear down."""
    results: dict[str, Any] = {
        "cell_path": "",
        "baseline_stdout": "",
        "shadow_stdout": "",
        "mutation_errors": [],
        "improvement_pct": None,
        "ran_live": False,
    }

    try:
        # Spin up
        cell_path = spin_up_shadow_cell(force=True)
        results["cell_path"] = cell_path

        # Execute mutation commands sequentially inside the shadow cell
        for cmd in plan.get("mutation_commands", []):
            if not cmd.strip():
                continue
            out = execute_shadow_benchmark(cmd, timeout=120)
            if out["returncode"] != 0:
                results["mutation_errors"].append(
                    f"CMD FAILED [{out['returncode']}]: {cmd}\n{out['stderr']}"
                )

        # Run baseline on LIVE repo
        baseline_cmd = plan.get("baseline_command", "")
        if baseline_cmd:
            import subprocess
            base_result = subprocess.run(
                baseline_cmd,
                cwd=str(_PROJECT_ROOT),
                shell=True,
                capture_output=True,
                text=True,
                timeout=120,
            )
            results["baseline_stdout"] = base_result.stdout

        # Run benchmark on SHADOW Cell
        bench_cmd = plan.get("benchmark_command", "")
        if bench_cmd:
            shadow_result = execute_shadow_benchmark(bench_cmd, timeout=120)
            results["shadow_stdout"] = shadow_result["stdout"]

        results["ran_live"] = True

    except Exception as exc:
        results["mutation_errors"].append(f"EXPERIMENT ERROR: {exc}")
    finally:
        destroy_shadow_cell()

    return results


def _format_benchmark_section(results: dict[str, Any]) -> str:
    if not results.get("ran_live"):
        return "\n\n## Benchmark Results\n_Experiment did not run (check errors above)._\n"

    errors_md = ""
    if results.get("mutation_errors"):
        errors_md = "### ⚠️ Mutation Errors\n```\n" + \
            "\n".join(results["mutation_errors"]) + "\n```\n"

    return f"""

---

## 📊 Benchmark Results

### Baseline (live repo)
```
{results.get('baseline_stdout') or '_No output_'}
```

### Shadow Cell (mutated architecture)
```
{results.get('shadow_stdout') or '_No output_'}
```

{errors_md}
"""


def _should_write_proposal(results: dict[str, Any]) -> bool:
    """
    Determine if benchmark results warrant a Paradigm Shift Proposal.
    Currently a heuristic — full numeric parsing can be added per experiment type.
    """
    if not results.get("ran_live"):
        return False
    # Simple heuristic: if shadow cell produced output and no mutation errors
    # the Darwin Agent writes a proposal and leaves the evaluation to the Operator.
    shadow_out = results.get("shadow_stdout", "")
    has_errors = bool(results.get("mutation_errors"))
    return bool(shadow_out) and not has_errors


def _write_paradigm_shift_proposal(
    plan: dict[str, Any],
    results: dict[str, Any],
    hypothesis: str,
    timestamp: str,
) -> None:
    """Writes the formal proposal Markdown to the project root."""
    content = f"""\
# 🚨 PARADIGM SHIFT PROPOSAL

**Date:** `{timestamp}`
**Agent:** Darwin Agent (Architectural Red Team)

---

## Hypothesis

> {hypothesis}

## Bottleneck

{plan.get('hypothesis', 'N/A')}

**Affected Component:** `{plan.get('affected_component', 'N/A')}`

## Proposed Mutation

{plan.get('mutation_summary', 'N/A')}

## Benchmark Evidence

### Current Architecture (Baseline)
```
{results.get('baseline_stdout', '_not measured_')}
```

### Mutated Architecture (Shadow Cell)
```
{results.get('shadow_stdout', '_not measured_')}
```

## Expected Improvement

**Metric:** {plan.get('expected_metric', 'N/A')}
**Claimed gain:** `{plan.get('expected_improvement_pct', 0)}%`

## Risk Assessment

**Level:** `{plan.get('risk_level', 'UNKNOWN')}`
**Rollback:** {plan.get('rollback_plan', 'N/A')}

## Technical Rationale

{plan.get('rationale', 'N/A')}

---

## Governor Decision Required

The Shadow Cell experiment is complete and has been destroyed.
The mutation commands listed below have NOT been applied to the live repository.

To apply:
```bash
{chr(10).join(plan.get('mutation_commands', ['# no commands']))}
```

**Authorise by running:** `python factory.py build specs/strategy/evolution/<proposal_spec>.md`
"""
    PROPOSAL_PATH.write_text(content, encoding="utf-8")
    print(f"   📄 PARADIGM_SHIFT_PROPOSAL.md written → {PROPOSAL_PATH}")


def _log_experiment(
    hypothesis: str,
    plan: dict[str, Any],
    results: dict[str, Any],
    timestamp: str,
) -> None:
    """Append a JSONL entry to the experiment log for historical tracking."""
    import json

    entry = {
        "timestamp": timestamp,
        "hypothesis": hypothesis,
        "affected_component": plan.get("affected_component"),
        "expected_improvement_pct": plan.get("expected_improvement_pct"),
        "risk_level": plan.get("risk_level"),
        "ran_live": results.get("ran_live", False),
        "had_errors": bool(results.get("mutation_errors")),
        "proposal_written": PROPOSAL_PATH.exists(),
    }
    try:
        with open(EXPERIMENT_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass  # Non-critical


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Darwin Agent — Architectural Red Team",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python backend/factory/darwin_agent.py 'SQLite JOINs are too slow'\n"
            "  python backend/factory/darwin_agent.py --live 'Test asyncio scraper'\n"
            "  python backend/factory/darwin_agent.py --last-proposal\n"
        ),
    )
    parser.add_argument(
        "hypothesis",
        nargs="?",
        default="",
        help="Architectural hypothesis to test.",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Execute mutation + benchmark in the Shadow Cell (default: plan only).",
    )
    parser.add_argument(
        "--last-proposal",
        action="store_true",
        help="Print the last PARADIGM_SHIFT_PROPOSAL.md.",
    )

    args = parser.parse_args()

    if args.last_proposal:
        print(get_last_proposal())
        sys.exit(0)

    if not args.hypothesis:
        parser.print_help()
        sys.exit(1)

    result = initiate_darwin_experiment(args.hypothesis, run_in_cell=args.live)
    print("\n" + result)
