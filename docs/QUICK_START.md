# Quick Start

Get the Halilit Operator Console running in one place. No scattered "clear cache" or "verify" steps—just run.

---

## First Time: Install

From the **project root** (folder that contains `backend/` and `frontend/`):

**1. Python virtual environment**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell: `.venv\Scripts\Activate.ps1`

**2. Backend dependencies**

```bash
pip install -r backend/requirements.txt
```

**3. Frontend dependencies**

```bash
cd frontend && (pnpm install || npm install) && cd ..
```

**4. (Optional) Environment**

Copy `.env.example` to `.env` and set `GOOGLE_API_KEY` if you want JIT (on-demand product intelligence). The catalog works without it.

---

## Every Time: Run the App

**One command (recommended):**

```bash
./factory_reset.sh
```

- Backend: http://localhost:8000 (API docs: http://localhost:8000/docs)
- Frontend: http://localhost:5173

If you see "CRITICAL: No catalog artifact found", run once:

```bash
./factory_reset.sh --rebuild
```

That rebuilds the catalog then starts both servers.

**Alternative:** Use your existing script:

```bash
./start_console.sh
```

---

## Open in Browser

- **URL:** http://localhost:5173
- **In Cursor:** View → Simple Browser → enter `http://localhost:5173`

Keep the terminal open while using the app.

---

## Next Steps

- **How we work:** [WORKFLOW.md](WORKFLOW.md)
- **Run and data commands:** [FACTORY_PIPELINE.md](FACTORY_PIPELINE.md)
- **What the console must do:** [OPERATOR_CONSOLE_SPEC.md](../OPERATOR_CONSOLE_SPEC.md)
