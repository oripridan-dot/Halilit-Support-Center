"""
REPOSITORY MANAGER AGENT — backend/factory/repo_agent.py  (Level 8)
=====================================================================
Handles all git operations: semantic commit messages, changelog management,
and professional version control standards.

Usage:
    python repo_agent.py             # Audit, commit, and push changes
    python repo_agent.py --dry-run   # Preview commit message only
"""

import sys
import subprocess
import os
import re
from pathlib import Path

# agent_core.py lives in the same directory
sys.path.insert(0, str(Path(__file__).parent))
from agent_core import query_llm  # noqa: E402

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

SYSTEM_PROMPT = """
You are the REPOSITORY MANAGER for a professional software product.
Your job is to maintain world-class version control standards.

RULES:
1. **Semantic Commits:** Use Conventional Commits format ONLY.
   Allowed types: feat, fix, docs, style, refactor, test, chore, perf, ci
   Format: type(scope): description  (all lowercase, no period, max 72 chars)
   Examples:
     feat(inventory): add stock status indicator column
     fix(jit): handle empty catalog response gracefully
     refactor(frontend): extract product card into reusable component
     chore(deps): update pnpm lockfile
2. **Scope:** Use the most specific area affected (ui, inventory, jit, api,
   backend, frontend, factory, docs, deps, config).
3. **No Fluff:** Output ONLY the single-line commit message — no explanation,
   no markdown, no quotes.
4. **One Line:** The commit message must be exactly one line.
"""

CHANGELOG_SYSTEM_PROMPT = """
You are a technical writer summarizing code changes for a developer audience.
Write concise, bullet-point changelog entries.
Format each entry as: - [type] Brief description of what changed
Group under a header if multiple changes. No intro text, no markdown fences.
"""


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def _run_git(args: list[str], capture: bool = True) -> subprocess.CompletedProcess:
    """Run a git command in the repo root."""
    return subprocess.run(
        ["git"] + args,
        cwd=str(ROOT_DIR),
        capture_output=capture,
        text=True,
    )


def get_git_diff(staged_only: bool = True) -> str:
    """Returns the current diff (staged by default, falls back to unstaged)."""
    diff = _run_git(["diff", "--cached"]).stdout.strip()
    if not diff and not staged_only:
        diff = _run_git(["diff"]).stdout.strip()
    return diff


def get_git_status() -> str:
    """Returns 'CLEAN', 'STAGED', 'DIRTY', or 'UNKNOWN'."""
    try:
        result = _run_git(["status", "--porcelain"])
        output = result.stdout.strip()
        if not output:
            return "CLEAN"
        # Check if anything is staged
        staged = any(
            line[:2][0] in "MADRC" for line in output.splitlines() if len(line) >= 2)
        return "STAGED" if staged else "DIRTY"
    except Exception:
        return "UNKNOWN"


def get_current_branch() -> str:
    """Returns the current git branch name."""
    result = _run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    return result.stdout.strip() or "unknown"


def get_current_version_tag() -> str | None:
    """Returns the latest semver tag, or None if none exist."""
    result = _run_git(["describe", "--tags", "--abbrev=0", "--match", "v*"])
    if result.returncode == 0:
        return result.stdout.strip()
    return None


# ---------------------------------------------------------------------------
# AI generation
# ---------------------------------------------------------------------------

def generate_commit_message(diff: str) -> str | None:
    """Use LLM to generate a Conventional Commits message from the diff."""
    if not diff:
        return None

    prompt = (
        "Analyze this git diff and generate a SINGLE LINE Semantic Commit Message "
        "in Conventional Commits format (type(scope): description).\n\n"
        f"DIFF:\n{diff[:4000]}\n\n"
        "Output ONLY the commit message — one line, no quotes, no explanation."
    )

    result = query_llm(SYSTEM_PROMPT, prompt, model_tier="fast")
    if not result:
        return None

    # Sanitize: keep only the first non-empty line
    lines = [l.strip() for l in result.strip().splitlines() if l.strip()]
    msg = lines[0] if lines else None

    # Strip accidental markdown fences or quotes
    if msg:
        msg = msg.strip("`\"'")

    return msg


def generate_changelog_entry(diff: str, version: str) -> str:
    """Use LLM to generate a human-readable changelog entry."""
    if not diff:
        return "- chore: minor updates\n"

    prompt = (
        f"Summarize the following git diff as changelog bullet points for version {version}.\n\n"
        f"DIFF:\n{diff[:4000]}\n\n"
        "Use format: - [type] description. Bullet points only, no intro text."
    )

    result = query_llm(CHANGELOG_SYSTEM_PROMPT, prompt, model_tier="fast")
    return result.strip() if result else "- chore: minor updates"


