"""
TECH LEAD AGENT — Heuristics Engine
=====================================
Static analysis engine that scans the repository for technical debt,
architectural smells, and data-pipeline risks at factory boot time.

Generates DAILY_BRIEFING.md with categorized findings and
copy-paste Chief commands for every flagged issue.

Usage (standalone):
    python backend/factory/tech_lead_agent.py

Usage (via nexus.py):
    python nexus.py --briefing
"""

import json
import os
import re
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False

# Relative-import fallback for both direct execution and package import
try:
    from agent_core import query_llm
except ImportError:
    from .agent_core import query_llm

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_COMPONENTS_DIR = ROOT_DIR / "frontend" / "src" / "components"
SPECS_DIR = ROOT_DIR / "specs"

# ---------------------------------------------------------------------------
# SYSTEM PROMPT
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """
You are the PRINCIPAL ENGINEER and TECH LEAD (Level 9) of the Halilit Support Center Dark Factory.
Your job is to analyze the raw heuristic data provided by the file system scanner and generate a professional DAILY_BRIEFING.md for the Operator.

Categorize your findings STRICTLY into:
🔴 CRITICAL: Rate-limit risks, massive memory traps (>5 MB client-side JSON), or systemic UI/State bugs.
🟠 MAJOR: Architecture smells, overgrown React components (>300 lines), hardcoded CSS colors, or pending Evolution Proposals.
🟡 MINOR: Code hygiene, dead ghost folders, duplicate configs.

OUTPUT RULES:
1. Output MUST be pure Markdown. Do NOT wrap the output in triple-backtick code fences.
2. Under each issue, you MUST provide a "Suggested Chief Command" — an exact, copy-paste prompt the Operator can hand to the Chief to fix it immediately via a Task Force.
3. Keep the tone authoritative, concise, and highly technical.
4. If no issues exist in a category, write "No issues detected." under that heading.
5. Always end with a "Factory Status" summary line.
"""


# ---------------------------------------------------------------------------
# HEURISTICS ENGINE
# ---------------------------------------------------------------------------

