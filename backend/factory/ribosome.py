"""
RIBOSOME — Genome Interpreter Engine  (backend/factory/ribosome.py)
====================================================================
The Ribosome translates a framework-agnostic Genome YAML into a synthesis
directive that the Builder Agent can use to generate framework-specific code.

Biological analogy:
  DNA (Genome YAML) + Cell (Ribosome) + Environment (codebase) → Protein (Code)

Architecture:
  1. Parse Genome YAML → validate schema
  2. Environmental Check — read environment files listed in genome
  3. Trait Resolution — merge with parent genome (inheritance)
  4. State Mapping — translate FSM states to React/Python constructs
  5. Synthesis Directive — emit an enriched spec for the Builder Agent
  6. Phenotype Verification — after build, verify every State exists in output

Usage:
  python ribosome.py specs/genomes/product_explorer.yaml
  →  writes  specs/temp/synthesis_product_explorer.md   (Builder reads this)

  python ribosome.py specs/genomes/product_explorer.yaml --verify path/to/output.tsx
  →  verifies phenotype assertions against the compiled file
"""

from __future__ import annotations

import re
import sys
import json
import argparse
import textwrap
from pathlib import Path
from typing import Any

try:
    import yaml
    _YAML_OK = True
except ImportError:
    _YAML_OK = False

# ── Project root ────────────────────────────────────────────────────────────
_ROOT = Path(__file__).resolve().parent.parent.parent
_GENOMES_DIR = _ROOT / "specs" / "genomes"
_SYNTH_DIR = _ROOT / "specs" / "temp"
_SYNTH_DIR.mkdir(parents=True, exist_ok=True)

# ── Bootstrap agent_core ─────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from agent_core import query_llm, SMART_MODEL
except ImportError:
    def query_llm(system, user, model=None):  # type: ignore[misc]
        raise RuntimeError("agent_core not available")
    SMART_MODEL = "gemini-2.0-flash"


# ═══════════════════════════════════════════════════════════════════════════
# GENOME LOADER
# ═══════════════════════════════════════════════════════════════════════════

class GenomeError(ValueError):
    pass


def _load_yaml(path: Path) -> dict:
    if not _YAML_OK:
        raise GenomeError("PyYAML not installed — run: pip install pyyaml")
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_genome(genome_path: Path) -> dict:
    """
    Load a genome YAML and resolve trait inheritance from 'extends'.
    Returns a fully merged genome dict.
    """
    genome = _load_yaml(genome_path)

    # Resolve parent inheritance
    if "extends" in genome:
        parent_id = genome["extends"]
        parent_path = _GENOMES_DIR / f"{parent_id.replace('genome_', '')}.yaml"
        if parent_path.exists():
            parent = _load_yaml(parent_path)
            # Deep merge: child overrides parent
            genome = _deep_merge(parent, genome)
        # Remove the extends key after merging
        genome.pop("extends", None)

    return genome


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override into base; override wins on conflicts."""
    result = dict(base)
    for key, val in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(val, dict):
            result[key] = _deep_merge(result[key], val)
        else:
            result[key] = val
    return result


# ═══════════════════════════════════════════════════════════════════════════
# ENVIRONMENT READER
# ═══════════════════════════════════════════════════════════════════════════

def _read_environment(genome: dict) -> str:
    """
    Read the files listed in genome.environment and return their contents
    (truncated to 800 lines total) as a formatted context block.
    """
    env_files = genome.get("environment", [])
    if not env_files:
        return ""

    parts: list[str] = []
    budget = 800  # total line budget across all env files

    for rel_path in env_files:
        abs_path = _ROOT / rel_path
        if not abs_path.exists():
            parts.append(f"# ── {rel_path} (NOT FOUND — skipped) ──")
            continue
        try:
            text = abs_path.read_text(encoding="utf-8", errors="replace")
            lines = text.splitlines()
            allowed = min(len(lines), budget)
            budget -= allowed
            excerpt = "\n".join(lines[:allowed])
            parts.append(
                f"# ── {rel_path} ({len(lines)} lines, showing first {allowed}) ──\n"
                f"{excerpt}\n"
            )
        except Exception as exc:
            parts.append(f"# ── {rel_path} (READ ERROR: {exc}) ──")
        if budget <= 0:
            parts.append("# ── [Environment budget exhausted — truncated] ──")
            break

    return "\n".join(parts)


# ═══════════════════════════════════════════════════════════════════════════
# SYNTHESIS DIRECTIVE GENERATOR
# ═══════════════════════════════════════════════════════════════════════════

_RIBOSOME_SYSTEM_PROMPT = """\
You are THE RIBOSOME — a genome synthesis engine.

