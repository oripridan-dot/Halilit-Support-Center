"""
MUTATION ENGINE — Genetic Feedback Loop  (backend/factory/mutation_engine.py)
==============================================================================
The Mutation Engine is the evolutionary core of the Bio-Swarm architecture.

After every Nexus swarm execution, this engine:
  1. OBSERVE  — scans factory_logs/ for success/failure events
  2. ORIENT   — calculates per-agent Fitness Scores (0.0–1.0)
  3. DECIDE   — if fitness drops below threshold, triggers a mutation
  4. ACT      — writes mutation to LEARNED_GUIDELINES.md or patches
                agent SYSTEM_PROMPT directly

Fitness is persisted in backend/data/genome/fitness_ledger.json so the
system accumulates telemetry across every single execution.

Biological analogy:
  Each agent is an organism. Its DNA is its SYSTEM_PROMPT.
  When it fails repeatedly, the tech_lead_agent diagnoses WHY and
  permanently splices a new heuristic into the organism's DNA.

Usage:
  python mutation_engine.py                      # Analyse latest run
  python mutation_engine.py --force-mutate       # Skip threshold check, always mutate
  python mutation_engine.py --report             # Print fitness ledger, no mutations

Or import:
  from mutation_engine import run_mutation_cycle, FitnessLedger
"""

from __future__ import annotations

import re
import sys
import json
import time
import argparse
import textwrap
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import Optional

# ── Project root ─────────────────────────────────────────────────────────────
_ROOT = Path(__file__).resolve().parent.parent.parent
_FACTORY_LOGS = _ROOT / "factory_logs"
_GUIDELINES = _ROOT / "docs" / "LEARNED_GUIDELINES.md"
_LEDGER_PATH = _ROOT / "backend" / "data" / "genome" / "fitness_ledger.json"
_BUILDER_PATH = _ROOT / "backend" / "factory" / "builder_agent.py"

# Fitness threshold below which a mutation is triggered
MUTATION_THRESHOLD = 0.65

# Bootstrap agent_core
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from agent_core import query_llm, SMART_MODEL
except ImportError:
    def query_llm(system, user, model=None):  # type: ignore[misc]
        raise RuntimeError("agent_core not available")
    SMART_MODEL = "gemini-2.0-flash"


# ═══════════════════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class AgentRun:
    """A single agent task execution recorded from factory_logs."""
    agent:     str
    tool:      str
    args:      str
    success:   bool
    duration:  float
    error:     str
    timestamp: str


@dataclass
class AgentFitness:
    """Running fitness statistics for one agent type."""
    agent:            str
    total_runs:       int = 0
    successful_runs:  int = 0
    failed_runs:      int = 0
    consecutive_failures: int = 0
    score:            float = 1.0          # 0.0–1.0
    last_error:       str = ""
    last_updated:     str = ""
    mutation_count:   int = 0
    generation:       int = 1            # increments with each mutation

    def update(self, run: AgentRun) -> None:
        self.total_runs += 1
        self.last_updated = datetime.now(timezone.utc).isoformat()

        if run.success:
            self.successful_runs += 1
            # Exponential recovery: each success moves score towards 1.0
            self.score = min(1.0, self.score + 0.05 * (1.0 - self.score))
            self.consecutive_failures = 0
        else:
            self.failed_runs += 1
            self.consecutive_failures += 1
            self.last_error = run.error[:500]
            # Exponential decay on failures
            self.score = max(0.0, self.score - 0.15 * self.score - 0.05)

        # Clamp
        self.score = round(max(0.0, min(1.0, self.score)), 4)

    @property
    def needs_mutation(self) -> bool:
        return self.score < MUTATION_THRESHOLD or self.consecutive_failures >= 3


# ═══════════════════════════════════════════════════════════════════════════
# FITNESS LEDGER  (persisted JSON)
# ═══════════════════════════════════════════════════════════════════════════

