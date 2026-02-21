"""
Telemetry Agent — The Sovereign Nerve Reflex Arc
=================================================
Part of the Sovereign Nerve system (v9.7.6).

Activated instantly when a production crash report is received via
POST /api/telemetry/crash-report from the self-hosted browser telemetry
(frontend/src/telemetry.ts).  It:
  1. Extracts the error details from the payload.
  2. Prints a high-urgency alert to the Swarm console.
  3. Drafts a HOTFIX_PROPOSAL markdown file in docs/ for the Governor.

No external dependencies required beyond the stdlib — this module must
remain importable even before optional packages are installed.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Resolve docs/ relative to the repo root regardless of cwd
_REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = _REPO_ROOT / "docs"


def process_production_error(sentry_payload: dict) -> str:
    """The Sovereign Reflex Arc — triggered instantly when a production crash arrives.

    Args:
        sentry_payload: The raw JSON body posted by the browser telemetry client
                        (frontend/src/telemetry.ts) or any compatible ingestor.

    Returns:
        Absolute path to the hotfix proposal file that was created.
    """
    # ── 1. Extract Signal ────────────────────────────────────────────────────
    # The browser telemetry client uses event.title; fallback to root keys for
    # any other compatible ingestors.
    event = sentry_payload.get("event", sentry_payload)  # fallback to root
    error_message = (
        event.get("title")
        or event.get("message")
        or sentry_payload.get("message")
        or "Unknown Production Error"
    )
    culprit = event.get("culprit") or sentry_payload.get(
        "culprit") or "Unknown location"
    level = event.get("level") or sentry_payload.get("level") or "error"
    environment = event.get("environment") or sentry_payload.get(
        "environment") or "production"
    project = sentry_payload.get(
        "project_name") or sentry_payload.get("project") or "Halilit"

    # ── 2. Alert ─────────────────────────────────────────────────────────────
    siren = "🚨" * 10
    print(f"\n{siren}")
    print(f"📡  SOVEREIGN NERVE TRIGGERED: Production Crash Detected!")
    print(f"    Project     : {project}")
    print(f"    Environment : {environment}")
    print(f"    Level       : {level.upper()}")
    print(f"    Error       : {error_message}")
    print(f"    Culprit     : {culprit}")
    print(f"{siren}\n")

    logger.critical(
        "[SOVEREIGN NERVE] %s | culprit=%s | env=%s",
        error_message,
        culprit,
        environment,
    )

    # ── 3. Draft Hotfix Proposal ─────────────────────────────────────────────
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    proposal_path = DOCS_DIR / f"HOTFIX_PROPOSAL_{timestamp}.md"

    # Pretty-print payload for context (truncate if massive)
    try:
        raw_dump = json.dumps(sentry_payload, indent=2, ensure_ascii=False)
        if len(raw_dump) > 8000:
            raw_dump = raw_dump[:8000] + "\n... [truncated]"
    except Exception:
        raw_dump = str(sentry_payload)[:8000]

    proposal_content = f"""# 🚑 URGENT HOTFIX PROPOSAL

**Timestamp:** {datetime.now().isoformat()}
**Project:** {project}
**Environment:** {environment}
**Level:** {level.upper()}

---

## Error

```
{error_message}
```

**Culprit:** `{culprit}`

---

## Raw Sentry Payload

```json
{raw_dump}
```

---

## Governor Action Required

The Telemetry Nerve detected this crash in production.

**Shall I:**
- [ ] Spin up an `evo/hotfix` branch
- [ ] Analyse the stack trace with the Unified Diff tool
- [ ] Prepare a patch and run TDD tests
- [ ] Send a deployment approval request

Reply `YES` to dispatch the Swarm or `NO` to archive this proposal.
"""

    proposal_path.write_text(proposal_content, encoding="utf-8")
    print(f"📝  Hotfix proposal drafted → {proposal_path}")
    print(f"    Governor, review and approve to dispatch the Swarm.\n")

    return str(proposal_path)