class FactoryHeuristics:
    """Static analysis engine for the Halilit Support Center repository."""

    def __init__(self) -> None:
        self.issues: List[str] = []

    # --- 1. Memory Traps ----------------------------------------------------

    def check_memory_traps(self) -> None:
        """Flags large data files that risk freezing the React client."""
        taxonomy = ROOT_DIR / "backend" / "data" / "learned_taxonomy.json"
        if taxonomy.exists():
            size_mb = taxonomy.stat().st_size / (1024 * 1024)
            if size_mb > 3.0:
                self.issues.append(
                    f"[DATA] learned_taxonomy.json is dangerously large "
                    f"({size_mb:.2f} MB). High risk of React client memory "
                    f"freeze. Needs JIT routing."
                )
        else:
            self.issues.append(
                "[DATA] learned_taxonomy.json is MISSING. "
                "The frontend catalog will be empty."
            )

        # Also check catalog JSON blobs in public/data
        public_data = ROOT_DIR / "frontend" / "public" / "data"
        if public_data.exists():
            for json_file in public_data.glob("*.json"):
                try:
                    size_mb = json_file.stat().st_size / (1024 * 1024)
                    if size_mb > 5.0:
                        self.issues.append(
                            f"[DATA] {json_file.name} in frontend/public/data "
                            f"is {size_mb:.2f} MB — exceeds 5 MB client-side "
                            f"threshold. Must be paginated or lazy-loaded."
                        )
                except OSError:
                    pass

    # --- 2. Ghost Directories -----------------------------------------------

    def check_ghost_directories(self) -> None:
        """Flags populated deprecated folders that pollute the AI context window."""
        candidates = [
            "backend/scripts/archive",
            "specs/temp",
            "specs/repairs",
        ]
        for rel in candidates:
            target = ROOT_DIR / rel
            if target.exists():
                try:
                    children = list(target.iterdir())
                except PermissionError:
                    continue
                non_readme = [c for c in children if c.name.upper()
                              != "README.MD"]
                if non_readme:
                    self.issues.append(
                        f"[HYGIENE] Ghost directory populated: '{rel}' "
                        f"({len(non_readme)} file(s)). This will cause the "
                        f"Context Discovery AI to hallucinate deprecated logic."
                    )

        # Flag .backup.* files left behind by automated patchers
        backup_files = [
            f for f in ROOT_DIR.rglob("*.backup.*")
            if ".venv" not in str(f) and "node_modules" not in str(f)
        ]
        if backup_files:
            names = [str(f.relative_to(ROOT_DIR)) for f in backup_files[:5]]
            self.issues.append(
                f"[HYGIENE] Found {len(backup_files)} .backup.* artifact(s): "
                f"{names}. These ghost files pollute AI context — delete them."
            )

    # --- 3. Duplicate Configs -----------------------------------------------

    def check_duplicate_configs(self) -> None:
        """Flags multiple .cursorrules files that cause conflicting AI rules."""
        rules = list(ROOT_DIR.rglob(".cursorrules"))
        if len(rules) > 1:
            paths = [str(p.relative_to(ROOT_DIR)) for p in rules]
            self.issues.append(
                f"[CONFIG] Found {len(rules)} .cursorrules files: {paths}. "
                f"Keep only the root-level copy to prevent conflicting AI rules."
            )

        # Also flag multiple tailwind configs (common after v0/Stitch merges)
        tw_configs = list(ROOT_DIR.rglob("tailwind.config.*"))
        tw_in_root_or_frontend = [
            p for p in tw_configs
            if ".venv" not in str(p) and "node_modules" not in str(p)
        ]
        if len(tw_in_root_or_frontend) > 1:
            paths = [str(p.relative_to(ROOT_DIR))
                     for p in tw_in_root_or_frontend]
            self.issues.append(
                f"[CONFIG] Found {len(tw_in_root_or_frontend)} tailwind.config files: "
                f"{paths}. Only the frontend copy is valid."
            )

    # --- 4. React Code Smells -----------------------------------------------

    def check_react_code_smells(self) -> None:
        """Scans for monolithic components and design-token violations."""
        if not FRONTEND_COMPONENTS_DIR.exists():
            self.issues.append(
                "[ARCHITECTURE] frontend/src/components/ directory not found. "
                "The component tree may be missing.",
            )
            return

        # Tailwind arbitrary-value hex color: text-[#rrggbb] or bg-[#rrggbb]
        hex_regex = re.compile(
            r'(?:text|bg|border|ring|fill|stroke)-\[#[0-9a-fA-F]{3,6}\]'
        )

        for tsx_file in FRONTEND_COMPONENTS_DIR.rglob("*.tsx"):
            try:
                content = tsx_file.read_text(
                    encoding="utf-8", errors="replace")
            except OSError:
                continue  # Skip unreadable files safely

            lines = content.splitlines()
            rel_path = tsx_file.relative_to(ROOT_DIR)

            # Check 1: Monolithic component (>350 lines)
            if len(lines) > 350:
                self.issues.append(
                    f"[ARCHITECTURE] Monolithic Component: {tsx_file.name} "
                    f"is {len(lines)} lines ({rel_path}). "
                    f"Needs refactoring into focused sub-components."
                )

            # Check 2: Hardcoded hex colors (v0/Stitch design-system violations)
            hex_matches = hex_regex.findall(content)
            if hex_matches:
                unique_hex = sorted(set(hex_matches))
                self.issues.append(
                    f"[UI] Design-System Violation in {tsx_file.name}: "
                    f"Found raw hex colors {unique_hex}. "
                    f"Must be converted to Tailwind scale tokens (e.g., text-slate-900)."
                )

            # Check 3: TODO/FIXME markers (unresolved debt)
            todo_count = len(re.findall(
                r'//\s*(TODO|FIXME|HACK|XXX)', content))
            if todo_count >= 3:
                self.issues.append(
                    f"[HYGIENE] {tsx_file.name} has {todo_count} unresolved "
                    f"TODO/FIXME markers. Needs triage."
                )

    # --- 5. Pending Evolution Proposals ------------------------------------

    def check_pending_evolution(self) -> None:
        """Checks if the Scout agent has queued unreviewed evolution proposals.

        Reports at most 3 proposals (oldest first) so the Chief does not try
        to action the entire backlog in a single session.  Remaining count is
        surfaced so the Chief knows a backlog exists.
        """
        evo_dir = SPECS_DIR / "strategy" / "evolution"
        if evo_dir.exists():
            all_proposals = sorted(
                [p for p in evo_dir.glob("*.md")          # top-level only
                 if p.name.upper() != "README.MD"],        # reviewed/ subdir excluded by *.md
                key=lambda p: p.name,  # lexicographic ≈ date order
            )
            if all_proposals:
                # Cap at 3 per session to prevent mass-parallel anchor conflicts
                batch = all_proposals[:3]
                remaining = len(all_proposals) - len(batch)
                names = ", ".join(p.name for p in batch)
                tail = f" (+{remaining} more — process in next session)" if remaining else ""
                self.issues.append(
                    f"[EVOLUTION] Tech Scout has {len(all_proposals)} pending proposal(s) "
                    f"awaiting Chief review (batch of {len(batch)}): {names}{tail}. "
                    f"CHIEF RULE: process ONLY this batch of {len(batch)} this session. "
                    f"Use delegate_data per proposal. Do NOT schedule all at once."
                )

    # --- 6. Backend Integrity Checks ---------------------------------------

    def check_backend_integrity(self) -> None:
        """Verifies critical backend files are present and non-empty."""
        critical_files = [
            "backend/source_rules.py",
            "backend/server.py",
            "backend/product_normalizer.py",
            "backend/jit_agent.py",
        ]
        for rel in critical_files:
            path = ROOT_DIR / rel
            if not path.exists():
                self.issues.append(
                    f"[INTEGRITY] MISSING critical backend file: {rel}. "
                    f"The factory cannot start without it."
                )
            else:
                try:
                    if path.stat().st_size < 100:
                        self.issues.append(
                            f"[INTEGRITY] {rel} is suspiciously small "
                            f"({path.stat().st_size} bytes). Likely empty or stub."
                        )
                except OSError:
                    pass

    # --- 7. Spec Drift Detection (Holographic Specs) -----------------------

    def check_spec_drift(self) -> None:
        """
        Compares recently changed code files against the ``api_contracts``,
        ``dependencies``, ``ui_dependencies``, and ``golden_scenarios_validation``
        arrays declared in every spec's YAML frontmatter.

        Flags a 🟠 MAJOR warning for each spec whose declared dependencies were
        modified in the last 48 hours, indicating potential spec-to-code drift.
        """
        if not _YAML_AVAILABLE:
            self.issues.append(
                "[SPEC DRIFT] PyYAML is not installed — cannot run spec-drift detection. "
                "Run `pip install PyYAML` to enable this heuristic."
            )
            return

        # ── 1. Ask Git for files touched in the last 48 hours ────────────────
        try:
            result = subprocess.run(
                ["git", "log", "--name-only",
                    "--pretty=format:", "--since=48 hours ago"],
                cwd=str(ROOT_DIR),
                capture_output=True,
                text=True,
                timeout=15,
            )
            recently_changed: set[str] = {
                line.strip()
                for line in result.stdout.splitlines()
                if line.strip()
            }
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return  # Git not available or timed out — skip silently

        if not recently_changed:
            return  # Nothing changed recently

        # ── 2. Scan all spec files for YAML frontmatter ───────────────────────
        spec_dirs: list[Path] = [
            SPECS_DIR / "interface",
            SPECS_DIR / "data_pipeline",
        ]
        dep_keys = (
            "api_contracts",
            "dependencies",
            "ui_dependencies",
            "golden_scenarios_validation",
        )

        for spec_dir in spec_dirs:
            if not spec_dir.exists():
                continue
            for spec_file in sorted(spec_dir.glob("*.md")):
                try:
                    raw = spec_file.read_text(encoding="utf-8")
                except OSError:
                    continue

                import re as _re
                fm_match = _re.match(r"^---\n(.*?)\n---", raw, _re.DOTALL)
                if not fm_match:
                    continue  # legacy spec without frontmatter — skip

                try:
                    metadata: dict = yaml.safe_load(fm_match.group(1)) or {}
                except yaml.YAMLError:
                    continue

                # Collect all declared dependency paths from this spec
                declared: list[str] = []
                for key in dep_keys:
                    declared.extend(metadata.get(key, []))

                # Check overlap with recently-changed files
                drifted = [d for d in declared if d in recently_changed]
                if drifted:
                    spec_rel = spec_file.relative_to(ROOT_DIR)
                    spec_id = metadata.get("id", spec_file.stem)
                    files_str = ", ".join(f"`{d}`" for d in drifted)
                    self.issues.append(
                        f"[SPEC DRIFT] 🟠 MAJOR — Schema Drift Detected in `{spec_rel}` "
                        f"(id: {spec_id}). "
                        f"The following declared dependencies were modified in the last 48 h: "
                        f"{files_str}. "
                        f"Suggestion: queue Chief to audit this spec's intent against the "
                        f"updated code and regenerate the affected component."
                    )

    # --- 8. Placeholder / Stub Detection ------------------------------------

    def check_placeholder_stubs(self, since_minutes: int = 60) -> None:
        """
        Scans recently modified frontend and backend files for placeholder
        patterns — the kind the builder agent produces when it runs out of
        context or receives an empty spec.

        Patterns flagged:
          • TypeScript file whose entire content is just `export {};`
          • React component that only renders a <p>Placeholder… or similar
          • Any non-config file under 120 bytes that ends in .ts/.tsx/.py
          • File containing the literal string "Placeholder for … Implementation"
          • Empty types/index.ts (canonical type hub)
        """
        import time as _time

        stub_patterns = [
            re.compile(r'Placeholder for .* [Ii]mplementation'),
            re.compile(r'<p>Placeholder'),
            re.compile(r'// Implement .* here'),
            re.compile(r"^\s*export\s*\{\s*\}\s*;?\s*$", re.MULTILINE),
        ]

        cutoff = _time.time() - (since_minutes * 60)
        search_roots = [
            ROOT_DIR / "frontend" / "src",
            ROOT_DIR / "backend",
        ]
        ignore_dirs = {".venv", "node_modules", "__pycache__", ".git"}

        for root in search_roots:
            if not root.exists():
                continue
            for path in root.rglob("*"):
                # Skip irrelevant dirs/files
                if any(part in ignore_dirs for part in path.parts):
                    continue
                if path.suffix not in (".ts", ".tsx", ".py"):
                    continue
                if not path.is_file():
                    continue
                try:
                    mtime = path.stat().st_mtime
                    size = path.stat().st_size
                except OSError:
                    continue

                # Only files modified recently (or always check tiny files)
                is_recent = mtime >= cutoff
                rel = str(path.relative_to(ROOT_DIR))

                # Rule 1: Critically small non-config file
                if size < 120 and is_recent:
                    # Allow __init__.py files to be tiny
                    if path.name not in ("__init__.py", "vite-env.d.ts"):
                        self.issues.append(
                            f"[STUB] Suspiciously small file ({size} bytes): {rel}. "
                            f"Likely an empty stub left by the Builder. Needs regeneration."
                        )
                    continue  # no need to read content

                if not is_recent:
                    continue  # skip older files for performance

                try:
                    content = path.read_text(
                        encoding="utf-8", errors="replace")
                except OSError:
                    continue

                # Skip detector files to prevent false positives
                if path.name in ("tech_lead_agent.py",):
                    continue
                # Rule 2: Pattern matches
                for pat in stub_patterns:
                    if pat.search(content):
                        self.issues.append(
                            f"[STUB] Placeholder pattern detected in {rel}. "
                            f"The Builder generated stub code. "
                            f"Queue 'implement' with the correct spec to regenerate."
                        )
                        break

    # --- Full Scan ----------------------------------------------------------

    def run_full_scan(self) -> str:
        print("👔  Tech Lead is running static analysis on the factory floor...")
        self.check_memory_traps()
        self.check_ghost_directories()
        self.check_duplicate_configs()
        self.check_react_code_smells()
        self.check_pending_evolution()
        self.check_backend_integrity()
        self.check_spec_drift()
        self.check_placeholder_stubs()

        if not self.issues:
            return "✅ No critical heuristics flagged. The factory is clean."

        return "\n".join(f"- {issue}" for issue in self.issues)