class FitnessLedger:
    """
    Persistent store of Fitness scores.
    Backed by backend/data/genome/fitness_ledger.json.
    """

    def __init__(self) -> None:
        self._data: dict[str, AgentFitness] = {}
        self._load()

    def _load(self) -> None:
        if _LEDGER_PATH.exists():
            try:
                raw = json.loads(_LEDGER_PATH.read_text(encoding="utf-8"))
                for agent, blob in raw.items():
                    af = AgentFitness(agent=agent, **{
                        k: v for k, v in blob.items() if k != "agent"
                    })
                    self._data[agent] = af
            except Exception:
                self._data = {}

    def save(self) -> None:
        _LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
        out = {agent: asdict(af) for agent, af in self._data.items()}
        _LEDGER_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")

    def get(self, agent: str) -> AgentFitness:
        if agent not in self._data:
            self._data[agent] = AgentFitness(agent=agent)
        return self._data[agent]

    def all_agents(self) -> list[AgentFitness]:
        return sorted(self._data.values(), key=lambda a: a.score)

    def record(self, run: AgentRun) -> AgentFitness:
        af = self.get(run.agent)
        af.update(run)
        return af

    def report(self) -> str:
        lines = ["# Fitness Ledger Report",
                 f"Generated: {datetime.now().isoformat()}", ""]
        for af in sorted(self._data.values(), key=lambda a: a.score):
            bar = "█" * int(af.score * 20) + "░" * (20 - int(af.score * 20))
            lines.append(
                f"  {af.agent:<20s} [{bar}] {af.score:.2f}  "
                f"runs={af.total_runs} ok={af.successful_runs} fail={af.failed_runs}  "
                f"gen={af.generation}  mut={af.mutation_count}"
            )
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════
# LOG PARSER
# ═══════════════════════════════════════════════════════════════════════════

# Patterns for parsing nexus/factory_logs output
_SUCCESS_RE = re.compile(
    r"✅\s+\[([A-Z_]+)\s*(.*?)\]\s+\((\d+\.?\d*)s\)", re.IGNORECASE)
_FAILURE_RE = re.compile(r"❌\s+\[([A-Z_]+)\s*(.*?)\]", re.IGNORECASE)
_ERROR_RE = re.compile(
    r"(?:Error|error|FAILED|failed|Exception|exception)[\s:]+(.+)")

# Map tool names → logical agent names
_TOOL_AGENT_MAP = {
    "implement":   "builder",
    "build":       "builder",
    "sandbox":     "builder",
    "heal":        "watchdog",
    "diagnose":    "watchdog",
    "ui_validate": "ui_validator",
    "design":      "architect",
    "steer":       "strategist",
    "doc":         "scribe",
    "optimize":    "optimizer",
    "commit":      "repo_agent",
    "reflect":     "mentor",
    "task_force":  "task_force",
    "scout":       "scout",
    "synthesize":  "ribosome",
}


def _parse_log_file(path: Path) -> list[AgentRun]:
    """Extract AgentRun records from a single factory log file."""
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    runs: list[AgentRun] = []
    ts = datetime.fromtimestamp(
        path.stat().st_mtime, tz=timezone.utc).isoformat()
    error_buf = ""

    for i, line in enumerate(lines):
        # Collect error context
        em = _ERROR_RE.search(line)
        if em:
            error_buf = em.group(1)[:400]

        sm = _SUCCESS_RE.search(line)
        if sm:
            tool = sm.group(1).lower().strip()
            args = sm.group(2).strip()
            dur = float(sm.group(3))
            agent = _TOOL_AGENT_MAP.get(tool, tool)
            runs.append(AgentRun(
                agent=agent, tool=tool, args=args,
                success=True, duration=dur, error="", timestamp=ts,
            ))
            error_buf = ""
            continue

        fm = _FAILURE_RE.search(line)
        if fm:
            tool = fm.group(1).lower().strip()
            args = fm.group(2).strip()
            agent = _TOOL_AGENT_MAP.get(tool, tool)
            # Collect error from next few lines
            extra = " | ".join(lines[i + 1: i + 5])
            runs.append(AgentRun(
                agent=agent, tool=tool, args=args,
                success=False, duration=0.0,
                error=(error_buf or extra)[:500], timestamp=ts,
            ))
            error_buf = ""

    return runs


def collect_runs_since(since_ts: float | None = None) -> list[AgentRun]:
    """
    Scan factory_logs/ for all log files modified after since_ts (epoch).
    Returns a flat list of AgentRun records.
    """
    if not _FACTORY_LOGS.exists():
        return []

    all_runs: list[AgentRun] = []
    for log_file in _FACTORY_LOGS.glob("*.log"):
        if since_ts and log_file.stat().st_mtime < since_ts:
            continue
        try:
            runs = _parse_log_file(log_file)
            all_runs.extend(runs)
        except Exception:
            pass
    return all_runs


