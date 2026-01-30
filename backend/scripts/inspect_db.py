import sqlite3
from pathlib import Path
import json

DB_PATH = Path("backend/data/ingestion_history.db")


def inspect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    print("--- Runs ---")
    c.execute("SELECT * FROM ingestion_runs")
    for r in c.fetchall():
        print(dict(r))

    print("\n--- Snapshots (First 3) ---")
    c.execute("SELECT * FROM product_snapshots LIMIT 3")
    for r in c.fetchall():
        print(dict(r))

    print("\n--- Changes ---")
    c.execute("SELECT * FROM product_changes")
    changes = c.fetchall()
    if not changes:
        print("No changes yet (expected for first run).")
    else:
        for r in changes:
            print(dict(r))

    conn.close()


if __name__ == "__main__":
    inspect()