# ---------------------------------------------------------------------------
# BRIEFING GENERATOR
# ---------------------------------------------------------------------------

def generate_morning_briefing() -> None:
    """
    Runs the full heuristics scan, sends results to the LLM Tech Lead,
    and writes DAILY_BRIEFING.md to the project root.
    """
    scanner = FactoryHeuristics()
    raw_data = scanner.run_full_scan()

    prompt = (
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        f"RAW HEURISTICS DATA:\n{raw_data}\n\n"
        f"Generate the DAILY_BRIEFING.md based strictly on this data."
    )

    print("🧠  Tech Lead is compiling the daily briefing...")
    briefing_content = query_llm(SYSTEM_PROMPT, prompt, model_tier="smart")

    if briefing_content:
        # Strip AI markdown fences if hallucinated
        content = briefing_content.strip()
        if content.startswith("```markdown"):
            content = content[11:].strip()
            if content.endswith("```"):
                content = content[:-3].strip()
        elif content.startswith("```"):
            content = content[3:].strip()
            if content.endswith("```"):
                content = content[:-3].strip()

        out_path = ROOT_DIR / "DAILY_BRIEFING.md"
        out_path.write_text(content, encoding="utf-8")
        print(f"✅  DAILY_BRIEFING.md compiled → {out_path}")
    else:
        # Fallback: write the raw scan data so the operator isn't left blind
        fallback = (
            f"# Daily Briefing — {datetime.now().strftime('%Y-%m-%d')}\n\n"
            f"> ⚠️  LLM unreachable. Raw scan data below.\n\n"
            f"{raw_data}\n"
        )
        out_path = ROOT_DIR / "DAILY_BRIEFING.md"
        out_path.write_text(fallback, encoding="utf-8")
        print("⚠️  LLM unavailable. Raw heuristics written to DAILY_BRIEFING.md.")


