# Spec: TooLoo Workflow Alignment Refactor
**Target Repo:** `oripridan-dot/Halilit-Support-Center`
**Spec Type:** Architecture / Housekeeping
**Priority:** High — foundational compliance before any feature sprint proceeds
**Author:** TooLoo Governor
**Date:** 2026-02-22

---

## Problem Statement

The repo is ~70% aligned with the TooLoo workflow. Several structural violations
accumulate technical debt and will cause governance breakdowns as the product
scales. This spec defines all changes required to reach 100% compliance.

---

## Violations & Fixes

### 1. Git-Mind Protocol Violation — Manual Push Scripts

**Files:** `push_cifix.py`, `push_cifix2.py`

These scripts push files directly to a branch via the GitHub API, bypassing the
PR-review gate entirely. This is a direct violation of TooLoo Law: **all code
changes must land via a TooLoo-generated PR**.

**Action:** Delete both files. If an emergency direct-push capability is ever
needed, it must be implemented inside `tooloo-core` as an agent tool (not a
one-off script in the product repo) and must still open a PR, not push to a
branch directly.

---

### 2. Orphaned Launch Scripts — Root-Level Clutter

**Files:** `start-tooloo.sh`, `start.command`, `start_console.sh`,
`ignite_factory.sh`, `check_data_status.sh`, `clear_all_caches.sh`,
`test_functionality.sh`

These are ad-hoc operational scripts that have no spec backing them and are not
governed by any agent.

**Action:**
- If a script is still needed, move it to `scripts/` and add a single-sentence
  comment at the top referencing the spec or task that justifies it.
- If a script is stale / superseded, delete it.
- `ignite_factory.sh` — evaluate: if this is the TooLoo entrypoint, it belongs
  in the repo root but must be documented in `docs/WORKFLOW.md`. If it is purely
  a dev convenience, move to `scripts/`.

---

### 3. `local_autonomy/` — Misclassified Module

**Directory:** `local_autonomy/` (contains `facade_agent.py`, `warden.py`,
`escalation_webhook.py`, `dependency_drift.py`, `db_janitor.py`,
`product_mcp_server.py`)

These are **product-layer application components**, not TooLoo core agents.
`facade_agent.py` is a FastAPI router. `warden.py`, `db_janitor.py`, and
`dependency_drift.py` are backend services. `product_mcp_server.py` is the
product's MCP server.

Placing them in `local_autonomy/` implies they are TooLoo agents, which creates
confusion and makes routing logic ambiguous.

**Action:**
- Move `facade_agent.py`, `warden.py`, `escalation_webhook.py`,
  `dependency_drift.py`, `db_janitor.py` → `backend/local_autonomy/` (keep the
  module name, just nest it under `backend/` where all application logic lives).
- Move `product_mcp_server.py` → `backend/mcp/product_mcp_server.py` (MCP
  servers are protocol infrastructure, not local agents).
- Update all imports, FastAPI route registrations, and Docker entrypoints
  accordingly.
- Remove the now-empty root-level `local_autonomy/` directory.

---

### 4. `docs/` — Sprawl & Duplication

**Files in `docs/`:** `ARCHITECTURE.md`, `FACTORY_PIPELINE.md`,
`FEATURE_PROPOSAL_1771698095.md`, `LEARNED_GUIDELINES.md`,
`MEMORY_MANAGEMENT.md`, `QUICK_START.md`, `README.md`, `ROADMAP.md`,
`SPEC_DRIVEN_DEVELOPMENT.md`, `WORKFLOW.md`

There are 10 files. Several are redundant or stale.

**Action:**
- `ROADMAP.md` — keep, this is the PM's single source of truth. ✅
- `ARCHITECTURE.md` — keep, update to reflect post-refactor structure. ✅
- `WORKFLOW.md` — keep, ensure it documents the exact TooLoo PR loop. ✅
- `QUICK_START.md` — keep for onboarding. ✅
- `FACTORY_PIPELINE.md` — merge relevant content into `ARCHITECTURE.md`,
  then delete.
- `SPEC_DRIVEN_DEVELOPMENT.md` — merge into `WORKFLOW.md` (one paragraph),
  then delete.
- `MEMORY_MANAGEMENT.md` — if this documents TooLoo hippocampus behaviour,
  it belongs in `tooloo-core/docs/`, not here. Move and delete.
- `LEARNED_GUIDELINES.md` — archive to `docs/archive/` if historically
  relevant, otherwise delete.
- `FEATURE_PROPOSAL_1771698095.md` — this is a one-off proposal, not a
  standing document. If the feature is tracked in `specs/`, delete this.
  Otherwise move to `specs/interface/`.
- `README.md` inside `docs/` — remove, there is already a root `README.md`.

---

### 5. `nexus.py` at Repo Root — Undocumented Entrypoint

**File:** `nexus.py`

A `TooLoo.py` rename already happened (per CHANGELOG) but `nexus.py` still
exists at the root.

**Action:** Confirm whether `nexus.py` is still referenced anywhere. If not,
delete it. If still needed as an alias, add a one-line deprecation comment and
a tracking issue.

---

### 6. Branch Protection — Enforce PR-Only Merges

**Current state:** Unknown — no branch ruleset verified.

**Action:** Enable the following GitHub branch protection rules on `main`:
- Require pull request before merging (minimum 1 review — TooLoo auto-approve
  counts).
- Require status checks to pass (CI must be green).
- Disallow direct pushes (including from admins in production).
- Disallow force-pushes.

This is the mechanical lock that makes the Git-Mind Protocol enforceable.

---

### 7. `.tooloo.config` — Centralise TooLoo Configuration

**Current state:** Referenced in `product_mcp_server.py` but the file's location
and schema are not documented.

**Action:** Create `docs/TOOLOO_CONFIG.md` documenting every key in
`.tooloo.config`, its purpose, and its expected values. This file should be the
canonical reference consulted by all agents that read config.

---

## Execution Order

These changes should land as a **single PR** titled:
`chore: TooLoo workflow alignment refactor`

Suggested commit sequence within the branch:
1. Delete `push_cifix.py`, `push_cifix2.py`.
2. Relocate `local_autonomy/` → `backend/local_autonomy/` + update imports.
3. Move `product_mcp_server.py` → `backend/mcp/product_mcp_server.py`.
4. Consolidate `docs/` (merges + deletions).
5. Audit and relocate root-level scripts.
6. Delete or tombstone `nexus.py`.
7. Enable GitHub branch protection rules (done via GitHub UI or `gh` CLI,
   not a code commit).
8. Create `docs/TOOLOO_CONFIG.md`.

---

## Definition of Done

- [ ] Zero root-level ad-hoc scripts without a `scripts/` home and a comment.
- [ ] `local_autonomy/` lives under `backend/`.
- [ ] `product_mcp_server.py` lives under `backend/mcp/`.
- [ ] `push_cifix*.py` files are deleted.
- [ ] `docs/` contains exactly: `ARCHITECTURE.md`, `ROADMAP.md`, `WORKFLOW.md`,
      `QUICK_START.md`, `TOOLOO_CONFIG.md`.
- [ ] `main` branch has PR-required protection enabled.
- [ ] All CI checks pass on the alignment PR before merge.
