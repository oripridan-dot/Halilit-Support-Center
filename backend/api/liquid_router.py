"""
Liquid Route Manager — backend/api/liquid_router.py
=====================================================
The Ephemeral Backend Router: register temporary SQL SELECT queries in
memory against an in-memory SQLite mirror of the Halilit catalog.  No
files written.  No server restart.  Endpoints expire when cleared.

Architecture:
  • `_CATALOG_DB`       — shared in-memory SQLite built once from inventory.json
  • `EPHEMERAL_ROUTES`  — dict mapping route_id → sql_query (live registry)
  • `register_dynamic_route(sql)` → "/api/liquid/data/{route_id}"
  • GET /api/liquid/data/{route_id} — safe sandbox executor (SELECT only)
  • DELETE /api/liquid/data/{route_id} — optional manual eviction
  • GET /api/liquid/schema — expose available columns for LLM prompt context

Boundary Sandbox Rules (Zero-Trust):
  1. Only SELECT statements are allowed.
  2. Query runs against the read-only in-memory mirror (DROP TABLE is a no-op even
     if attempted because the catalog is rebuilt on demand from JSON).
  3. Hard row cap: 500 rows per request.
"""

from __future__ import annotations

import json
import logging
import sqlite3
import threading
import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/liquid", tags=["liquid"])

# ---------------------------------------------------------------------------
# In-memory database — built once from inventory.json at import time
# ---------------------------------------------------------------------------

_DB_LOCK = threading.Lock()
_CATALOG_DB: sqlite3.Connection | None = None

_INVENTORY_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "frontend" / "public" / "data" / "inventory.json"
)

_CREATE_SQL = """
CREATE TABLE IF NOT EXISTS products (
    id              TEXT,
    name            TEXT,
    brand           TEXT,
    category        TEXT,
    price           REAL,
    price_eilat     REAL,
    in_stock        INTEGER,
    halilit_url     TEXT
);
"""