def get_insights_for_chief(include_stubs: bool = True) -> str:
    """
    Fast, LLM-free heuristics scan designed to be called inline by the Chief
    Agent before planning.  Returns a compact plain-text summary of issues so
    the Chief can factor them into its task queue without a full LLM round-trip.

    This is intentionally lightweight — it runs in < 1 second and never blocks
    the Nexus event loop.

    Returns an empty string when the factory is clean.
    """
    scanner = FactoryHeuristics()
    # Run only the fast, filesystem-based checks (skip spec-drift which calls git)
    scanner.check_memory_traps()
    scanner.check_ghost_directories()
    scanner.check_react_code_smells()
    scanner.check_backend_integrity()
    scanner.check_pending_evolution()
    if include_stubs:
        scanner.check_placeholder_stubs(since_minutes=120)

    if not scanner.issues:
        return ""

    lines = [
        f"=== SENIOR TECH LEAD SCAN ({len(scanner.issues)} issue(s) detected) ===",
    ]
    for i, issue in enumerate(scanner.issues, 1):
        lines.append(f"  {i}. {issue}")
    lines.append("=== END SENIOR SCAN ===")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# DEATH LOOP DIAGNOSIS  (On-Call Senior Architect)
# ---------------------------------------------------------------------------
DEATH_LOOP_SYSTEM_PROMPT = """
You are the ON-CALL SENIOR ARCHITECT (Level 9) for the Halilit Dark Factory.

A DEATH LOOP has been detected: the same task has failed multiple times with the same approach.

Your job:
1. Read the failure context provided.
2. Identify WHY the previous approach failed.
3. Prescribe a COMPLETELY DIFFERENT strategy.

RULES:
- NEVER suggest the same approach that already failed (same tool, same args).
- Be specific: name the exact tool or file to use instead.
- If the failure is a 'patch_component' anchor miss → mandate 'sandbox' or full file rewrite.
- If the failure is a missing import → mandate the exact import path fix.
- If the failure is a 'delegate_frontend' loop → mandate a design review step first.

Always end your response with exactly this format (one line):
SYSTEM OVERRIDE MANDATE: [your exact instruction for the Chief to follow]
"""


