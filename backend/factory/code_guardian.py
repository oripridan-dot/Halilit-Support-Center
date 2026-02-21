"""
CODE GUARDIAN — System Invariant Enforcer  (backend/factory/code_guardian.py)
==============================================================================
Automatically protects critical functions and code blocks from being silently
removed by LLM-driven `implement` / `patch_component` runs.

How it works
------------
1. REGISTRY   — a list of (file, marker, capsule) triples.
   • `marker`  : a short string that MUST appear in the file (e.g. a def name).
   • `capsule` : the full source block to INJECT at the end of the file if the
                 marker is missing.
2. verify()   — checks every registry entry; returns a list of violations.
3. restore()  — for each violation, appends the capsule to the file.
4. run()      — verify → print report → restore if needed → return ok/fail.

Wire-up
-------
Called from:
  • nexus.py  — before every swarm execution and at every steering gate.
  • frontend_manager.py / data_manager.py — at the top of each run.

CLI
---
  python backend/factory/code_guardian.py            # verify + restore
  python backend/factory/code_guardian.py --verify   # verify only (exit 1 if violations)
"""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent

# ──────────────────────────────────────────────────────────────────────────────
# CAPSULE STORE
# Each capsule is injected verbatim at the END of the target file when its
# marker is absent.  Keep capsules minimal — just enough to restore the logic.
# ──────────────────────────────────────────────────────────────────────────────

_SELF_HEAL_CAPSULE = textwrap.dedent('''
    # ── CODE GUARDIAN RESTORED ──────────────────────────────────────────────────
    # SYSTEM INVARIANT: _self_heal_patch_component (auto-restored by code_guardian)
    import re as _cg_re, json as _cg_json
    from pathlib import Path as _CGPath

    _HEAL_SYSTEM_PROMPT = """
    You are the FRONTEND MANAGER in self-healing mode.
    A patch_component operation just failed because the search anchor was not found.
    Read the ACTUAL FILE CONTENT and produce a corrected patch, or fall back to implement.
    OUTPUT FORMAT (JSON only):
    {"thought":"...","queue":[{"tool":"patch_component","args":{"file":"...","search":"...","replace":"..."},"parallel":false},{"tool":"ui_validate","args":"","parallel":false}]}
    """

    def _self_heal_patch_component(file_path: str, intent: str,
                                    original_search: str, original_replace: str,
                                    max_retries: int = 2) -> dict:
        """SYSTEM INVARIANT — do NOT remove. Auto-restored by code_guardian."""
        abs_path = _ROOT / file_path
        if not abs_path.exists():
            return {"tool": "patch_component", "args": file_path, "success": False,
                    "summary": f"❌ [self-heal] File not found: {file_path}",
                    "error_output": f"path {file_path} does not exist"}
        file_lines = abs_path.read_text(encoding="utf-8").splitlines()
        file_preview = "\\n".join(file_lines[:300])
        if len(file_lines) > 300:
            file_preview += f"\\n... ({len(file_lines)-300} more lines truncated)"
        user_prompt = (
            f"Original intent: {intent}\\n\\n"
            f"Failed anchor:\\n```\\n{original_search}\\n```\\n\\n"
            f"Intended replacement:\\n```\\n{original_replace}\\n```\\n\\n"
            f"ACTUAL FILE ({file_path}):\\n```tsx\\n{file_preview}\\n```\\n\\n"
            f"Produce corrected JSON task queue."
        )
        for attempt in range(1, max_retries + 1):
            print(f"   🔧 [self-heal] Attempt {attempt}/{max_retries}…")
            raw = query_llm(_HEAL_SYSTEM_PROMPT, user_prompt, temperature=0.2, model_tier="smart")
            if not raw:
                continue
            raw = _cg_re.sub(r"^```(?:json)?\\s*", "", raw.strip())
            raw = _cg_re.sub(r"\\s*```$", "", raw)
            try:
                m = _cg_re.search(r"\\{.*\\}", raw, _cg_re.DOTALL)
                if not m:
                    continue
                parsed = _cg_json.loads(m.group(0))
                if parsed.get("thought"):
                    print(f"   💡 [self-heal] {parsed['thought']}")
                for task in parsed.get("queue", []):
                    t, a = task.get("tool", ""), task.get("args", "")
                    if t == "patch_component":
                        pa = a if isinstance(a, dict) else {}
                        res = _execute_patch_component(pa)
                        if res.get("success"):
                            print(f"   ✅ [self-heal] Patch applied on attempt {attempt}.")
                            return res
                    elif t == "implement":
                        return _execute_factory_cmd("implement", a if isinstance(a, str) else str(a))
            except (_cg_json.JSONDecodeError, ValueError):
                continue
        # fallback: write temp spec and implement
        tmp = _CGPath(__file__).resolve().parent.parent.parent / "specs" / "temp" / f"_heal_{_CGPath(file_path).stem}.md"
        tmp.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_text(
            f"# Auto-heal spec for {file_path}\\n\\n## Intent\\n{intent}\\n\\n"
            f"## Target\\n`{file_path}`\\n\\n## Constraint\\nPreserve all existing behaviour.",
            encoding="utf-8",
        )
        res = _execute_factory_cmd("implement", str(tmp.relative_to(_CGPath(__file__).resolve().parent.parent.parent)))
        res["self_healed"] = True
        return res
    # ── END CODE GUARDIAN RESTORE ───────────────────────────────────────────────
''')

