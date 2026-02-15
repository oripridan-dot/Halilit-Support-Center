# What to do — get the app running (v9.2 JIT)

Do these in order, from the **project root** (the folder that contains `backend/` and `frontend/`).

---

## 1. Create and use the Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows (PowerShell): `.venv\Scripts\Activate.ps1`

---

## 2. Install backend dependencies

With the venv **activated**:

```bash
pip install -r backend/requirements.txt
```

---

## 3. Install frontend dependencies

Still from project root:

```bash
cd frontend && (pnpm install || npm install) && cd ..
```

---

## 4. (Optional) Environment file for API keys

Only needed if you want **JIT intelligence** (live AI-powered product analysis). The catalog itself works from skeleton data without API keys.

```bash
cp .env.example .env
```

Edit `.env` and set at least:

- `GOOGLE_API_KEY` — from [Google AI Studio](https://makersuite.google.com/app/apikey) (Gemini 2.0 Flash)

Leave other keys empty if you don't have them; the app will start and the catalog loads from skeleton inventory.

---

## 5. Start the app

From project root, with the venv **activated** (see step 1):

```bash
source .venv/bin/activate   # if you haven't already
./start.sh
```

- Backend runs on **http://localhost:8000**
- Frontend runs on **http://localhost:5173**
- The script will try to open the browser; if not, go to **http://localhost:5173**

Keep the terminal open. To stop: **Ctrl+C**.

---

## If you see "No products" or empty catalog

Product data can come from either:

**Option A — Skeleton sync** (fast, ~30 seconds): ID, Name, Price, URL, Thumbnail only.

```bash
source .venv/bin/activate
PYTHONPATH=. python3 backend/conductor_main.py skeleton-sync
```

This writes `frontend/public/data/inventory.json`.

**Option B — Full catalog** (Golden List + optional enrich): full commercial data, many brands.

```bash
source .venv/bin/activate
PYTHONPATH=. python3 backend/conductor_main.py commercial-ingest
# optional: PYTHONPATH=. python3 backend/conductor_main.py enrich
```

Or run both in one go: `PYTHONPATH=. python3 backend/conductor_main.py ingest-all`

After scraping, rebuild catalog and product graph:  
`PYTHONPATH=. python3 backend/conductor_main.py rebuild-catalog`

See [backend/ingestion/README.md](backend/ingestion/README.md) and [IMPLEMENTATION-COMPLETE.md](IMPLEMENTATION-COMPLETE.md) for the full pipeline.

---

## Loading live product intelligence

In v9.0, there is **no heavy ingestion step**. Instead:

1. **Skeleton sync** populates the browse-able catalog (name, price, image).
2. **JIT Agent** streams live AI intelligence when a user clicks on any product.
3. Intelligence is **cached for 7 days** — the first view takes a few seconds, then it's instant.

The JIT Agent requires:
- `GOOGLE_API_KEY` set in `.env` (for Gemini 2.0 Flash)
- `SERP_API_KEY` set in `.env` (for trusted review lookups — optional)

---

## Quick reference

| Step              | Command |
|-------------------|--------|
| Create venv       | `python3 -m venv .venv` |
| Activate venv     | `source .venv/bin/activate` |
| Install backend   | `pip install -r backend/requirements.txt` |
| Install frontend  | `cd frontend && (pnpm install \|\| npm install) && cd ..` |
| Optional .env     | `cp .env.example .env` then edit |
| Skeleton sync     | `PYTHONPATH=. python3 backend/conductor_main.py skeleton-sync` |
| Full pipeline     | `PYTHONPATH=. python3 backend/conductor_main.py ingest-all` |
| Rebuild catalog  | `PYTHONPATH=. python3 backend/conductor_main.py rebuild-catalog` |
| Start app         | `./start.sh` or `PYTHONPATH=. python backend/conductor_main.py dev` |

Planned features and implementation status: [IMPLEMENTATION-COMPLETE.md](IMPLEMENTATION-COMPLETE.md).