def diagnose_death_loop(failed_task_intent: str, previous_attempts: int = 1) -> str:
    """
    Called by nexus.py when consecutive_failures >= 2.
    Reads recent log + KANBAN context, calls LLM with DEATH_LOOP_SYSTEM_PROMPT,
    returns a mandate string the Chief will inject via senior_override.
    Safe fallback if LLM is unavailable.
    """
    # --- Gather context ---
    log_path = ROOT_DIR / "factory_logs" / "autopilot_halt.log"
    kanban_path = ROOT_DIR / "FACTORY_KANBAN.md"

    log_tail = ""
    if log_path.exists():
        lines = log_path.read_text(
            encoding="utf-8", errors="replace").splitlines()
        log_tail = "\n".join(lines[-50:])

    kanban_snippet = ""
    if kanban_path.exists():
        kanban_snippet = kanban_path.read_text(
            encoding="utf-8", errors="replace")[:2000]

    context_block = (
        f"FAILED TASK INTENT: {failed_task_intent}\n"
        f"PREVIOUS ATTEMPTS: {previous_attempts}\n\n"
        f"--- RECENT LOG (last 50 lines) ---\n{log_tail}\n\n"
        f"--- FACTORY_KANBAN (truncated) ---\n{kanban_snippet}\n"
    )

    try:
        mandate = query_llm(
            system_prompt=DEATH_LOOP_SYSTEM_PROMPT,
            user_message=context_block,
            model_tier="smart",
        )
        # Ensure mandate line is always present
        if "SYSTEM OVERRIDE MANDATE:" not in mandate:
            mandate += (
                "\n\nSYSTEM OVERRIDE MANDATE: Stop retrying the same approach. "
                "Use 'sandbox' tool to rewrite the target file from scratch, "
                "then verify with get_errors before continuing."
            )
        return mandate.strip()
    except Exception as exc:  # noqa: BLE001
        return (
            f"SYSTEM OVERRIDE MANDATE: LLM unavailable ({exc}). "
            "Do NOT retry the previous approach. "
            "Use 'sandbox' to rewrite the failing component from scratch."
        )


