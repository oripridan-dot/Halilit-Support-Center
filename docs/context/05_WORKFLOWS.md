# 🛠️ 05_WORKFLOWS.md

**Version:** 4.1.0  
**Updated:** January 28, 2026

## 🔄 Daily Dev Cycle

### 1. Start Environment

```bash
cd frontend
pnpm dev
```

### 2. Update Data (If Scrapers Changed)

```bash
cd backend
python3 forge_backbone.py
# Verify check:
# python3 system_architect.py
```

### 3. Deployment Build

```bash
cd frontend
pnpm build
# Upload 'dist/' folder to host
```

## 🚨 Troubleshooting

- **Missing Images?** Run `forge_backbone.py` to trigger Visual Factory.
- **Type Errors?** Run `npx tsc --noEmit` in frontend.
- **Stale Data?** Clear browser cache or run `window.__hscdev.clearCache()`.

## 🤖 AI-Assisted Iteration Protocol

To maintain high velocity and code quality ("tightness") when working with Gemini:

### 1. The Context File (`GEMINI_CONTEXT.md`)

Use this file at the root to drive the development session.

- **Current Focus**: Briefly state what we are doing.
- **Constraints**: Reminders for the AI (e.g., "Don't break the build").
- **Memory**: Dump error logs or code snippets here for the AI to analyze.

### 2. The Feedback Loop

1. **User**: Defines task in `GEMINI_CONTEXT.md` or via chat.
2. **Gemini**: **MUST** run `./verify_workspace.sh` to ensure no regressions.
3. **Gemini**: Makes changes & Updates `GEMINI_CONTEXT.md` with progress.
4. **User**: Reviews and approves.

### 3. Verification Script

Run `./verify_workspace.sh` from the root. It aggregates:

- **Backend**: `ruff` (linting) and `pytest`.
- **Frontend**: Type checking (`tsc`) and Linting (`eslint`). (Skipping full build for speed).

Use this script consistently.
