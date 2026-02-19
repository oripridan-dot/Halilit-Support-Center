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
