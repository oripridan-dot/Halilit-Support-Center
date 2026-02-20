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

    if status == "CLEAN":
        print("❌ Nothing to commit — working tree is clean.")
        return

    # 1. Always stage everything (handles DIRTY, STAGED, or mixed states)
    print("   Staging all changes...")
    if not dry_run:
        _run_git(["add", "-A"], capture=False)

    # 2. Get diff for message generation
    diff = get_git_diff(staged_only=True)
    if not diff:
        # Nothing staged yet — try unstaged
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

    # 4. Write changelog NOW (before the commit) so it gets staged with everything
    tag = get_current_version_tag() or "unreleased"
    changelog_entry = generate_changelog_entry(diff, tag)
    if not dry_run:
        update_changelog(tag, changelog_entry)
        # Re-stage after writing changelog so it's included in the commit
        _run_git(["add", "-A"], capture=False)

    if dry_run:
        print("\n[DRY RUN] Would have committed with the above message.")
        print("[DRY RUN] Changelog entry:")
        print(changelog_entry)
        return

    # 5. Commit (disable GPG signing — avoids failures in dev containers)
    result = _run_git(["-c", "commit.gpgsign=false", "commit", "-m", msg])
    if result.returncode != 0:
        combined = (result.stdout + "\n" + result.stderr).strip()
        print(f"❌ Commit failed:\n{combined}")
        return

    # 6. Push — resilient: no-upstream → set-upstream, diverged → merge/force-with-lease
    print("   Pushing to origin...")
    push_result = _run_git(["push"])
    if push_result.returncode != 0:
        stderr = push_result.stderr.strip()
        if "no upstream branch" in stderr or "has no upstream" in stderr or "set-upstream" in stderr:
            # Branch is new — publish it automatically
            print(f"   🔗 No upstream set — publishing branch '{branch}'...")
            push_result = _run_git(
                ["push", "--set-upstream", "origin", branch])
        elif "non-fast-forward" in stderr or "rejected" in stderr:
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
            # Commit succeeded — push is optional. Warn but don't treat as failure.
            print("   ⚠️  Push failed (no remote access or permission denied).")
            print(f"      ({push_result.stderr.strip()})")
            print("   ✅ Commit saved locally — push when origin is available.")
            return
    print("✅ Code synced to repository.")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    dry = "--dry-run" in sys.argv or "-n" in sys.argv
    commit_and_push(dry_run=dry)


# ---------------------------------------------------------------------------
# Feature Branch Lifecycle (Pillar: Autonomous Rollbacks)
# ---------------------------------------------------------------------------

def create_feature_branch(feature_slug: str) -> str:
    """
    Create and checkout a new AI feature branch before any code is touched.

    Branch name: ai-<feature_slug>-<short_sha>
    Returns the branch name, or the current branch name if creation fails
    (safe fallback — we never block the build over a branch failure).
    """
    import re as _re
    # Sanitize slug: lowercase, replace spaces/special chars with hyphens
    clean_slug = _re.sub(r"[^\w]+", "-", feature_slug.lower()).strip("-")[:40]
    # Short SHA for uniqueness
    sha_result = _run_git(["rev-parse", "--short", "HEAD"])
    short_sha = sha_result.stdout.strip(
    )[:7] if sha_result.returncode == 0 else "x"
    branch_name = f"ai-{clean_slug}-{short_sha}"

    result = _run_git(["checkout", "-b", branch_name])
    if result.returncode == 0:
        print(f"🌿  Feature branch created: {branch_name}")
        return branch_name

    # Branch may already exist — try checking it out
    result2 = _run_git(["checkout", branch_name])
    if result2.returncode == 0:
        print(f"🌿  Resumed feature branch: {branch_name}")
        return branch_name

    # Fallback: stay on current branch
    current = get_current_branch()
    print(f"⚠️  Could not create feature branch — continuing on: {current}")
    return current


