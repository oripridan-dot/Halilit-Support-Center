# `.tooloo.config` Reference

The `.tooloo.config` file lives at the repository root. It is the single
authoritative configuration contract between the product repository and TooLoo
Core. Every agent that starts up reads this file before executing any task.

> **Do not duplicate these values** in environment files, Docker Compose, or any
> other config surface. If a value needs to reach a runtime, write a small
> adapter that sources `.tooloo.config`.

---

## Identity Keys

| Key | Example | Purpose |
|-----|---------|---------|
| `PROJECT_NAME` | `"Halilit Support Center"` | Human-readable product name shown in TooLoo dashboards and CHANGELOG headers. |
| `PROJECT_SLUG` | `"halilit-support-center"` | URL-safe identifier used in branch names, PR titles, and CI labels. |
| `PROJECT_DESCRIPTION` | `"AI-powered support center"` | One-line product description surfaced by the Product Manager agent. |

---

## Path Keys

These tell TooLoo where important directories live, relative to the repo root.

| Key | Default | Purpose |
|-----|---------|---------|
| `TOOLOO_PATH` | `"../tooloo-core"` | Path to the TooLoo Core engine. Used when running TooLoo locally in dev mode. |
| `FRONTEND_DIR` | `"frontend"` | Root of the React / Vite frontend. Used by the frontend manager and Vitest runner. |
| `BACKEND_DIR` | `"backend"` | Root of the FastAPI backend. Used by the builder agent and test runner. |
| `SPECS_DIR` | `"specs"` | Where spec files live. The spec writer writes here; the builder reads from here. |
| `DOCS_DIR` | `"docs"` | Where documentation lives. The PM reads `ROADMAP.md` from this directory. |
| `TESTS_DIR` | `"backend/tests"` | Where pytest files live. Used by the watchdog and CI agent. |

---

## Deployment Keys

| Key | Values | Purpose |
|-----|--------|---------|
| `DOCKER_ENABLED` | `"true"` / `"false"` | Whether Docker Compose is the deployment strategy. |
| `DOCKER_COMPOSE_FILE` | `"docker-compose.yml"` | Path to the Compose file, relative to repo root. |

---

## Version Management Keys

| Key | Example | Purpose |
|-----|---------|---------|
| `CURRENT_VERSION` | `$(cat .version)` | Shell expression that reads the live version from `.version`. **Never hardcode.** |
| `CHANGELOG_PATH` | `"CHANGELOG.md"` | Path to the CHANGELOG. TooLoo appends entries here on every PR merge. |

> **Law 6 — Version Sovereignty:** Only TooLoo may bump version numbers. Never
> edit `.version`, `package.json#version`, or `pyproject.toml#version` by hand.

---

## CI/CD Keys

| Key | Default | Purpose |
|-----|---------|---------|
| `GITHUB_WORKFLOWS_DIR` | `".github/workflows"` | Where GitHub Actions YAML files live. The CI agent reads and patches these. |

---

## Development Environment Keys

| Key | Values | Purpose |
|-----|--------|---------|
| `DEV_CONTAINER_ENABLED` | `"true"` / `"false"` | Whether a Dev Container is configured for this repo. |
| `DEV_CONTAINER_CONFIG` | `".devcontainer/devcontainer.json"` | Path to the Dev Container config. |

---

## Agent Toggle Keys

These keys control which TooLoo agents are activated for this product. Setting
a value to `"false"` disables that agent entirely — it will not be instantiated
even if TooLoo Core attempts to spawn it.

| Key | Default | Purpose |
|-----|---------|---------|
| `CHIEF_AGENT_ENABLED` | `"true"` | The orchestration chief that plans and delegates tasks. |
| `TECH_LEAD_AGENT_ENABLED` | `"true"` | Pre-flight architectural veto gate (Bicameral Governance). |
| `REPO_AGENT_ENABLED` | `"true"` | Manages git branches and opens PRs via the GitHub API. |
| `BUILDER_AGENT_ENABLED` | `"true"` | Materialises spec files into code. |
| `WATCHDOG_AGENT_ENABLED` | `"true"` | Scans for errors and auto-repairs (Wolverine Protocol). |

---

## Verification Command Keys

TooLoo runs these shell commands to verify that a change does not break the
product. All three must exit `0` for a PR to be auto-merged.

| Key | Default Command | Purpose |
|-----|-----------------|---------|
| `FRONTEND_BUILD_COMMAND` | `cd frontend && npm run build` | Ensures the frontend compiles cleanly. |
| `BACKEND_TESTS_COMMAND` | `pytest backend/tests` | Runs the full backend test suite. |
| `LINT_COMMAND` | `cd frontend && npm run lint` | Ensures no lint violations in the frontend. |

---

## Feature Flags

| Key | Values | Purpose |
|-----|--------|---------|
| `AUTO_CHANGELOG` | `"true"` / `"false"` | TooLoo automatically appends a CHANGELOG entry on each PR merge. |
| `AUTO_VERSION_BUMP` | `"true"` / `"false"` | TooLoo bumps the patch version on each PR merge (governed by Law 6). |
| `SEMANTIC_COMMITS` | `"true"` / `"false"` | Enforce Conventional Commits format on all TooLoo-generated commits. |
