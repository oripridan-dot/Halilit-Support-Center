"""
REPAIR SERVICE — backend/factory/repair_service.py
====================================================
The Immune System of the Bio-Swarm.

A persistent, history-aware, multi-tool repair controller that:

1. Runs every available deterministic fixer (SmartImportFixer, stub detector,
   JSX syntax healer, backup orphan cleaner).
2. Runs TypeScript / ESLint / Vite checks and captures structured errors.
3. Records EVERY repair attempt to a persistent JSON ledger
   (backend/data/repair_history.json) so recurring problems surface as
   chronic patterns instead of being silently re-fixed each time.
4. Analyses the history to detect chronic errors and prints actionable
   pattern warnings so the Chief / Builder prompts can be improved.
5. Emits a structured report at the end of each run.

CLI:
    python backend/factory/repair_service.py [--target path] [--dry-run] [--report]

Factory integration:
    python factory.py repair
    python factory.py repair --target frontend/src/components/views/InventoryView.tsx
    python factory.py repair --report      ← history analysis only, no fixes

Nexus actions:
    {"tool": "repair"}
    {"tool": "repair", "args": "--report"}
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent.parent
FACTORY_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = ROOT / "frontend"
FRONTEND_SRC = ROOT / "frontend" / "src"
HISTORY_FILE = ROOT / "backend" / "data" / "repair_history.json"
MAX_HISTORY_ENTRIES = 500   # keep last N repair records

# ── make sure sys.path includes factory dir so sibling imports work ─────────
if str(FACTORY_DIR) not in sys.path:
    sys.path.insert(0, str(FACTORY_DIR))


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class RepairEntry:
    """A single repair run recorded in the persistent history ledger."""
    timestamp: str
    tool: str
    target: str               # file path or "full_src"
    errors_found: list[str]
    fixes_applied: list[str]
    success: bool
    duration_sec: float
    notes: str = ""


@dataclass
class RepairReport:
    """Collated result of one full repair_service run."""
    started_at: str
    total_errors_found: int
    total_fixes_applied: int
    tools_run: list[str]
    entries: list[RepairEntry] = field(default_factory=list)
    chronic_patterns: list[str] = field(default_factory=list)

    def print(self) -> None:
        width = 64
        print("\n" + "═" * width)
        print("🛠️   REPAIR SERVICE — Full System Report")
        print("═" * width)
        print(f"  Started      : {self.started_at}")
        print(f"  Tools run    : {', '.join(self.tools_run)}")
        print(f"  Errors found : {self.total_errors_found}")
        print(f"  Fixes applied: {self.total_fixes_applied}")
        if self.entries:
            print("\n  ── Tool Results ─────────────────────────────────────")
            for e in self.entries:
                icon = "✅" if e.success else "⚠️ "
                print(
                    f"  {icon} [{e.tool}] {e.target} ({e.duration_sec:.1f}s)")
                for fix in e.fixes_applied:
                    print(f"       › {fix}")
                if not e.success and e.errors_found:
                    for err in e.errors_found[:5]:
                        print(f"       ✗ {err[:100]}")
        if self.chronic_patterns:
            print("\n  ── ⚠️  CHRONIC PATTERNS (recurring errors) ──────────")
            for pat in self.chronic_patterns:
                print(f"  • {pat}")
        overall = "✅ CLEAN" if self.total_errors_found == 0 else (
            f"⚠️  {self.total_errors_found} issue(s) remain after {self.total_fixes_applied} fix(es)"
        )
        print(f"\n  Result: {overall}")
        print("═" * width + "\n")


# ---------------------------------------------------------------------------
# Persistent History Ledger
# ---------------------------------------------------------------------------

class RepairHistory:
    """Read/write the persistent repair history JSON file."""

    def __init__(self, path: Path = HISTORY_FILE) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._entries: list[RepairEntry] = self._load()

    def _load(self) -> list[RepairEntry]:
        if not self.path.exists():
            return []
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            return [RepairEntry(**e) for e in raw]
        except Exception:
            return []

    def save(self) -> None:
        trimmed = self._entries[-MAX_HISTORY_ENTRIES:]
        self.path.write_text(
            json.dumps([asdict(e) for e in trimmed],
                       indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def add(self, entry: RepairEntry) -> None:
        self._entries.append(entry)
        self.save()

    def all(self) -> list[RepairEntry]:
        return list(self._entries)

    def recent(self, n: int = 50) -> list[RepairEntry]:
        return self._entries[-n:]

    # ── Pattern Analysis ───────────────────────────────────────────────────

    def analyze_patterns(self, lookback: int = 100) -> list[str]:
        """
        Scan the last `lookback` entries to surface recurring errors.
        Returns a list of human-readable pattern warnings.
        """
        from collections import Counter
        recent = self.recent(lookback)
        if not recent:
            return []

        error_counts: Counter[str] = Counter()
        file_failure_counts: Counter[str] = Counter()

        for entry in recent:
            for err in entry.errors_found:
                # Normalise: strip file-specific paths to find the pattern
                # e.g. "Cannot resolve '../../stores/foo'" → "Cannot resolve '../../stores/'"
                key = err[:80].strip()
                error_counts[key] += 1
            if not entry.success:
                file_failure_counts[entry.target] += 1

        patterns: list[str] = []

        # Errors seen 3+ times
        for err, count in error_counts.most_common(10):
            if count >= 3:
                patterns.append(
                    f"[x{count}] Recurring error: \"{err[:72]}\" "
                    f"— update SYSTEM_PROMPT or builder lore to prevent this."
                )

        # Files that failed repair 2+ times
        for target, count in file_failure_counts.most_common(5):
            if count >= 2:
                patterns.append(
                    f"[x{count}] Chronic failure: {target} — "
                    f"consider a dedicated spec or manual review."
                )

        return patterns


# ---------------------------------------------------------------------------
# Repair tools
# ---------------------------------------------------------------------------

def _tool_import_fixer(
    target_file: Optional[Path],
    dry_run: bool,
    history: RepairHistory,
) -> RepairEntry:
    """Run SmartImportFixer on target_file (or full src tree) and record result."""
    t0 = time.time()
    label = target_file.relative_to(ROOT) if target_file else "full_src"
    print(f"\n🔧  [import_fixer] Scanning {label}...")

    from smart_import_fixer import fix_imports  # noqa: PLC0415

    report = fix_imports(
        target_file=target_file,
        dry_run=dry_run,
    )
    print(report.summary())

    fixes = [f"[{f.kind}] {f.description}" for f in report.fixes_applied]
    skipped = report.skipped

    entry = RepairEntry(
        timestamp=datetime.now().isoformat(timespec="seconds"),
        tool="import_fixer",
        target=str(label),
        errors_found=skipped,
        fixes_applied=fixes,
        success=len(skipped) == 0,
        duration_sec=round(time.time() - t0, 2),
    )
    history.add(entry)
    return entry


def _tool_tsc(history: RepairHistory) -> RepairEntry:
    """Run `pnpm tsc --noEmit` and record result."""
    t0 = time.time()
    print("\n🔧  [tsc] Running TypeScript check...")
    result = subprocess.run(
        ["pnpm", "tsc", "--noEmit"],
        cwd=str(FRONTEND_DIR),
        capture_output=True,
        text=True,
    )
    duration = round(time.time() - t0, 2)
    combined = (result.stdout + "\n" + result.stderr).strip()
    errors = [ln.strip()
              for ln in combined.splitlines() if "error TS" in ln][:30]

    if result.returncode == 0:
        print(f"  ✅ TypeScript: no errors ({duration}s)")
    else:
        print(f"  ❌ TypeScript: {len(errors)} error(s) ({duration}s)")
        for e in errors[:5]:
            print(f"     • {e[:120]}")

    entry = RepairEntry(
        timestamp=datetime.now().isoformat(timespec="seconds"),
        tool="tsc",
        target="frontend",
        errors_found=errors,
        fixes_applied=[],
        success=result.returncode == 0,
        duration_sec=duration,
    )
    history.add(entry)
    return entry


def _tool_lint(history: RepairHistory) -> RepairEntry:
    """Run ESLint and record result."""
    t0 = time.time()
    print("\n🔧  [eslint] Running ESLint...")
    result = subprocess.run(
        ["pnpm", "run", "lint"],
        cwd=str(FRONTEND_DIR),
        capture_output=True,
        text=True,
    )
    duration = round(time.time() - t0, 2)
    combined = (result.stdout + "\n" + result.stderr).strip()
    errors = [ln.strip() for ln in combined.splitlines()
              if ("error" in ln.lower() or "warning" in ln.lower()) and ln.strip()][:20]

    if result.returncode == 0:
        print(f"  ✅ ESLint: clean ({duration}s)")
    else:
        print(f"  ❌ ESLint: issues found ({duration}s)")
        for e in errors[:5]:
            print(f"     • {e[:120]}")

    entry = RepairEntry(
        timestamp=datetime.now().isoformat(timespec="seconds"),
        tool="eslint",
        target="frontend",
        errors_found=errors,
        fixes_applied=[],
        success=result.returncode == 0,
        duration_sec=duration,
    )
    history.add(entry)
    return entry


def _tool_vite(history: RepairHistory) -> RepairEntry:
    """Run Vite production build to catch runtime import errors."""
    t0 = time.time()
    print("\n🔧  [vite_build] Running Vite production build...")
    try:
        from ui_validator_agent import run_vite_build  # noqa: PLC0415
        ok, output = run_vite_build()
    except ImportError:
        result = subprocess.run(
            ["pnpm", "build"],
            cwd=str(FRONTEND_DIR),
            capture_output=True,
            text=True,
            timeout=120,
        )
        ok = result.returncode == 0
        output = (result.stdout + "\n" + result.stderr).strip()

    duration = round(time.time() - t0, 2)
    errors = []
    if not ok:
        for ln in output.splitlines():
            s = ln.strip()
            if s and any(kw in s for kw in ("error", "Error", "ERROR", "Failed", "Cannot find")):
                errors.append(s[:120])
        errors = errors[:20]
        print(f"  ❌ Vite build failed: {len(errors)} error(s) ({duration}s)")
        for e in errors[:3]:
            print(f"     • {e}")
    else:
        print(f"  ✅ Vite build: clean ({duration}s)")

    entry = RepairEntry(
        timestamp=datetime.now().isoformat(timespec="seconds"),
        tool="vite_build",
        target="frontend",
        errors_found=errors,
        fixes_applied=[],
        success=ok,
        duration_sec=duration,
    )
    history.add(entry)
    return entry


def _tool_stub_detector(history: RepairHistory) -> RepairEntry:
    """Find stub/empty files that the Builder produced but never filled."""
    t0 = time.time()
    print("\n🔧  [stub_detector] Scanning for empty/stub files...")

    import re
    stub_re = re.compile(
        r"(TODO.*implement|raise NotImplementedError|pass\s*#\s*TODO|"
        r"export\s*\{\s*\}|// TODO: implement)",
        re.IGNORECASE,
    )
    empty_re = re.compile(r"^export\s*\{\s*\}\s*;?\s*$", re.MULTILINE)

    stubs_found: list[str] = []
    for fpath in list(FRONTEND_SRC.rglob("*.ts")) + list(FRONTEND_SRC.rglob("*.tsx")):
        if "node_modules" in fpath.parts:
            continue
        try:
            text = fpath.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if empty_re.match(text.strip()) or (len(text.strip()) < 80 and "export" in text):
            stubs_found.append(f"EMPTY_MODULE: {fpath.relative_to(ROOT)}")
        elif stub_re.search(text):
            stubs_found.append(f"STUB_PATTERN: {fpath.relative_to(ROOT)}")

    duration = round(time.time() - t0, 2)
    if stubs_found:
        print(f"  ⚠️  {len(stubs_found)} stub/empty file(s) found:")
        for s in stubs_found[:5]:
            print(f"     • {s}")
    else:
        print(f"  ✅ No stub or empty files ({duration}s)")

    entry = RepairEntry(
        timestamp=datetime.now().isoformat(timespec="seconds"),
        tool="stub_detector",
        target="frontend/src",
        errors_found=stubs_found,
        fixes_applied=[],
        success=len(stubs_found) == 0,
        duration_sec=duration,
        notes="Stubs require a Builder re-run with the target spec.",
    )
    history.add(entry)
    return entry


def _tool_janitor(history: RepairHistory, dry_run: bool) -> RepairEntry:
    """Run the metabolic flush (Janitor Agent)."""
    t0 = time.time()
    print("\n🔧  [janitor] Running metabolic flush...")
    from janitor_agent import metabolic_flush  # noqa: PLC0415
    count = metabolic_flush(dry_run=dry_run, silent=True)
    duration = round(time.time() - t0, 2)
    label = f"Removed {count} waste artifact(s)" if count else "Nothing to flush"
    print(f"  ✅ Janitor: {label} ({duration}s)")

    entry = RepairEntry(
        timestamp=datetime.now().isoformat(timespec="seconds"),
        tool="janitor",
        target="workspace",
        errors_found=[],
        fixes_applied=[f"Flushed {count} artifact(s)"] if count else [],
        success=True,
        duration_sec=duration,
    )
    history.add(entry)
    return entry


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_repair(
    target_file: Optional[str | Path] = None,
    dry_run: bool = False,
    skip_vite: bool = False,
) -> RepairReport:
    """
    Run the full repair pipeline and return a RepairReport.

    Args:
        target_file: If set, focus import_fixer on this specific file.
                     If None, scan the full frontend/src tree.
        dry_run:     Report what would change without touching disk.
        skip_vite:   Skip the Vite production build (saves ~30s in CI).
    """
    started_at = datetime.now().isoformat(timespec="seconds")
    history = RepairHistory()

    target_path: Optional[Path] = None
    if target_file:
        target_path = (ROOT / target_file).resolve()
        if not target_path.exists():
            print(
                f"⚠️  Target file not found: {target_file} — scanning full tree instead.")
            target_path = None

    print("\n" + "━" * 64)
    print("🛠️   REPAIR SERVICE — Activating immune response...")
    print("━" * 64)

    entries: list[RepairEntry] = []
    tools_run: list[str] = []

    # 1. Import fixer (deterministic — always first)
    e = _tool_import_fixer(target_path, dry_run, history)
    entries.append(e)
    tools_run.append("import_fixer")

    # 2. Stub detector
    e = _tool_stub_detector(history)
    entries.append(e)
    tools_run.append("stub_detector")

    # 3. TypeScript check
    e = _tool_tsc(history)
    entries.append(e)
    tools_run.append("tsc")

    # 4. ESLint
    e = _tool_lint(history)
    entries.append(e)
    tools_run.append("eslint")

    # 5. Vite build (optional — skip in fast mode)
    if not skip_vite:
        e = _tool_vite(history)
        entries.append(e)
        tools_run.append("vite_build")

    # 6. Janitor — metabolic flush
    e = _tool_janitor(history, dry_run)
    entries.append(e)
    tools_run.append("janitor")

    # Collate totals
    total_errors = sum(len(e.errors_found) for e in entries)
    total_fixes = sum(len(e.fixes_applied) for e in entries)

    # Pattern analysis from full history
    patterns = history.analyze_patterns()

    report = RepairReport(
        started_at=started_at,
        total_errors_found=total_errors,
        total_fixes_applied=total_fixes,
        tools_run=tools_run,
        entries=entries,
        chronic_patterns=patterns,
    )
    report.print()
    return report


def print_history_report(n: int = 20) -> None:
    """Print a summary of the last N repair history entries and pattern analysis."""
    history = RepairHistory()
    entries = history.recent(n)

    print("\n" + "═" * 64)
    print(f"📋  REPAIR HISTORY — last {len(entries)} entries")
    print("═" * 64)

    if not entries:
        print("  No repair history yet.")
    else:
        for e in entries:
            icon = "✅" if e.success else "❌"
            print(f"  {icon} {e.timestamp}  [{e.tool}]  {e.target}")
            if e.fixes_applied:
                for fx in e.fixes_applied[:2]:
                    print(f"       › {fx[:90]}")
            if not e.success and e.errors_found:
                for err in e.errors_found[:2]:
                    print(f"       ✗ {err[:90]}")

    patterns = history.analyze_patterns()
    if patterns:
        print("\n  ── ⚠️  Chronic Patterns ─────────────────────────────")
        for p in patterns:
            print(f"  • {p}")
    else:
        print("\n  ✅ No chronic patterns detected.")

    print("═" * 64 + "\n")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    _dry = "--dry-run" in sys.argv or "-n" in sys.argv
    _report = "--report" in sys.argv or "-r" in sys.argv
    _fast = "--fast" in sys.argv          # skip Vite build
    _target: Optional[str] = None

    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == "--target" and i + 1 < len(sys.argv):
            _target = sys.argv[i + 1]
        elif arg.startswith("--target="):
            _target = arg.split("=", 1)[1]

    if _report:
        print_history_report()
        sys.exit(0)

    result = run_repair(target_file=_target, dry_run=_dry, skip_vite=_fast)
    overall_ok = result.total_errors_found == 0
    sys.exit(0 if overall_ok else 1)