def rollback_branch(branch_name: str, base_branch: str = "v9.7.0") -> bool:
    """
    Hard-reset to the last clean commit and optionally delete the feature branch.
    Used when the inner loop exhausts its retries without passing verification.

    Steps:
        1. git reset --hard HEAD  (discard uncommitted changes on feature branch)
        2. git checkout <base_branch>
        3. git branch -D <feature_branch>   (delete the failed branch)

    Returns True if rollback succeeded.
    """
    if branch_name == base_branch:
        print("⚠️  Cannot rollback — already on base branch. Resetting to HEAD...")
        _run_git(["reset", "--hard", "HEAD"])
        _run_git(["clean", "-fd"])
        return True

    print(f"🚨  Rolling back failed branch: {branch_name} → {base_branch}")

    # 1. Discard any uncommitted changes on the feature branch
    _run_git(["reset", "--hard", "HEAD"])
    _run_git(["clean", "-fd"])

    # 2. Switch back to base
    checkout = _run_git(["checkout", base_branch])
    if checkout.returncode != 0:
        print(f"❌  Rollback failed: could not checkout {base_branch}")
        return False

    # 3. Delete the failed branch
    _run_git(["branch", "-D", branch_name])
    print(f"✅  Rolled back. Working tree restored to {base_branch}.")
    return True


def merge_feature_branch(feature_branch: str, base_branch: str = "v9.7.0") -> bool:
    """
    Squash-merge a successful feature branch into the base branch.
    Called by the Chief after the Gatekeeper approves.

    Returns True if merge succeeded.
    """
    if feature_branch == base_branch:
        return True  # Nothing to merge

    print(f"🔀  Merging {feature_branch} → {base_branch}...")
    checkout = _run_git(["checkout", base_branch])
    if checkout.returncode != 0:
        print(f"❌  Cannot checkout base branch {base_branch} for merge.")
        return False

    merge = _run_git(["merge", "--squash", feature_branch])
    if merge.returncode != 0:
        print(f"❌  Merge failed:\n{merge.stderr.strip()}")
        return False

    print(f"✅  Squash-merged {feature_branch} into {base_branch}.")
    # Delete the feature branch
    _run_git(["branch", "-D", feature_branch])
    return True


def generate_failure_report(
    feature_slug: str,
    original_prompt: str,
    error_summary: str,
    rounds_attempted: int,
    branch_name: str,
) -> str:
    """
    Write a FACTORY_FAILURE_REPORT.md to the project root explaining exactly
    why the autonomous cycle failed — saves operators from untangling broken code.

    Returns the absolute path to the report file.
    """
    from datetime import datetime
    report_path = ROOT_DIR / "FACTORY_FAILURE_REPORT.md"
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    content = f"""# 🏭 Factory Failure Report

**Feature:** {feature_slug}
**Date:** {timestamp}
**Branch (auto-rolled back):** `{branch_name}`
**Rounds Attempted:** {rounds_attempted}

---

## Original Request

> {original_prompt}

---

## Failure Analysis

The autonomous improvement loop exhausted **{rounds_attempted} rounds** without
producing code that passed all Verification Commands.

### Last Error Encountered

```
{error_summary[:3000]}
```

---

## What Happened

1. The Builder generated code and the Sandbox Executor ran the Verification Commands.
2. The code failed the automated checks on every round.
3. After {rounds_attempted} attempts, the system halted and rolled back `{branch_name}`.
4. The working tree has been restored to a clean state.

---

## Recommended Next Steps

1. **Review the error above** — copy the exact error message and tell the Chief:
   `"The last attempt failed with: [paste error]. Fix it."`
2. **Simplify the request** — break it into smaller, atomic tasks.
3. **Check `specs/repairs/current_fix.md`** — the Watchdog may have generated a
   detailed repair spec already.

---

*Generated automatically by the Dark Factory Autonomous Pipeline.*
"""
    report_path.write_text(content, encoding="utf-8")
    print(f"📋  Failure report written → FACTORY_FAILURE_REPORT.md")
    return str(report_path)