# ═══════════════════════════════════════════════════════════════════════════
# MUTATION GENERATOR
# ═══════════════════════════════════════════════════════════════════════════

_MUTATION_SYSTEM_PROMPT = """\
You are THE MUTATION ENGINE (Level 9 — Genetic Architect).

Your role: analyze agent failure patterns and generate ONE permanent micro-heuristic
to splice into the agent's DNA (SYSTEM_PROMPT or LEARNED_GUIDELINES.md).

A micro-heuristic is an imperative rule (NEVER/ALWAYS/PREFER/AVOID/ENSURE) that,
if the agent had known it on the failed run, would have prevented the failure.

OUTPUT FORMAT (return ONLY this block, no markdown fences, no extra text):

### [{today}] Mutation — {agent_name} Gen {generation}
**Fitness Score:** {score:.2f} (dropped below {threshold:.2f})
**Consecutive Failures:** {consecutive_failures}
**Root Pattern:** <one sentence — what class of error recurred>
**Micro-Heuristic:** <imperative rule. Start with NEVER/ALWAYS/PREFER/AVOID/ENSURE.>
**Injection Target:** GUIDELINES | SYSTEM_PROMPT
**Confidence:** HIGH | MEDIUM | LOW
**Rationale:** <one sentence explaining why this mutation prevents the failure class>
"""

_GUIDELINES_INJECTION_PROMPT = """\
You are THE MUTATION ENGINE.

Given the micro-heuristic below, craft a full LEARNED_GUIDELINES.md entry in
the exact format already used in that file, referencing today's date ({today}).

Micro-heuristic block:
{micro_block}

Existing guidelines (do not duplicate):
{existing_guidelines}

Return ONLY the new guideline entry block (no markdown fences, no preamble).
"""

_SYSTEM_PROMPT_PATCH_PROMPT = """\
You are THE MUTATION ENGINE splicing a new rule into a Builder Agent SYSTEM_PROMPT.

Current SYSTEM_PROMPT (excerpt):
{current_prompt}

New micro-heuristic to splice in:
{micro_heuristic}

RULES:
- Insert the heuristic as a new numbered rule at the END of the RULES section.
- Return ONLY the complete updated SYSTEM_PROMPT string without any surrounding text,
  explanation, or markdown fences.
- Do NOT change any existing rules. Only append the new one.
"""


@dataclass
class MutationResult:
    agent:        str
    mutated:      bool
    target:       str          # "GUIDELINES" or "SYSTEM_PROMPT"
    heuristic:    str
    confidence:   str
    score_before: float
    score_after:  float
    generation:   int


