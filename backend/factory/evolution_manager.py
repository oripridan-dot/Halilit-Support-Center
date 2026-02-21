"""
EVOLUTION MANAGER  (backend/factory/evolution_manager.py)
==========================================================
Processes Scout evolution proposals through a deterministic decision
pipeline — no LLM required for the verdict.

Decision Rules (applied in order):
  1. If the Scout already marked the proposal SKIP → REJECT without build.
  2. If the proposal introduces a framework outside the approved stack → REJECT.
  3. RECOMMEND + LOW_RISK  → SANDBOX  (validate + build via inner loop).
  4. RECOMMEND + MEDIUM_RISK → SPEC    (write spec, defer build to next session).
  5. MONITOR / unknown risk → MONITOR  (move to reviewed, no build).

In ALL cases the proposal file is stamped with a Chief verdict section and
moved to specs/strategy/evolution/reviewed/ so the Tech Lead scan backlog
clears. Nothing is left in the pending directory after processing.

Usage (from nexus.py or factory.py):
    from backend.factory.evolution_manager import process_proposal
    result = process_proposal("specs/strategy/evolution/2026-02-22_proposal_xxx.md")
"""

from __future__ import annotations

import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT))

REVIEWED_DIR = _ROOT / "specs" / "strategy" / "evolution" / "reviewed"
INTERFACE_SPECS_DIR = _ROOT / "specs" / "interface"
TODAY = datetime.now().strftime("%Y-%m-%d")

# ---------------------------------------------------------------------------
# Approved tech-stack whitelist
# Frontend: React 18, Vite, TypeScript, Zustand, React Query (<= v5), Tailwind,
#           lucide-react, framer-motion, @tanstack/react-query
# Backend:  Python 3.11+, FastAPI, google-genai, Pydantic v2, SQLite
# ---------------------------------------------------------------------------
_APPROVED_PATTERNS = [
    r"debounce", r"throttle", r"lodash", r"trie", r"prefix.?search",
    r"react.?query", r"tanstack", r"zustand", r"tailwind", r"lucide",
    r"framer.?motion", r"vite", r"typescript", r"pydantic",
    r"fastapi", r"sqlite", r"gemini", r"google.?genai",
    r"playwright", r"vitest", r"eslint", r"prettier",
    r"image.?validation", r"clarifai", r"webp", r"memoiz",
]

_BLOCKED_PATTERNS = [
    r"three\.?js", r"galaxy", r"relay.?compiler", r"server.?component",
    r"next\.?js", r"nuxt", r"remix", r"graphql", r"react.?native",
    r"supabase", r"firebase", r"meilisearch", r"elasticsearch",
    r"mongodb", r"redis", r"celery", r"kafka", r"rabbitmq",
    r"prisma", r"drizzle",
]


def _extract_field(text: str, field: str) -> str:
    """Pull a single-line field from the proposal markdown header."""
    m = re.search(rf"\*\*{field}:\*\*\s*(.+)", text, re.IGNORECASE)
    if m:
        return m.group(1).strip().strip("`").strip()
    return ""


def _is_blocked(text: str) -> bool:
    """Return True if the proposal mentions a blocked framework/library."""
    lower = text.lower()
    for pat in _BLOCKED_PATTERNS:
        if re.search(pat, lower):
            return True
    return False


def _is_in_approved_stack(text: str) -> bool:
    """Return True if the tool maps to something in the approved stack."""
    lower = text.lower()
    for pat in _APPROVED_PATTERNS:
        if re.search(pat, lower):
            return True
    return False


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

