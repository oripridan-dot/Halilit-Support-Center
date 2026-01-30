import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

DB_PATH = Path("backend/data/ingestion_history.db")


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Run History Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS ingestion_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand_id TEXT NOT NULL,
            started_at TIMESTAMP NOT NULL,
            completed_at TIMESTAMP,
            status TEXT,
            metrics JSON,
            pipeline_version TEXT
        )
    ''')

    # Product Snapshots Table (TimeSeries data for products)
    c.execute('''
        CREATE TABLE IF NOT EXISTS product_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER,
            brand_id TEXT,
            product_id TEXT NOT NULL,
            halilit_id TEXT,
            name TEXT,
            price REAL,
            stock_status TEXT,
            manual_count INTEGER,
            specs_count INTEGER,
            content_hash TEXT,
            captured_at TIMESTAMP,
            FOREIGN KEY(run_id) REFERENCES ingestion_runs(id)
        )
    ''')

    # Product Changes (Diff log)
    c.execute('''
        CREATE TABLE IF NOT EXISTS product_changes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER,
            product_id TEXT,
            field_name TEXT,
            old_value TEXT,
            new_value TEXT,
            FOREIGN KEY(run_id) REFERENCES ingestion_runs(id)
        )
    ''')

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
