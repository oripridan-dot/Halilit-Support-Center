# OpenClaw Agent Skills — Halilit Field Agent

**Compliance:** Use is restricted and documented in [COMPLIANCE.md](./COMPLIANCE.md). Only allowlisted manufacturer domains and internal API access.

These skills are mounted into the OpenClaw container so the Field Agent knows how to:

1. **official_scout.md** — Verify product specs on manufacturer sites (Roland, Yamaha, etc.)
2. **shop_floor_assistant.md** — Answer employee questions via WhatsApp/Telegram using Halilit API
3. **halilit_api.md** — Tool definitions for querying the Halilit Support Center backend
4. **catalog_organizer.md** — Per-brand catalog consolidation: turn raw products into a unified structure (categories, search_index) for easy search and browse

When running with `docker-compose --profile openclaw up`, the `openclaw` service mounts this directory at `/root/.openclaw/skills`.

**Backend URL:** Skills use `http://backend:8000` for the Halilit API. When the API runs on the host (not in Docker), either run the API in Docker (uncomment `api_server` in docker-compose) or configure OpenClaw to use `http://host.docker.internal:8000` for backend calls.
