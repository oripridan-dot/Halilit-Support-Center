# How to open the app in your browser

**First time:** install (below). **Every time after:** run one command and the app opens.

---

## Easiest: one command (recommended)

1. **In Cursor:** press **Ctrl+`** (or **View → Terminal**) to open the terminal at the bottom.
2. Paste this and press **Enter**:
   ```bash
   ./start.sh
   ```
3. Wait a few seconds. Your **browser will open automatically** at the app. Keep the terminal open (you can minimize it).
4. **To see the app inside Cursor** (no switching to Chrome/Safari): once it's running, go to **View → Simple Browser**, type `http://localhost:5173`, and press Enter. The app opens in a tab inside Cursor so you don't leave the editor.

**Alternative (Mac):** In Finder, go to the project folder and **double-click `start.command`**. Terminal will open, start the app, and open it in your browser.

---

## First time only: install

Run these once before using `./start.sh` (you're already in the project folder if you opened the terminal from Cursor):

**Step 1 — Use the project's virtual environment** (avoids the "externally-managed-environment" error on Mac):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Step 2 — Install backend (Python) into that environment:**

```bash
pip install -r backend/requirements.txt
```

**Step 3 — Install frontend:**

```bash
cd frontend && (pnpm install || npm install) && cd ..
```

After that, run `./start.sh` whenever you want to open the app.

---

## Populating the catalog

**Fast option (skeleton sync, ~30 seconds):**

```bash
source .venv/bin/activate
PYTHONPATH=. python3 backend/conductor_main.py skeleton-sync
```

**Full catalog (Golden List):** `PYTHONPATH=. python3 backend/conductor_main.py ingest-all` (commercial → enrich → sync → graph). Then optionally `rebuild-catalog` to refresh catalog and product graph. See [IMPLEMENTATION-COMPLETE.md](IMPLEMENTATION-COMPLETE.md).

Detailed intelligence is loaded on-demand when users view individual products (JIT). **v9.3**

---

## If something doesn't work

- **"externally-managed-environment"** — You must use the project's virtual environment. Run `source .venv/bin/activate` first, then `pip install -r backend/requirements.txt`. Do not use `pip3 install` without activating `.venv` first.
- **"python3: command not found"** — Install Python from https://www.python.org (or use `python` instead of `python3`).
- **"pnpm: command not found"** — The start script will use `npm` instead; run `cd frontend && npm install && cd ..` for the frontend.
- **Port already in use** — Something is already running on 8000 or 5173. Close that app or restart your computer and try again.
- **Blank or error page** — Keep the terminal open where you ran `./start.sh`; closing it stops the app.
- **"No products"** — Run skeleton-sync: `PYTHONPATH=. python3 backend/conductor_main.py skeleton-sync`
