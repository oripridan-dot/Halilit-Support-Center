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

### [2026-02-20] Initialize Data Attributes
**Symptom:** `ui_validator_agent.py` raised an AttributeError.
**Root Cause:** FixReport objects lacked a default 'fixes' attribute.
**Fix:** Initialized the 'fixes' attribute in FixReport.
**Lesson:** ALWAYS initialize data object attributes.

### [2026-02-20] Check Attribute Existence
**Symptom:** AttributeError occurred when accessing 'fixes'.
**Root Cause:** 'fixes' attribute missing in FixReport object.
**Fix:** Added a check for attribute existence.
**Lesson:** ALWAYS check object attributes exist.

### [2026-02-20] Validate API Response Schemas
**Symptom:** UI validation failed due to missing 'fixes' attribute.
**Root Cause:** The API response schema lacked the expected 'fixes' attribute.
**Fix:** Added the missing 'fixes' attribute to the FixReport.
**Lesson:** ALWAYS validate API response schemas.

### [2026-02-20] Missing Attribute Handler
**Symptom:** Code failed due to missing attribute.
**Root Cause:** `fixes` attribute was not present.
**Fix:** Added a handler for the missing attribute.
**Lesson:** ALWAYS handle potentially missing attributes.


### [2026-02-20] Mutation — Check Patch Anchor Existence
**Symptom:** Patch application failed.
**Root Cause:** Required anchor element was missing in the target file.
**Fix:** Added verification that the anchor exists before patching.
**Lesson:** ALWAYS verify that the specified anchor exists in the target file before attempting a `patch_component` operation.


### [2026-02-20] Mutation — patch_component Gen 3
**Symptom:** Patch application failed.
**Root Cause:** Required anchor element was missing in the target file.
**Fix:** Added verification that the anchor exists before patching.
**Lesson:** ALWAYS verify that the specified anchor exists in the target file before attempting a `patch_component` operation.


### [2026-02-20] Mutation — ui_validator Gen 2
**Symptom:** UI validation failed.
**Root Cause:** The agent failed to complete the UI validation task due to an overly broad instruction that requires updates across multiple specification documents.
**Fix:** Decomposed UI validation tasks into smaller, sequential tasks.
**Lesson:** ALWAYS decompose UI validation tasks that require updates to more than two specification documents into smaller, sequential tasks.


### [2026-02-20] Mutation — patch_component Gen 4
**Symptom:** Patch application failed.
**Root Cause:** Required anchor element was missing in the target file.
**Fix:** Added verification that the anchor exists before patching.
**Lesson:** ALWAYS verify that the specified anchor exists in the target file before attempting a `patch_component` operation.


### [2026-02-20] Mutation — ui_validator Gen 3
**Symptom:** UI validation failed.
**Root Cause:** The agent failed when delegating front-end tasks involving complex component updates and specification modifications related to image optimization.
**Fix:** Implement task decomposition and prioritization for complex UI validation tasks, focusing on incremental updates and utilizing specific image optimization metrics for validation.
**Lesson:** ALWAYS decompose complex UI validation tasks involving multiple components, specifications, and image optimization into smaller, prioritized steps, validating each step against specific, measurable metrics.

### [2026-02-21] Implement Code Generation Fully
**Symptom:** A stub file was committed.
**Root Cause:** Code generation created incomplete file.
**Fix:** Completed the implementation for that file.
**Lesson:** ALWAYS ensure generated files are complete.

### [2026-02-21] Refactor Naming Conventions
**Symptom:** Refactoring caused duplicate symbol errors.
**Root Cause:** Inconsistent naming and export conventions.
**Fix:** Corrected naming and export declarations.
**Lesson:** ALWAYS enforce consistent naming conventions.