# ──────────────────────────────────────────────────────────────────────────────
# REGISTRY
# Format: (relative_file_path, marker_string, capsule_or_None)
# capsule=None means "fail loudly but don't auto-inject" (manual fix required)
# ──────────────────────────────────────────────────────────────────────────────

REGISTRY: list[tuple[str, str, str | None]] = [
    # ── frontend_manager.py ──────────────────────────────────────────────────
    (
        "backend/factory/frontend_manager.py",
        "_self_heal_patch_component",
        _SELF_HEAL_CAPSULE,
    ),
    (
        "backend/factory/frontend_manager.py",
        "SYSTEM INVARIANT",
        None,  # marker-only; the capsule above already restores the whole block
    ),
    (
        "backend/factory/frontend_manager.py",
        "def run_frontend_swarm(",
        None,  # core public API — if missing the file is fundamentally broken
    ),
    # ── agent_core.py ────────────────────────────────────────────────────────
    (
        "backend/factory/agent_core.py",
        "def query_llm(",
        None,
    ),
    (
        "backend/factory/agent_core.py",
        "def build_dynamic_context(",
        None,
    ),
    # ── udiff_patcher.py ─────────────────────────────────────────────────────
    (
        "backend/factory/udiff_patcher.py",
        "def apply_patch(",
        None,
    ),
    (
        "backend/factory/udiff_patcher.py",
        "def apply_udiff(",
        None,
    ),
    # ── data_manager.py ──────────────────────────────────────────────────────
    (
        "backend/factory/data_manager.py",
        "def run_data_swarm(",
        None,
    ),
    # ── source_rules.py — THE LAW ────────────────────────────────────────────
    (
        "backend/source_rules.py",
        "class AuthorizedSource(",
        None,
    ),
    (
        "backend/source_rules.py",
        "def enforce_source_rules(",
        None,
    ),
    (
        "backend/source_rules.py",
        "ZERO TOLERANCE POLICY",
        None,
    ),
    # ── nexus.py ─────────────────────────────────────────────────────────────
    (
        "nexus.py",
        "def execute_swarm(",
        None,
    ),
    (
        "nexus.py",
        "def review_changes(",
        None,
    ),
    # ── server.py ────────────────────────────────────────────────────────────
    (
        "backend/server.py",
        "def _build_catalog_cache(",
        None,
    ),
]

# ──────────────────────────────────────────────────────────────────────────────
# Core logic
# ──────────────────────────────────────────────────────────────────────────────

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def _read(rel: str) -> str | None:
    p = _ROOT / rel
    if not p.exists():
        return None
    return p.read_text(encoding="utf-8")