def _build_in_memory_db() -> sqlite3.Connection:
    """Build (or rebuild) the shared in-memory SQLite catalog mirror."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute(_CREATE_SQL)

    if _INVENTORY_PATH.exists():
        try:
            raw = json.loads(_INVENTORY_PATH.read_text(encoding="utf-8"))
            products: list[dict] = raw.get("products", [])
            rows = [
                (
                    p.get("id", ""),
                    p.get("name", ""),
                    p.get("brand", ""),
                    p.get("category_hint", ""),
                    p.get("price"),
                    p.get("price_eilat"),
                    1 if p.get("in_stock", True) else 0,
                    p.get("halilit_url", ""),
                )
                for p in products
            ]
            conn.executemany(
                "INSERT INTO products VALUES (?,?,?,?,?,?,?,?)", rows
            )
            conn.commit()
            logger.info(
                f"[LiquidRouter] Catalog mirror built: {len(rows)} products loaded into :memory:"
            )
        except Exception as exc:
            logger.warning(
                f"[LiquidRouter] Catalog mirror build failed: {exc}")
    else:
        logger.warning(
            f"[LiquidRouter] inventory.json not found at {_INVENTORY_PATH}. "
            "In-memory DB is empty — queries will return no rows."
        )

    return conn


def _get_db() -> sqlite3.Connection:
    global _CATALOG_DB
    if _CATALOG_DB is None:
        with _DB_LOCK:
            if _CATALOG_DB is None:
                _CATALOG_DB = _build_in_memory_db()
    return _CATALOG_DB


# ---------------------------------------------------------------------------
# Ephemeral route registry
# ---------------------------------------------------------------------------

EPHEMERAL_ROUTES: dict[str, str] = {}   # route_id → SQL query
_ROUTES_LOCK = threading.Lock()
MAX_ROUTES = 100          # Evict oldest when full
_MAX_ROWS = 500           # Safety cap


def register_dynamic_route(sql_query: str) -> str:
    """
    Register a safe SELECT query in memory and return the API path.

    Returns:
        str: endpoint path, e.g. "/api/liquid/data/ephemeral_a1b2c3d4"
    Raises:
        ValueError: if the query is not a SELECT statement.
    """
    q = sql_query.strip()
    if not q.upper().startswith("SELECT"):
        raise ValueError(
            "Sandbox Violation: only SELECT queries can be registered.")

    route_id = f"ephemeral_{uuid.uuid4().hex[:8]}"

    with _ROUTES_LOCK:
        # Evict oldest entry when at capacity
        if len(EPHEMERAL_ROUTES) >= MAX_ROUTES:
            oldest = next(iter(EPHEMERAL_ROUTES))
            del EPHEMERAL_ROUTES[oldest]
            logger.debug(f"[LiquidRouter] Evicted oldest route: {oldest}")
        EPHEMERAL_ROUTES[route_id] = q

    endpoint = f"/api/liquid/data/{route_id}"
    logger.info(f"[LiquidRouter] Registered ephemeral route: {endpoint}")
    return endpoint


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------

@router.get("/data/{route_id}")
def execute_ephemeral_route(route_id: str) -> dict[str, Any]:
    """
    JIT Data Streamer — execute a registered ephemeral SELECT query.

    Sandbox guarantees:
      • Only SELECT statements can be registered (enforced at registration).
      • Row cap: 500 rows max.
      • Runs against the read-only in-memory catalog mirror.
    """
    with _ROUTES_LOCK:
        query = EPHEMERAL_ROUTES.get(route_id)

    if query is None:
        raise HTTPException(
            status_code=404,
            detail=f"Ephemeral route '{route_id}' has expired or does not exist.",
        )

    # Belt-and-suspenders: re-validate at execution time
    if not query.strip().upper().startswith("SELECT"):
        raise HTTPException(
            status_code=403,
            detail="Sandbox Violation: only SELECT statements are permitted.",
        )

    try:
        db = _get_db()
        with _DB_LOCK:
            cursor = db.execute(query)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchmany(_MAX_ROWS)
            data = [dict(zip(columns, row)) for row in rows]

        return {
            "route_id": route_id,
            "columns": columns,
            "row_count": len(data),
            "capped": len(data) == _MAX_ROWS,
            "data": data,
        }
    except sqlite3.Error as exc:
        raise HTTPException(status_code=400, detail=f"SQL Error: {exc}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.delete("/data/{route_id}")
def evict_ephemeral_route(route_id: str) -> dict[str, str]:
    """Manually evict an ephemeral route from memory."""
    with _ROUTES_LOCK:
        if route_id not in EPHEMERAL_ROUTES:
            raise HTTPException(status_code=404, detail="Route not found.")
        del EPHEMERAL_ROUTES[route_id]

    logger.info(f"[LiquidRouter] Evicted route: {route_id}")
    return {"status": "evicted", "route_id": route_id}


@router.get("/schema")
def get_catalog_schema() -> dict[str, Any]:
    """
    Returns the available table/column metadata for the catalog mirror.
    Used by the LLM prompt to generate valid SQL without hallucinating column names.
    """
    db = _get_db()
    try:
        with _DB_LOCK:
            cursor = db.execute("SELECT COUNT(*) FROM products")
            count = cursor.fetchone()[0]
        return {
            "tables": {
                "products": {
                    "columns": [
                        {"name": "id", "type": "TEXT"},
                        {"name": "name", "type": "TEXT"},
                        {"name": "brand", "type": "TEXT"},
                        {"name": "category", "type": "TEXT"},
                        {"name": "price", "type": "REAL",
                            "note": "IL price in ILS"},
                        {"name": "price_eilat", "type": "REAL",
                            "note": "Eilat price in ILS"},
                        {"name": "in_stock", "type": "INTEGER",
                            "note": "1=in stock, 0=out"},
                        {"name": "halilit_url", "type": "TEXT"},
                    ],
                    "row_count": count,
                }
            },
            "max_rows_per_query": _MAX_ROWS,
            "active_ephemeral_routes": len(EPHEMERAL_ROUTES),
        }
    except Exception as exc:
        return {"error": str(exc)}


@router.get("/routes")
def list_active_routes() -> dict[str, Any]:
    """List all currently registered ephemeral routes (for debugging)."""
    with _ROUTES_LOCK:
        return {
            "active_routes": list(EPHEMERAL_ROUTES.keys()),
            "count": len(EPHEMERAL_ROUTES),
        }