# ---------------------------------------------------------------------------
# BICAMERAL GOVERNANCE — Two-Key Pre-Flight Gatekeeper
# ---------------------------------------------------------------------------

GATEKEEPER_SYSTEM_PROMPT = """
You are the RUTHLESS SENIOR ARCHITECT and GATEKEEPER (Level 9) of the Halilit Dark Factory.
The Chief Agent has proposed a plan. Your job is to detect BULLSHIT before a single line of
code is touched.

ARCHITECTURE LAWS (these are absolute — any violation is an immediate VETO):
- Frontend: React 18 + Vite SPA. NEVER Next.js or any server-side rendering framework.
- State management: Zustand (app state) + React Query (server state). NEVER Redux, MobX, Jotai, or any store we don't already use.
- CSS: Tailwind CSS with design-system tokens (slate-*, blue-*, etc.). NEVER arbitrary hex colors. NEVER brittle CSS Grid when Flexbox satisfies the requirement.
- Backend: Python 3.11 + FastAPI. NEVER Django, NEVER Flask.
- Data purity: ZERO synthetic/mock/AI-generated data presented as real product data. Empty fields > fake fields.
- No new third-party libraries or frameworks unless an Evolution Proposal exists in specs/strategy/evolution/.
- Three Source Rules: Commercial (Halilit.com) owns prices/SKUs. Official (brand pages) owns specs/media. Contextual (review sites) owns reviews. NEVER mix ownership.
- If it is a frontend change, it must go through delegate_frontend (never 'implement' directly).
- If it is a backend change, it must go through delegate_data (never 'implement' directly).

YOUR VERDICT CRITERIA:
1. Does the plan violate any Architecture Law above? → VETO, provide the corrected strategy.
2. Does the plan introduce unnecessary complexity (10-file blast for a 2-line fix)? → VETO.
3. Does the plan suggest deprecated patterns (class components, inline styles, hardcoded data)? → VETO.
4. Is the plan architecturally sound and minimal? → APPROVE.

Respond ONLY with a JSON object. No markdown fences, no commentary outside the JSON:
{"status": "APPROVED" | "VETOED", "feedback": "<one paragraph: if VETOED explain the violation and prescribe the exact corrected strategy; if APPROVED write one confirming sentence>"}
"""


