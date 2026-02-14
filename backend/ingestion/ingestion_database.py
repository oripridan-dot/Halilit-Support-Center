"""
Ingestion Database - Persistent storage for ingestion pipeline

Handles storage and retrieval of:
- IngestionProductDraft objects (approved & rejected)
- IngestionReport summaries
- Quality metrics and analytics
- Processing history and performance stats

Uses filesystem-based JSON storage organized by brand and date.
Can be extended with SQL database backend.
"""

import json
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import asdict

from backend.ingestion.data_models import (
    IngestionProductDraft, IngestionReport, IngestionStatus
)

logger = logging.getLogger("IngestionDatabase")


class IngestionDatabase:
    """Manages persistent storage of ingestion data"""

    def __init__(self, base_path: str | None = None):
        if base_path is None:
            from backend.project_config import INGESTION_DATA_DIR
            base_path = str(INGESTION_DATA_DIR)
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"IngestionDatabase initialized at {self.base_path}")

    def save_report(self, report: IngestionReport) -> str:
        """
        Save IngestionReport to database

        Returns:
            Path to saved report file
        """
        report_dir = self.base_path / "reports" / report.brand
        report_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"report_{timestamp}.json"

        report_data = {
            "batch_id": report.batch_id,
            "brand": report.brand,
            "timestamp": report.timestamp.isoformat() if hasattr(report.timestamp, 'isoformat') else str(report.timestamp),
            "execution_time_seconds": report.execution_time_seconds,
            "total_processed": report.total_products_processed,
            "approved_count": report.approved_count,
            "rejected_count": report.rejected_count,
            "recommendations": report.recommendations,
            "approved_products_count": len(report.approved_products),
            "rejected_products_count": len(report.rejected_products),
        }

        with open(report_file, "w") as f:
            json.dump(report_data, f, indent=2, default=str)

        logger.info(f"✅ Saved report to {report_file}")
        return str(report_file)

    def save_products(
        self,
        brand: str,
        approved_products: List[IngestionProductDraft],
        rejected_products: Optional[List[IngestionProductDraft]] = None,
    ) -> Dict[str, str]:
        """
        Save approved and rejected products

        Returns:
            Dict with paths to saved files
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        brand_dir = self.base_path / "products" / brand
        brand_dir.mkdir(parents=True, exist_ok=True)

        results = {}

        # Save approved products
        if approved_products:
            approved_file = brand_dir / f"approved_{timestamp}.json"
            approved_data = {
                "brand": brand,
                "timestamp": timestamp,
                "count": len(approved_products),
                "products": [self._product_to_dict(p) for p in approved_products],
            }

            with open(approved_file, "w") as f:
                json.dump(approved_data, f, indent=2, default=str)

            results["approved"] = str(approved_file)
            logger.info(
                f"✅ Saved {len(approved_products)} approved products to {approved_file}"
            )

        # Save rejected products
        if rejected_products:
            rejected_file = brand_dir / f"rejected_{timestamp}.json"
            rejected_data = {
                "brand": brand,
                "timestamp": timestamp,
                "count": len(rejected_products),
                "products": [self._product_to_dict(p) for p in rejected_products],
            }

            with open(rejected_file, "w") as f:
                json.dump(rejected_data, f, indent=2, default=str)

            results["rejected"] = str(rejected_file)
            logger.info(
                f"✅ Saved {len(rejected_products)} rejected products to {rejected_file}"
            )

        return results

    def save_quality_snapshot(
        self, brand: str, quality_metrics: Dict[str, Any]
    ) -> str:
        """
        Save quality metrics snapshot

        Returns:
            Path to saved metrics file
        """
        snapshot_dir = self.base_path / "quality" / brand
        snapshot_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        snapshot_file = snapshot_dir / f"quality_{timestamp}.json"

        snapshot_data = {
            "brand": brand,
            "timestamp": timestamp,
            "metrics": quality_metrics,
        }

        with open(snapshot_file, "w") as f:
            json.dump(snapshot_data, f, indent=2)

        logger.info(f"✅ Saved quality snapshot to {snapshot_file}")
        return str(snapshot_file)

    def load_latest_products(
        self, brand: str, status: str = "approved", limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Load latest products for a brand

        Args:
            brand: Brand name
            status: "approved" or "rejected"
            limit: Max number of products to return

        Returns:
            List of product dicts
        """
        products_dir = self.base_path / "products" / brand
        if not products_dir.exists():
            logger.warning(f"No products directory for {brand}")
            return []

        # Find latest file matching status
        files = sorted(
            products_dir.glob(f"{status}_*.json"), key=os.path.getmtime, reverse=True
        )

        if not files:
            logger.warning(f"No {status} products found for {brand}")
            return []

        latest_file = files[0]
        with open(latest_file, "r") as f:
            data = json.load(f)

        products = data.get("products", [])
        if limit:
            products = products[:limit]

        logger.info(
            f"✅ Loaded {len(products)} {status} products from {latest_file}")
        return products

    def get_all_approved_products(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all approved products from all brands.

        Returns:
            Dict of {brand: [approved_products]}
        """
        products_dir = self.base_path / "products"
        if not products_dir.exists():
            logger.warning("No products directory found")
            return {}

        all_products = {}

        # Iterate through each brand directory
        for brand_dir in products_dir.iterdir():
            if not brand_dir.is_dir():
                continue

            brand_name = brand_dir.name
            approved_products = self.load_latest_products(
                brand_name, status="approved")

            if approved_products:
                all_products[brand_name] = approved_products

        logger.info(
            f"✅ Loaded approved products from {len(all_products)} brands")
        return all_products

    def load_latest_report(self, brand: str) -> Optional[Dict[str, Any]]:
        """
        Load latest report for a brand

        Returns:
            Report dict or None if not found
        """
        reports_dir = self.base_path / "reports" / brand
        if not reports_dir.exists():
            logger.warning(f"No reports directory for {brand}")
            return None

        # Find latest report file
        files = sorted(
            reports_dir.glob("report_*.json"), key=os.path.getmtime, reverse=True
        )

        if not files:
            logger.warning(f"No reports found for {brand}")
            return None

        latest_file = files[0]
        with open(latest_file, "r") as f:
            report = json.load(f)

        logger.info(f"✅ Loaded report from {latest_file}")
        return report

    def get_brand_history(self, brand: str) -> Dict[str, Any]:
        """
        Get processing history for a brand

        Returns:
            Dict with history stats
        """
        reports_dir = self.base_path / "reports" / brand
        products_dir = self.base_path / "products" / brand
        quality_dir = self.base_path / "quality" / brand

        history = {
            "brand": brand,
            "reports": [],
            "approved_products_count": 0,
            "rejected_products_count": 0,
            "total_runs": 0,
        }

        # Count reports
        if reports_dir.exists():
            reports = list(reports_dir.glob("report_*.json"))
            history["total_runs"] = len(reports)
            history["reports"] = sorted([f.name for f in reports])

        # Count products
        if products_dir.exists():
            for approved_file in products_dir.glob("approved_*.json"):
                with open(approved_file, "r") as f:
                    data = json.load(f)
                    history["approved_products_count"] += data.get("count", 0)

            for rejected_file in products_dir.glob("rejected_*.json"):
                with open(rejected_file, "r") as f:
                    data = json.load(f)
                    history["rejected_products_count"] += data.get("count", 0)

        logger.info(
            f"Brand '{brand}' history: {history['total_runs']} runs, "
            f"{history['approved_products_count']} approved, "
            f"{history['rejected_products_count']} rejected"
        )

        return history

    def _product_to_dict(self, product: IngestionProductDraft) -> Dict[str, Any]:
        """Convert IngestionProductDraft to dictionary for JSON serialization"""
        # "flexible" fix: Use Pydantic's built-in serialization to capture ALL fields (even extra ones)
        return product.model_dump(mode='json')

    def export_analytics(self, brand: Optional[str] = None) -> Dict[str, Any]:
        """
        Export analytics for one or all brands

        Args:
            brand: Specific brand or None for all

        Returns:
            Analytics dict
        """
        analytics = {
            "timestamp": datetime.utcnow().isoformat(),
            "brands": {},
        }

        # Determine brands to analyze
        brands_to_analyze = []
        if brand:
            brands_to_analyze = [brand]
        else:
            products_dir = self.base_path / "products"
            if products_dir.exists():
                brands_to_analyze = [
                    d.name for d in products_dir.iterdir() if d.is_dir()]

        # Analyze each brand
        for b in brands_to_analyze:
            history = self.get_brand_history(b)
            analytics["brands"][b] = history

        logger.info(
            f"✅ Generated analytics for {len(analytics['brands'])} brands")
        return analytics


# Singleton pattern
_db = None


def get_ingestion_database(
    base_path: str | None = None,
) -> IngestionDatabase:
    """Get singleton IngestionDatabase instance"""
    global _db
    if _db is None:
        _db = IngestionDatabase(base_path)
    return _db
