# LEARNED GUIDELINES — Persistent Agent Memory

> Auto-maintained by the **Reflect Agent** (Chief → Recovery Mode → `reflect` tool).
> Injected into every agent's context via `get_project_context()`.
> **Do not edit manually** — append-only via the `reflect` workflow.

---

## How to Read This File

Each entry is structured as:

```
### [YYYY-MM-DD] <Short Title>
**Symptom:** what went wrong
**Root Cause:** why it happened
**Fix:** what was done to resolve it
**Lesson:** rule to prevent recurrence
```

---

## Guidelines

_(No lessons recorded yet. The Reflect Agent will populate this section as the system self-heals.)_

### [2026-02-19] Catalog Build Failure
**Symptom:** Product catalog build process failed unexpectedly.
**Root Cause:** A transient network issue interrupted data synchronization.
**Fix:** Implemented retry logic for catalog data synchronization.
**Lesson:** ALWAYS implement retry mechanisms for transient errors.

### [2026-02-19] TypeScript Linting Errors
**Symptom:** TypeScript code failed linting checks.
**Root Cause:** Newly optimized code introduced linting violations.
**Fix:** Fixed linting errors in InventoryView.tsx file.
**Lesson:** ALWAYS run linters after code optimization.

### [2026-02-19] TS/Lint After Optimization
**Symptom:** TypeScript linting errors after code optimization.
**Root Cause:** Optimization introduced linting violations.
**Fix:** Fixed linting errors in ProductDetailView.tsx.
**Lesson:** ALWAYS lint check after refactoring.

### [2026-02-19] Lint Before Committing
**Symptom:** Debugging revealed TypeScript/linting errors.
**Root Cause:** Un-linted code was introduced.
**Fix:** Resolved the TypeScript/lint errors.
**Lesson:** ALWAYS lint code before committing.