def verify() -> list[dict]:
    """
    Check every registry entry.
    Returns a list of violation dicts: {file, marker, has_capsule}.
    """
    violations: list[dict] = []
    seen: set[tuple[str, str]] = set()

    for rel, marker, capsule in REGISTRY:
        if (rel, marker) in seen:
            continue
        seen.add((rel, marker))
        content = _read(rel)
        if content is None:
            violations.append({"file": rel, "marker": marker, "has_capsule": capsule is not None,
                               "reason": "FILE MISSING"})
            continue
        if marker not in content:
            violations.append({"file": rel, "marker": marker, "has_capsule": capsule is not None,
                               "reason": "MARKER ABSENT"})
    return violations


def restore(violations: list[dict]) -> list[str]:
    """
    For each violation that has a capsule, append the capsule to the file.
    Returns list of files successfully restored.
    """
    restored: list[str] = []
    # Collect unique (file, capsule) pairs to inject
    injected: dict[str, set[str]] = {}

    for v in violations:
        if not v["has_capsule"]:
            continue
        rel = v["file"]
        # Find the matching capsule
        for freg, mreg, capsule in REGISTRY:
            if freg == rel and mreg == v["marker"] and capsule:
                injected.setdefault(rel, set()).add(capsule)

    for rel, capsules in injected.items():
        p = _ROOT / rel
        if not p.exists():
            print(f"  {RED}✗ Cannot restore {rel} — file does not exist{RESET}")
            continue
        content = p.read_text(encoding="utf-8")
        appended = content
        for capsule in capsules:
            if v["marker"] not in appended:  # double-check still needed
                appended += "\n" + capsule
        p.write_text(appended, encoding="utf-8")
        print(f"  {GREEN}✔ Restored invariants in {rel}{RESET}")
        restored.append(rel)

    return restored


def run(auto_restore: bool = True, silent: bool = False) -> bool:
    """
    Full guardian cycle: verify → report → optionally restore.
    Returns True if all invariants are healthy (after any restoration).
    """
    violations = verify()

    if not violations:
        if not silent:
            print(f"  {GREEN}🛡  Code Guardian: all invariants intact.{RESET}")
        return True

    print(f"\n{BOLD}{YELLOW}🛡  CODE GUARDIAN — {len(violations)} violation(s) detected:{RESET}")
    for v in violations:
        icon = "🔴" if not v["has_capsule"] else "🟡"
        print(f"  {icon}  [{v['reason']}] {v['file']} → `{v['marker']}`"
              + (" (auto-restorable)" if v["has_capsule"] else " ⚠️  MANUAL FIX REQUIRED"))

    if auto_restore:
        restorable = [v for v in violations if v["has_capsule"]]
        if restorable:
            print(
                f"\n  {YELLOW}↩  Restoring {len(restorable)} invariant(s)…{RESET}")
            restore(violations)
            # Re-verify after restoration
            violations2 = verify()
            if not violations2:
                print(f"  {GREEN}✔  All invariants restored successfully.{RESET}")
                return True
            else:
                still_bad = [v for v in violations2 if not v["has_capsule"]]
                if still_bad:
                    print(
                        f"  {RED}✗  {len(still_bad)} invariant(s) still missing after restore — MANUAL FIX REQUIRED:{RESET}")
                    for v in still_bad:
                        print(f"      └─ {v['file']}: `{v['marker']}`")
                    return False
                return True

    # non-restorable violations remain
    non_restorable = [v for v in violations if not v["has_capsule"]]
    if non_restorable:
        print(
            f"\n  {RED}⛔  {len(non_restorable)} critical invariant(s) missing — MANUAL FIX REQUIRED{RESET}")
        return False
    return True


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    verify_only = "--verify" in sys.argv
    ok = run(auto_restore=not verify_only)
    sys.exit(0 if ok else 1)