def evaluate_proposal(proposal_path: Path) -> dict[str, Any]:
    """
    Deterministically evaluate a proposal file without an LLM call.

    Returns a dict:
      verdict   : "SANDBOX" | "SPEC" | "MONITOR" | "REJECT"
      reason    : str
      scout_verdict: str  (what the Scout originally said)
      risk_level: str
    """
    text = proposal_path.read_text(encoding="utf-8")

    scout_verdict = _extract_field(text, "Verdict")
    risk_level = _extract_field(text, "Risk Level")
    tool_name = _extract_field(text, "Name") or proposal_path.stem
    prop_type = _extract_field(text, "Type")

    # Rule 1: Scout already said SKIP → agree
    if scout_verdict.upper() == "SKIP":
        return {"verdict": "REJECT", "reason": "Scout verdict was SKIP.",
                "scout_verdict": scout_verdict, "risk_level": risk_level}

    # Rule 2: Explicitly blocked framework
    if _is_blocked(text):
        return {"verdict": "REJECT",
                "reason": "Proposal introduces a framework outside the approved stack (Three Source Rules / Architecture Law).",
                "scout_verdict": scout_verdict, "risk_level": risk_level}

    # Rule 3: RECOMMEND + LOW → go straight to sandbox validation
    if scout_verdict.upper() == "RECOMMEND" and risk_level.upper() == "LOW":
        return {"verdict": "SANDBOX",
                "reason": f"RECOMMEND + LOW_RISK: '{tool_name}' cleared for sandbox validation.",
                "scout_verdict": scout_verdict, "risk_level": risk_level}

    # Rule 4: RECOMMEND + MEDIUM → write a spec, defer build
    if scout_verdict.upper() == "RECOMMEND" and risk_level.upper() == "MEDIUM":
        return {"verdict": "SPEC",
                "reason": f"RECOMMEND + MEDIUM_RISK: '{tool_name}' queued for spec-driven build next session.",
                "scout_verdict": scout_verdict, "risk_level": risk_level}

    # Rule 5: MONITOR or any other verdict → archive without building
    return {"verdict": "MONITOR",
            "reason": f"Scout verdict '{scout_verdict}' / risk '{risk_level}' — monitoring, no build this session.",
            "scout_verdict": scout_verdict, "risk_level": risk_level}


def _stamp_verdict(proposal_path: Path, evaluation: dict[str, Any]) -> None:
    """Append a Chief Verdict block to the proposal file before archiving."""
    block = (
        f"\n---\n"
        f"## Chief Verdict — {TODAY}\n"
        f"**Decision:** `{evaluation['verdict']}`\n"
        f"**Reason:** {evaluation['reason']}\n"
        f"*(Processed by evolution_manager.py — Chief auto-review)*\n"
    )
    with proposal_path.open("a", encoding="utf-8") as f:
        f.write(block)


def _write_spec_stub(proposal_path: Path, evaluation: dict[str, Any]) -> Path | None:
    """For SPEC-verdict proposals, write a minimal spec stub to specs/interface/."""
    text = proposal_path.read_text(encoding="utf-8")
    tool_name = _extract_field(text, "Name") or proposal_path.stem
    integration = re.search(r"## Integration Path\n(.*?)(?=\n##|\Z)",
                            text, re.DOTALL)
    integration_text = integration.group(
        1).strip() if integration else "See proposal."
    impact = re.search(
        r"## Expected Impact\n(.*?)(?=\n##|\Z)", text, re.DOTALL)
    impact_text = impact.group(1).strip() if impact else ""
    problem = re.search(
        r"## Problem Addressed\n(.*?)(?=\n##|\Z)", text, re.DOTALL)
    problem_text = problem.group(1).strip() if problem else ""

    safe_name = re.sub(r"[^\w]+", "_", tool_name.lower()).strip("_")
    spec_path = INTERFACE_SPECS_DIR / f"evolution_{safe_name}.md"

    spec_content = f"""# Spec: {tool_name} Integration
**Source:** {proposal_path.name}
**Created:** {TODAY}
**Status:** PENDING BUILD

---

## Problem
{problem_text}

## Proposed Solution
{integration_text}

## Expected Impact
{impact_text}

## Acceptance Criteria
- [ ] Existing tests still pass after integration (`pnpm test --run`).
- [ ] Vite build reports 0 errors.
- [ ] No new dependencies outside the approved stack (package.json audit).
- [ ] Three Source Rules: no synthetic data introduced.

## Sandbox Validation Required
Run `sandbox specs/interface/{spec_path.name}` before merging.
"""
    spec_path.write_text(spec_content, encoding="utf-8")
    print(f"   📄  Spec stub written → {spec_path.relative_to(_ROOT)}")
    return spec_path


