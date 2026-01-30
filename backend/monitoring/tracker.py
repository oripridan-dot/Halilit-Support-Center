import json
import hashlib
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from backend.monitoring.db import get_connection

logger = logging.getLogger("IngestionTracker")


class IngestionTracker:
    def __init__(self, brand_id: str):
        self.brand_id = brand_id
        self.run_id = None
        self.conn = get_connection()

    def start_run(self, pipeline_version: str = "v1.0"):
        """Starts a new ingestion run."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO ingestion_runs (brand_id, started_at, status, pipeline_version)
            VALUES (?, ?, ?, ?)
        ''', (self.brand_id, datetime.now(), "RUNNING", pipeline_version))
        self.conn.commit()
        self.run_id = cursor.lastrowid
        logger.info(f"📝 Tracking started for run #{self.run_id}")
        return self.run_id

    def finish_run(self, status: str, metrics: Dict[str, Any]):
        """Completes the run with status and metrics."""
        if not self.run_id:
            logger.warning("Attempted to finish run without starting one.")
            return

        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE ingestion_runs 
            SET completed_at = ?, status = ?, metrics = ?
            WHERE id = ?
        ''', (datetime.now(), status, json.dumps(metrics), self.run_id))
        self.conn.commit()
        logger.info(f"📝 Tracking finished for run #{self.run_id} [{status}]")

    def track_product(self, product: Dict[str, Any]):
        """
        Records a product's state and detects changes from previous runs.
        """
        if not self.run_id:
            return

        product_id = product.get("id")
        price = product.get("price", 0)
        stock_status = product.get("status", "UNKNOWN")
        manual_count = len(product.get("official_manuals", []))
        specs_count = len(product.get("specs", []))

        # Calculate Content Hash (stable JSON dump of meaningful fields)
        content_payload = {
            "name": product.get("name"),
            "description": product.get("description"),
            "features": product.get("features"),
            "specs": product.get("specs"),
            "images": product.get("images"),
            "manuals": product.get("official_manuals")
        }
        content_hash = hashlib.md5(json.dumps(
            content_payload, sort_keys=True).encode()).hexdigest()

        # Find previous snapshot
        prev_snapshot = self._get_last_snapshot(product_id)

        # Detect Changes
        if prev_snapshot:
            self._detect_changes(prev_snapshot, {
                "price": price,
                "stock_status": stock_status,
                "manual_count": manual_count,
                "specs_count": specs_count,
                "content_hash": content_hash
            }, product_id)

        # Insert current snapshot
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO product_snapshots 
            (run_id, brand_id, product_id, halilit_id, name, price, stock_status, manual_count, specs_count, content_hash, captured_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            self.run_id,
            self.brand_id,
            product_id,
            product.get("halilit_id"),
            product.get("name"),
            price,
            stock_status,
            manual_count,
            specs_count,
            content_hash,
            datetime.now()
        ))
        self.conn.commit()

    def _get_last_snapshot(self, product_id: str):
        """Fetch the most recent snapshot from a *previous* run."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM product_snapshots 
            WHERE product_id = ? AND run_id < ?
            ORDER BY id DESC LIMIT 1
        ''', (product_id, self.run_id))
        return cursor.fetchone()

    def _detect_changes(self, prev, curr, product_id):
        """Compare and log changes."""
        changes = []

        # Price Change
        if prev['price'] != curr['price']:
            changes.append(("price", prev['price'], curr['price']))

        # Stock Change
        if prev['stock_status'] != curr['stock_status']:
            changes.append(
                ("stock_status", prev['stock_status'], curr['stock_status']))

        # Doc Content Change
        if prev['manual_count'] != curr['manual_count']:
            changes.append(
                ("manual_count", prev['manual_count'], curr['manual_count']))

        # Content Deep Change
        if prev['content_hash'] != curr['content_hash']:
            # We rely on hash for deep content, but we don't store the deep diff string in DB yet to save space
            changes.append(("content", "hash_mismatch", "updated"))

        if changes:
            cursor = self.conn.cursor()
            for field, old, new in changes:
                cursor.execute('''
                    INSERT INTO product_changes (run_id, product_id, field_name, old_value, new_value)
                    VALUES (?, ?, ?, ?, ?)
                ''', (self.run_id, product_id, field, str(old), str(new)))

                logger.info(
                    f"🔄 Change detected for {product_id} [{field}]: {old} -> {new}")
            self.conn.commit()

    def close(self):
        self.conn.close()
