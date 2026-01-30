import sqlite3
import argparse
from pathlib import Path
from datetime import datetime

DB_PATH = Path("backend/data/ingestion_history.db")


def report_changes(brand_id: str = None):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    query = """
        SELECT c.*, r.started_at, s.name as product_name
        FROM product_changes c
        JOIN ingestion_runs r ON c.run_id = r.id
        LEFT JOIN product_snapshots s ON c.product_id = s.product_id AND s.run_id = c.run_id
    """
    params = []

    if brand_id:
        query += " WHERE r.brand_id = ?"
        params.append(brand_id)

    query += " ORDER BY r.started_at DESC, c.product_id"

    c.execute(query, params)
    rows = c.fetchall()

    print(
        f"\n📊 Change Report [{'ALL BRANDS' if not brand_id else brand_id.upper()}]")
    print("="*80)
    print(f"{'Date':<20} | {'Product Name':<30} | {'Field':<15} | {'Old':<10} -> {'New'}")
    print("-" * 80)

    for r in rows:
        date_str = r['started_at'].split('.')[0]
        prod_name = (r['product_name'] or r['product_id'])[:28]
        old_val = str(r['old_value'])[:10]
        new_val = str(r['new_value'])[:20]

        print(
            f"{date_str:<20} | {prod_name:<30} | {r['field_name']:<15} | {old_val:<10} -> {new_val}")

    print("="*80)
    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("brand_id", nargs="?", help="Filter by brand")
    args = parser.parse_args()

    report_changes(args.brand_id)