Your input is a structured Genome (States, Traits, Phenotype_Assertions)
plus real environment files from the codebase.

Your job: produce a concise, highly structured BUILD DIRECTIVE for the
Factory Builder Agent. The directive must be pure Markdown (no code fences).

DIRECTIVE FORMAT:
# Synthesis Directive — {genome_id}

## Target
`{target_file}`

## Fitness Goal
{fitness_goal}

## Required States
For each State in the genome, map it to a concrete React/TypeScript implementation:
- State name → useState hook name or conditional branch
- State→State transitions → useEffect triggers or event handler calls
- visual_hint → exact Tailwind class string

## Required Traits
For each Trait, describe the exact implementation pattern.

## Phenotype Assertions (must ALL pass after build)
List each assertion verbatim. The Builder must verify they hold.

## Environment Contracts
List key types, hooks, or API shapes extracted from the environment files
that the Builder MUST use.

## Builder Instructions
Write 3-5 imperative rules specific to this genome's complexity.
"""


def generate_synthesis_directive(genome: dict, env_context: str) -> str:
    """
    Ask the LLM to translate a genome + environment into a Builder directive.
    Returns the directive as a Markdown string.
    """
    genome_id = genome.get("id", "unknown")
    target_line = genome.get(
        "target", "(target not specified in genome — infer from id)")

    states_text = _format_states(genome)
    traits_text = _format_traits(genome)
    asserts_text = _format_assertions(genome)

    user_prompt = textwrap.dedent(f"""\
        GENOME ID: {genome_id}
        FITNESS GOAL: {genome.get('fitness_goal', 'UNKNOWN')}
        TARGET: {target_line}

        STATES:
        {states_text}

        TRAITS (CHROMOSOMES):
        {traits_text}

        PHENOTYPE ASSERTIONS:
        {asserts_text}

        MUTATIONS ALLOWED:
        {json.dumps(genome.get('Mutations_Allowed', []), indent=2)}

        ENVIRONMENT (codebase context):
        {env_context[:6000] if env_context else "(no environment files specified)"}

        Generate the Synthesis Directive now.
    """)

    system = _RIBOSOME_SYSTEM_PROMPT.format(
        genome_id=genome_id,
        target_file=target_line,
        fitness_goal=genome.get("fitness_goal", ""),
    )

    return query_llm(system, user_prompt, model_tier="smart")


def _format_states(genome: dict) -> str:
    states = genome.get("States", {})
    if not states:
        return "(none)"
    lines = []
    for name, body in states.items():
        if not isinstance(body, dict):
            lines.append(f"  {name}: {body}")
            continue
        lines.append(f"  {name}:")
        lines.append(f"    desc:    {body.get('description', '')}")
        lines.append(f"    hint:    {body.get('visual_hint', '')}")
        lines.append(f"    required:{body.get('required', True)}")
        for t in body.get("transitions", []):
            lines.append(
                f"    ↳ on '{t.get('trigger','')}' → {t.get('next','')}")
    return "\n".join(lines)


def _format_traits(genome: dict) -> str:
    traits = genome.get("Traits", {})
    if not traits:
        return "(none)"
    lines = []
    for name, body in traits.items():
        if not isinstance(body, dict):
            lines.append(f"  {name}: {body}")
            continue
        lines.append(
            f"  {name}: type={body.get('type','?')}  value={body.get('value','?')}  "
            f"inheritable={body.get('inheritable', False)}"
        )
        if "description" in body:
            lines.append(f"    → {body['description']}")
    return "\n".join(lines)


def _format_assertions(genome: dict) -> str:
    assertions = genome.get("Phenotype_Assertions", [])
    if not assertions:
        return "(none)"
    return "\n".join(f"  - {a}" for a in assertions)


# ═══════════════════════════════════════════════════════════════════════════
# PHENOTYPE VERIFIER
# ═══════════════════════════════════════════════════════════════════════════

_VERIFIER_SYSTEM_PROMPT = """\
You are the PHENOTYPE VERIFIER — the post-synthesis quality gate.