def generate_mutation(
    af: AgentFitness,
    runs: list[AgentRun],
) -> MutationResult | None:
    """
    Given an under-performing AgentFitness and its recent runs,
    generate a mutation and apply it.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    failure_runs = [r for r in runs if not r.success and r.agent == af.agent]

    if not failure_runs:
        return None

    # Build failure context
    failure_context = "\n".join(
        f"- Tool: {r.tool}  Args: {r.args}\n  Error: {r.error}"
        for r in failure_runs[-5:]  # last 5 failures
    )

    system = _MUTATION_SYSTEM_PROMPT.format(
        today=today,
        agent_name=af.agent,
        generation=af.generation + 1,
        score=af.score,
        threshold=MUTATION_THRESHOLD,
        consecutive_failures=af.consecutive_failures,
    )
    user_prompt = textwrap.dedent(f"""\
        AGENT: {af.agent}
        CURRENT FITNESS: {af.score:.2f}
        CONSECUTIVE FAILURES: {af.consecutive_failures}
        LAST ERROR: {af.last_error}

        RECENT FAILURE RUNS (last 5):
        {failure_context}

        Generate the mutation micro-heuristic now.
    """)

    micro_block = query_llm(system, user_prompt, model_tier="smart")

    # Determine injection target
    target = "SYSTEM_PROMPT" if "SYSTEM_PROMPT" in micro_block else "GUIDELINES"
    confidence = "HIGH"
    if "MEDIUM" in micro_block:
        confidence = "MEDIUM"
    elif "LOW" in micro_block:
        confidence = "LOW"

    # Extract the micro-heuristic line
    heuristic = ""
    for line in micro_block.splitlines():
        if any(line.strip().startswith(w) for w in ("NEVER", "ALWAYS", "PREFER", "AVOID", "ENSURE")):
            heuristic = line.strip()
            break
    if not heuristic:
        heuristic = micro_block[:300]

    # Get score before mutation
    score_before = af.score

    # Apply mutation
    if target == "GUIDELINES":
        _inject_to_guidelines(micro_block, heuristic, today)
    else:
        _splice_into_system_prompt(af.agent, heuristic)

    # Update fitness record
    af.mutation_count += 1
    af.generation += 1

    return MutationResult(
        agent=af.agent,
        mutated=True,
        target=target,
        heuristic=heuristic,
        confidence=confidence,
        score_before=score_before,
        score_after=af.score,
        generation=af.generation,
    )


def _inject_to_guidelines(micro_block: str, heuristic: str, today: str) -> None:
    """Append a properly formatted entry to LEARNED_GUIDELINES.md."""
    existing = _GUIDELINES.read_text(
        encoding="utf-8") if _GUIDELINES.exists() else ""

    system = _GUIDELINES_INJECTION_PROMPT.format(
        today=today,
        micro_block=micro_block,
        existing_guidelines=existing[-3000:],
    )
    new_entry = query_llm(
        system, "Generate the guidelines entry now.", model_tier="smart")

    # Ensure the entry is clean
    new_entry = new_entry.strip()
    if not new_entry.startswith("###"):
        new_entry = f"### [{today}] Mutation — Auto-Generated\n{new_entry}"

    # Append
    _GUIDELINES.parent.mkdir(parents=True, exist_ok=True)
    with _GUIDELINES.open("a", encoding="utf-8") as fh:
        fh.write(f"\n\n{new_entry}\n")

    print(f"   🧬 Mutation injected → docs/LEARNED_GUIDELINES.md")


def _splice_into_system_prompt(agent_name: str, heuristic: str) -> None:
    """
    Splice a micro-heuristic into the builder_agent.py SYSTEM_PROMPT.
    Only acts on the builder agent (highest-impact organism).
    Safe-guard: never touches other agent files without explicit target mapping.
    """
    agent_file_map = {
        "builder":    _BUILDER_PATH,
    }
    target_file = agent_file_map.get(agent_name)
    if not target_file or not target_file.exists():
        # Fallback: inject into guidelines instead
        _inject_to_guidelines(
            f"**Heuristic:** {heuristic}",
            heuristic,
            datetime.now().strftime("%Y-%m-%d"),
        )
        return

    source = target_file.read_text(encoding="utf-8")

    # Find the SYSTEM_PROMPT constant
    match = re.search(r'(SYSTEM_PROMPT\s*=\s*""")(.*?)(""")',
                      source, re.DOTALL)
    if not match:
        # Can't find SYSTEM_PROMPT — fall back to guidelines
        _inject_to_guidelines(
            f"**Heuristic:** {heuristic}", heuristic,
            datetime.now().strftime("%Y-%m-%d"),
        )
        return

    current_prompt_excerpt = match.group(2)[:2000]
    system = _SYSTEM_PROMPT_PATCH_PROMPT.format(
        current_prompt=current_prompt_excerpt,
        micro_heuristic=heuristic,
    )
    new_prompt_text = query_llm(
        system, "Splice the heuristic now.", model_tier="smart")

    # Reconstruct file
    new_source = source[:match.start(
        2)] + "\n" + new_prompt_text.strip() + "\n" + source[match.end(2):]
    target_file.write_text(new_source, encoding="utf-8")
    print(f"   🧬 Mutation spliced into {target_file.name} SYSTEM_PROMPT — "
          f"Builder is now Generation {_get_builder_generation()}")


def _get_builder_generation() -> int:
    """Read mutation count from ledger for 'builder'."""
    try:
        ledger = FitnessLedger()
        return ledger.get("builder").generation
    except Exception:
        return 1


# ═══════════════════════════════════════════════════════════════════════════
# OODA CYCLE RUNNER
# ═══════════════════════════════════════════════════════════════════════════

def run_mutation_cycle(
    since_ts:     float | None = None,
    force_mutate: bool = False,
    verbose:      bool = True,
) -> list[MutationResult]:
    """
    Main entry point: run one full Observe→Orient→Decide→Act cycle.

    Args:
        since_ts:     Only analyse logs modified after this epoch timestamp.
        force_mutate: Skip fitness threshold check; always attempt mutation.
        verbose:      Print progress to stdout.

    Returns:
        List of MutationResult objects (one per mutated agent).
    """
    ledger = FitnessLedger()
    results: list[MutationResult] = []

    # ── OBSERVE ────────────────────────────────────────────────────────────
    if verbose:
        print("\n🔬 MUTATION ENGINE — OODA CYCLE")
        print("────────────────────────────────")
        print("  [O] OBSERVE: Scanning factory_logs...")

    runs = collect_runs_since(since_ts)
    if verbose:
        print(f"        → {len(runs)} agent executions found")

    if not runs:
        if verbose:
            print("  No new runs to analyse. Mutation cycle complete (no-op).")
        return []

    # ── ORIENT ─────────────────────────────────────────────────────────────
    if verbose:
        print("  [O] ORIENT: Updating Fitness Ledger...")

    for run in runs:
        ledger.record(run)

    ledger.save()

    if verbose:
        for af in ledger.all_agents():
            bar = "█" * int(af.score * 16) + "░" * (16 - int(af.score * 16))
            flag = " ⚠️  < threshold" if af.needs_mutation else ""
            print(
                f"        {af.agent:<20s} [{bar}] {af.score:.2f}  gen={af.generation}{flag}")

    # ── DECIDE ─────────────────────────────────────────────────────────────
    if verbose:
        print("  [D] DECIDE: Evaluating mutation candidates...")

    candidates = [af for af in ledger.all_agents()
                  if af.needs_mutation or force_mutate]

    if not candidates:
        if verbose:
            print("        → All agents above fitness threshold. No mutations needed.")
        return []

    if verbose:
        print(f"        → {len(candidates)} agent(s) require mutation:")
        for af in candidates:
            print(f"          • {af.agent}  score={af.score:.2f}  "
                  f"consecutive_failures={af.consecutive_failures}")

    # ── ACT ────────────────────────────────────────────────────────────────
    if verbose:
        print("  [A] ACT: Generating mutations...")

    agent_runs = {af.agent: [r for r in runs if r.agent == af.agent]
                  for af in candidates}

    for af in candidates:
        if verbose:
            print(
                f"\n  🧫 Mutating agent: {af.agent}  (Generation {af.generation} → {af.generation + 1})")
        try:
            result = generate_mutation(af, agent_runs.get(af.agent, []))
            if result:
                results.append(result)
                if verbose:
                    print(f"     ✅ Mutation applied")
                    print(f"        Target:     {result.target}")
                    print(f"        Heuristic:  {result.heuristic[:120]}")
                    print(f"        Confidence: {result.confidence}")
        except Exception as exc:
            if verbose:
                print(f"     ❌ Mutation failed for {af.agent}: {exc}")

    ledger.save()

    if verbose:
        total = len(results)
        print(f"\n  ✅ Mutation cycle complete. {total} mutation(s) applied.")
        print(f"  Ledger saved → {_LEDGER_PATH.relative_to(_ROOT)}")

    return results


# ═══════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="mutation_engine.py",
        description="Genetic Feedback Loop — analyse agent fitness and apply mutations.",
    )
    parser.add_argument(
        "--force-mutate", action="store_true",
        help="Skip threshold check; always attempt mutation for all agents that have failures.",
    )
    parser.add_argument(
        "--report", action="store_true",
        help="Print fitness ledger report and exit without mutating.",
    )
    parser.add_argument(
        "--since", type=float, default=None,
        help="Only analyse logs modified after this Unix timestamp.",
    )
    args = parser.parse_args()

    if args.report:
        ledger = FitnessLedger()
        print(ledger.report())
        return

    run_mutation_cycle(
        since_ts=args.since,
        force_mutate=args.force_mutate,
        verbose=True,
    )


if __name__ == "__main__":
    main()
