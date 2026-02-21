# Spec: Pyroscope Integration

**Source:** 2026-03-01_proposal_pyroscope_for_performance_profiling.md
**Created:** 2026-02-21
**Status:** BUILT ✅

---

## What was built

- `backend/pyroscope_integration.py` — rewritten with `init_pyroscope()`,
  `profile()` context manager, `instrument()` decorator, `startup_check()`.
  All safe no-ops when `PYROSCOPE_SERVER_ADDRESS` env-var absent.
- `backend/server.py` lifespan → calls `init_pyroscope()` at startup.
- `backend/requirements.txt` → `pyroscope-io` documented as optional install.

## Acceptance Criteria

- [x] Server starts without pyroscope-io installed (ImportError handled).
- [x] `init_pyroscope()` called at lifespan startup.
- [x] `profile()` / `instrument()` available as stdlib-only decorator.
- [x] Three Source Rules: no synthetic data.