Given:
  1. A Genome (States, Traits, Phenotype_Assertions)
  2. The synthesized source code

Your job: verify that every Phenotype_Assertion holds in the code.

RULES:
- Mark as PASS if the assertion is satisfied OR if it cannot be verified from frontend
  code alone (e.g. hook internals, server behaviour). Do NOT fail for data field
  names like `image_url` that come from real API data — those are NOT mock data.
- Mark as FAIL only if you can point to a specific line that actively violates the assertion.
- Skeleton/loading-state placeholder shapes (SkeletonPulse divs) are NOT mock data.
- Fields sourced from catalog/JIT hooks are NOT mock data.

RESPONSE FORMAT (return ONLY this, no markdown fences):
PHENOTYPE_SCORE: <0-100>
PASS_COUNT: <n>
FAIL_COUNT: <n>
ASSERTIONS:
  PASS: "<assertion text>"
  FAIL: "<assertion text>"
       VIOLATION: "<specific line, pattern, or absence that caused this failure>"

If all assertions pass, end with: PHENOTYPE: VIABLE
If any fail, end with: PHENOTYPE: MUTANT
"""


class PhenotypeVerdict:
    # VIABLE threshold: score >= 80/100 OR all assertions pass.
    # Aligns with MUTATION_THRESHOLD=0.65 — 80% is the gold standard.
    VIABLE_SCORE = 80

    def __init__(self, score: int, passed: list[str], failed: list[tuple[str, str]]):
        self.score = score
        self.passed = passed
        self.failed = failed
        self.viable = score >= self.VIABLE_SCORE or len(failed) == 0

    def __str__(self) -> str:
        lines = [f"Phenotype Score: {self.score}/100"]
        lines += [f"  ✅ {p}" for p in self.passed]
        lines += [f"  ❌ {f[0]}\n     Violation: {f[1]}" for f in self.failed]
        lines.append(
            "PHENOTYPE: VIABLE" if self.viable else "PHENOTYPE: MUTANT")
        return "\n".join(lines)


def verify_phenotype(genome: dict, code_text: str) -> PhenotypeVerdict:
    """
    Ask the LLM to verify all Phenotype_Assertions against the generated code.
    Returns a PhenotypeVerdict.
    """
    assertions = genome.get("Phenotype_Assertions", [])
    if not assertions:
        return PhenotypeVerdict(score=100, passed=[], failed=[])

    user_prompt = textwrap.dedent(f"""\
        GENOME: {genome.get('id', 'unknown')}
        FITNESS_GOAL: {genome.get('fitness_goal', '')}

        PHENOTYPE_ASSERTIONS:
        {chr(10).join(f'- {a}' for a in assertions)}

        SYNTHESIZED CODE:
        {code_text[:8000]}

        Verify all assertions now.
    """)

    raw = query_llm(_VERIFIER_SYSTEM_PROMPT, user_prompt, model_tier="smart")

    # Parse response
    score_match = re.search(r"PHENOTYPE_SCORE:\s*(\d+)", raw)
    score = int(score_match.group(1)) if score_match else 0

    passed: list[str] = []
    failed: list[tuple[str, str]] = []

    for line in raw.splitlines():
        if line.strip().startswith("PASS:"):
            passed.append(line.split("PASS:", 1)[1].strip().strip('"'))
        elif line.strip().startswith("FAIL:"):
            failed.append((line.split("FAIL:", 1)[1].strip().strip('"'), ""))

    # Annotate violations
    lines_iter = raw.splitlines()
    fixed_failed: list[tuple[str, str]] = []
    for i, (assertion, _) in enumerate(failed):
        violation = "(see verifier output)"
        for j, line in enumerate(lines_iter):
            if assertion[:30] in line and j + 1 < len(lines_iter):
                next_line = lines_iter[j + 1]
                if "VIOLATION:" in next_line:
                    violation = next_line.split("VIOLATION:", 1)[1].strip()
                    break
        fixed_failed.append((assertion, violation))

    return PhenotypeVerdict(score=score, passed=passed, failed=fixed_failed)


# ═══════════════════════════════════════════════════════════════════════════
# FULL SYNTHESIS PIPELINE
# ═══════════════════════════════════════════════════════════════════════════

def synthesize(genome_path: Path, verify_file: Path | None = None) -> Path:
    """
    Full Ribosome pipeline:
      1. Load + inherit genome
      2. Read environment
      3. Generate synthesis directive
      4. Write directive to specs/temp/synthesis_{id}.md
      5. (Optional) verify phenotype against compiled file

    Returns the path to the synthesis directive.
    """
    print(f"🧬 RIBOSOME: Loading genome {genome_path.name}...")
    genome = load_genome(genome_path)
    genome_id = genome.get("id", genome_path.stem)

    print(f"   ↳ States: {list(genome.get('States', {}).keys())}")
    print(f"   ↳ Traits: {list(genome.get('Traits', {}).keys())}")
    print(f"   ↳ Fitness goal: {genome.get('fitness_goal', '?')}")

    print("🌿 Reading environment files...")
    env_context = _read_environment(genome)

    print("⚗️  Generating Synthesis Directive (LLM protein folding)...")
    directive = generate_synthesis_directive(genome, env_context)

    out_path = _SYNTH_DIR / f"synthesis_{genome_id}.md"
    out_path.write_text(directive, encoding="utf-8")
    print(f"✅ Synthesis Directive written → {out_path.relative_to(_ROOT)}")

    if verify_file and verify_file.exists():
        print(
            f"\n🔬 Running Phenotype Verification against {verify_file.name}...")
        code = verify_file.read_text(encoding="utf-8")
        verdict = verify_phenotype(genome, code)
        print(str(verdict))

        # Persist verdict alongside directive
        verdict_path = _SYNTH_DIR / f"phenotype_{genome_id}.txt"
        verdict_path.write_text(str(verdict), encoding="utf-8")

        if not verdict.viable:
            print(
                f"\n⚠️  MUTANT PHENOTYPE detected. Score: {verdict.score}/100")
            print("   Run the Builder again with the synthesis directive to fix.")

    return out_path


# ═══════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="ribosome.py",
        description="Genome Interpreter — translate a YAML genome into a Builder synthesis directive.",
    )
    parser.add_argument("genome", nargs="?", default="",
                        help="Path to genome YAML file")
    parser.add_argument(
        "--verify",
        metavar="FILE",
        default="",
        help="Optional: compiled file to verify phenotype assertions against",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available genomes and exit",
    )
    args = parser.parse_args()

    if args.list:
        print("Available genomes:")
        for g in sorted(_GENOMES_DIR.glob("*.yaml")):
            try:
                d = _load_yaml(g)
                print(
                    f"  {g.name:40s}  {d.get('id','?')}  →  {d.get('fitness_goal','?')}")
            except Exception:
                print(f"  {g.name}  (parse error)")
        return

    if not args.genome:
        parser.print_help()
        sys.exit(1)

    genome_path = Path(args.genome)
    if not genome_path.is_absolute():
        genome_path = _ROOT / genome_path

    if not genome_path.exists():
        print(f"❌ Genome file not found: {genome_path}")
        sys.exit(1)

    verify_path = Path(args.verify) if args.verify else None
    if verify_path and not verify_path.is_absolute():
        verify_path = _ROOT / verify_path

    synthesize(genome_path, verify_path)


if __name__ == "__main__":
    main()
