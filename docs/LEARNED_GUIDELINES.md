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

### [2026-02-19] Validate Catalog Data Format
**Symptom:** Product catalog build failed.
**Root Cause:** Invalid data format in catalog.
**Fix:** Added validation step to build.
**Lesson:** ALWAYS validate external data inputs.

### [2026-02-19] Incorrect Catalog Organizer Spec
**Symptom:** Product catalog build failed.
**Root Cause:** The catalog organizer spec was misconfigured.
**Fix:** Corrected misconfigured catalog organizer spec.
**Lesson:** ALWAYS validate organizer specifications before builds.

### [2026-02-19] Agent Autonomy Improvements
**Symptom:** Insufficient failure detail provided.
**Root Cause:** Unknown.
**Fix:** Not documented.
**Lesson:** ALWAYS provide detailed failure context when calling 'reflect'.

### [2026-02-19] Agent Autonomy Improvements
**Symptom:** Insufficient failure detail provided.
**Root Cause:** Unknown.
**Fix:** Not documented.
**Lesson:** ALWAYS provide detailed failure context when calling 'reflect'.

### [2026-02-20] Check Error Logs Diligently
**Symptom:** Build failed without clear reason.
**Root Cause:** Insufficiently analyzed error logs.
**Fix:** Manually checked error logs to diagnose issue.
**Lesson:** ALWAYS carefully analyze error logs.

### [2026-02-20] Remove Obsolete Code/Docs
**Symptom:** Code/documentation was obsolete or outdated.
**Root Cause:** Failure to remove/update outdated artifacts.
**Fix:** Removed/updated obsolete code and documentation.
**Lesson:** ALWAYS remove obsolete code/documentation promptly.

### [2026-02-20] Inner Agents Stability Needed
**Symptom:** Inner agents system experienced unspecified issues.
**Root Cause:** Unknown internal agent interactions led to errors.
**Fix:** Corrected underlying inner agents system errors.
**Lesson:** ALWAYS rigorously test inner-agent interactions.

### [2026-02-20] Missing Import Prevents Build
**Symptom:** UI validation failed during build process.
**Root Cause:** Missing or misnamed import statement.
**Fix:** Corrected import statements in the frontend.
**Lesson:** ALWAYS verify imports after code changes.

### [2026-02-20] Fix Build Automatically
**Symptom:** TypeScript build failed.
**Root Cause:** Undetermined compilation error.
**Fix:** Triggered automated healing process.
**Lesson:** ALWAYS automate build error recovery.

### [2026-02-20] Initialize All Object Attributes
**Symptom:** `ui_validator_agent.py` crashed due to missing attribute.
**Root Cause:** `FixReport` object was instantiated without 'fixes'.
**Fix:** Added initialization of the 'fixes' attribute.
**Lesson:** ALWAYS initialize all object attributes explicitly.

### [2026-02-20] Missing Attribute Causes Crash
**Symptom:** Code crashed due to missing attribute.
**Root Cause:** `fixes` attribute was missing.
**Fix:** Added the missing `fixes` attribute.
**Lesson:** ALWAYS validate object attribute existence.