def veto_or_approve_plan(intent: str, proposed_plan: str) -> dict:
    """
    Bicameral Governance Gate — ruthless Senior Architect reviews the Chief's
    proposed plan before any code is written.

    Args:
        intent:        The operator's original intent / goal.
        proposed_plan: Human-readable summary of what the Chief intends to do.

    Returns:
        {"status": "APPROVED" | "VETOED", "feedback": "..."}

    Fails open (APPROVED) when the LLM is unavailable so the factory
    is never hard-blocked by a network outage.
    """
    user_message = (
        f"OPERATOR INTENT:\n{intent}\n\n"
        f"CHIEF'S PROPOSED PLAN:\n{proposed_plan}"
    )
    try:
        raw = query_llm(
            GATEKEEPER_SYSTEM_PROMPT,
            user_message,
            model_tier="smart",
            temperature=0.2,
        )
        raw = (raw or "").strip()
        # Strip any accidental markdown fences from the LLM
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()
        data = json.loads(raw)
        return {
            "status": data.get("status", "APPROVED"),
            "feedback": data.get("feedback", "Plan reviewed — no issues found."),
        }
    except json.JSONDecodeError as exc:
        # Malformed JSON from LLM — fail open
        return {
            "status": "APPROVED",
            "feedback": f"Gatekeeper parse error ({exc}). Plan auto-approved.",
        }
    except Exception as exc:  # noqa: BLE001
        # Network / API failure — fail open so factory is never hard-blocked
        return {
            "status": "APPROVED",
            "feedback": f"Gatekeeper LLM unavailable ({exc}). Plan auto-approved.",
        }


# ---------------------------------------------------------------------------
# BICAMERAL GOVERNANCE — MCP-exposed review wrapper
# ---------------------------------------------------------------------------

def review_architectural_plan(intent: str, proposed_plan: str) -> str:
    """
    MCP-callable wrapper around veto_or_approve_plan().

    Formats the verdict for terminal display in bright colours so the Operator
    can watch the AI police itself, and returns a human-readable verdict string
    suitable for injection into the Chief's context.

    Returns:
        A string starting with '[APPROVED]' or '[VETOED]' followed by the
        Tech Lead's one-paragraph verdict.
    """
    # Colourful pre-flight banner
    print("\033[93m\n" + "─" * 60 + "\033[0m")
    print("\033[93m🛡️  Tech Lead: Reviewing Chief's proposed architecture...\033[0m")
    print(f"\033[90m   Intent: {intent[:120]}\033[0m")

    verdict = veto_or_approve_plan(intent, proposed_plan)

    if verdict["status"] == "VETOED":
        print(
            f"\033[91m\n🛑  TECH LEAD VETO DETECTED! Forcing Chief to rewrite plan...\033[0m"
        )
        print(f"\033[91m   {verdict['feedback']}\033[0m")
        print("\033[93m" + "─" * 60 + "\033[0m\n")
        return f"[VETOED] {verdict['feedback']}"
    else:
        print(
            f"\033[92m\n✅  Tech Lead Approved. Plan is structurally sound.\033[0m"
        )
        print(f"\033[92m   {verdict['feedback']}\033[0m")
        print("\033[93m" + "─" * 60 + "\033[0m\n")
        return f"[APPROVED] {verdict['feedback']}"


if __name__ == "__main__":
    generate_morning_briefing()