# ---------------------------------------------------------------------------
# Changelog management
# ---------------------------------------------------------------------------

def update_changelog(version: str, changes: str) -> None:
    """Prepend a new entry to CHANGELOG.md."""
    log_path = ROOT_DIR / "CHANGELOG.md"
    current_content = log_path.read_text(
        encoding="utf-8") if log_path.exists() else "# Changelog\n\n"

    from datetime import date
    today = date.today().isoformat()
    new_entry = f"## [{version}] — {today}\n{changes}\n\n"

    log_path.write_text(new_entry + current_content, encoding="utf-8")
    print("📝 Changelog updated.")


# ---------------------------------------------------------------------------
# Semantic version bump
# ---------------------------------------------------------------------------

def bump_patch_version(current: str) -> str:
    """Increment the patch segment of a semver tag: v1.2.3 → v1.2.4."""
    match = re.match(r"^(v?)(\d+)\.(\d+)\.(\d+)(.*)$", current)
    if not match:
        return current
    prefix, major, minor, patch, suffix = match.groups()
    return f"{prefix}{major}.{minor}.{int(patch) + 1}{suffix}"


# ---------------------------------------------------------------------------
# Main workflow
# ---------------------------------------------------------------------------

def commit_and_push(dry_run: bool = False) -> None:
    """Stage all changes, generate a semantic commit message, commit, and push."""
    print("👮 Repo Agent: Auditing repository...")

    branch = get_current_branch()
    status = get_git_status()
    print(f"   Branch : {branch}")
    print(f"   Status : {status}")

    # 1. Stage everything if nothing is staged yet
    if status == "DIRTY":
        print("   Staging all changes...")
        if not dry_run:
            _run_git(["add", "."], capture=False)
    elif status == "CLEAN":
        print("❌ Nothing to commit — working tree is clean.")
        return

    # 2. Get diff for message generation
    diff = get_git_diff(staged_only=True)
    if not diff:
        # Fall back to full diff after staging
        diff = get_git_diff(staged_only=False)

    if not diff:
        print("❌ No changes detected after staging.")
        return

    # 3. Generate semantic commit message
    print("   Generating Semantic Commit Message...")
    msg = generate_commit_message(diff)
    if not msg:
        msg = "chore: update files"
        print(f"   ⚠️  LLM unavailable — using fallback message.")

    print(f"   ✅ Commit: {msg}")

    if dry_run:
        print("\n[DRY RUN] Would have committed with the above message.")
        print("[DRY RUN] Changelog entry:")
        tag = get_current_version_tag() or "v0.0.1"
        entry = generate_changelog_entry(diff, tag)
        print(entry)
        return

    # 4. Commit (disable GPG signing — avoids failures in dev containers)
    result = _run_git(["-c", "commit.gpgsign=false", "commit", "-m", msg])
    if result.returncode != 0:
        combined = (result.stdout + "\n" + result.stderr).strip()
        print(f"❌ Commit failed:\n{combined}")
        return

    # 5. Update changelog with the current tag
    tag = get_current_version_tag() or "unreleased"
    changelog_entry = generate_changelog_entry(diff, tag)
    update_changelog(tag, changelog_entry)

    # 6. Push — resilient: merge-pull fallback → force-with-lease
    print("   Pushing to origin...")
    push_result = _run_git(["push"])
    if push_result.returncode != 0:
        stderr = push_result.stderr.strip()
        if "non-fast-forward" in stderr or "rejected" in stderr:
            # Remote has diverged — pull with merge then retry
            print("   ↩️  Remote diverged. Pulling (merge) then retrying...")
            pull = _run_git(["-c", "commit.gpgsign=false",
                             "pull", "--no-rebase", "--no-edit"])
            if pull.returncode == 0:
                push_result = _run_git(["push"])
            if push_result.returncode != 0:
                # Last resort: force-with-lease (safe overwrite)
                print("   ⚡ Merge didn't resolve — force-pushing (with lease)...")
                push_result = _run_git(["push", "--force-with-lease"])
        if push_result.returncode != 0:
            print("   ⚠️  Push failed — no upstream or permission denied.")
            print(f"      ({push_result.stderr.strip()})")
            return
    print("✅ Code synced to repository.")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    dry = "--dry-run" in sys.argv or "-n" in sys.argv
    commit_and_push(dry_run=dry)