def process_proposal(proposal_path_str: str) -> dict[str, Any]:
    """
    Full pipeline: evaluate → stamp → move to reviewed/.

    Returns a summary dict the Chief can act on:
      verdict      : "SANDBOX" | "SPEC" | "MONITOR" | "REJECT"
      reason       : str
      reviewed_path: str  (where the file now lives)
      spec_path    : str | None  (for SPEC verdict)
      sandbox_spec : str | None  (for SANDBOX verdict — path to feed into sandbox tool)
    """
    proposal_path = Path(proposal_path_str)
    if not proposal_path.is_absolute():
        proposal_path = _ROOT / proposal_path

    if not proposal_path.exists():
        return {"verdict": "ERROR", "reason": f"File not found: {proposal_path}"}

    evaluation = evaluate_proposal(proposal_path)
    verdict = evaluation["verdict"]

    print(f"\n📋  EVOLUTION MANAGER — {proposal_path.name}")
    print(
        f"   Scout: {evaluation['scout_verdict']} / Risk: {evaluation['risk_level']}")
    print(f"   Chief decision: {verdict} — {evaluation['reason']}")

    # Stamp verdict into the file
    _stamp_verdict(proposal_path, evaluation)

    # Move to reviewed/
    REVIEWED_DIR.mkdir(parents=True, exist_ok=True)
    dest = REVIEWED_DIR / proposal_path.name
    shutil.move(str(proposal_path), str(dest))
    print(f"   ✅  Archived → reviewed/{proposal_path.name}")

    result: dict[str, Any] = {
        "verdict": verdict,
        "reason": evaluation["reason"],
        "reviewed_path": str(dest.relative_to(_ROOT)),
        "spec_path": None,
        "sandbox_spec": None,
    }

    # For SPEC verdict: write stub spec in specs/interface/
    if verdict == "SPEC":
        spec_path = _write_spec_stub(dest, evaluation)
        if spec_path:
            result["spec_path"] = str(spec_path.relative_to(_ROOT))
            result["sandbox_spec"] = str(spec_path.relative_to(_ROOT))

    # For SANDBOX verdict: spec path IS the proposal in reviewed (already has integration path)
    if verdict == "SANDBOX":
        result["sandbox_spec"] = str(dest.relative_to(_ROOT))
        print(f"   🏗️   Ready for sandbox validation: "
              f"sandbox {result['sandbox_spec']}")

    return result


def process_all_pending(max_batch: int = 3) -> list[dict[str, Any]]:
    """Process up to `max_batch` pending proposals from the evolution directory."""
    evo_dir = _ROOT / "specs" / "strategy" / "evolution"
    pending = sorted(
        [p for p in evo_dir.glob("*.md") if p.name.upper() != "README.MD"],
        key=lambda p: p.name,
    )[:max_batch]

    if not pending:
        print("✅  No pending evolution proposals.")
        return []

    results = []
    for p in pending:
        results.append(process_proposal(str(p)))
    return results


if __name__ == "__main__":
    # CLI usage: python backend/factory/evolution_manager.py [proposal_path]
    if len(sys.argv) > 1:
        r = process_proposal(sys.argv[1])
        print(f"\nResult: {r}")
    else:
        results = process_all_pending()
        sandboxable = [r for r in results if r["verdict"] == "SANDBOX"]
        specd = [r for r in results if r["verdict"] == "SPEC"]
        print(f"\n{'='*60}")
        print(f"Batch complete: {len(results)} processed")
        print(f"  SANDBOX-ready : {len(sandboxable)}")
        print(f"  Spec written  : {len(specd)}")
        print(
            f"  Rejected/Mon. : {len(results) - len(sandboxable) - len(specd)}")
