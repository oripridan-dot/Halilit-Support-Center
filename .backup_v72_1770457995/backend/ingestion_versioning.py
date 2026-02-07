#!/usr/bin/env python3
"""
Ingestion Versioning System - Track and version all data ingestions

Every ingestion run creates a version record with:
- Batch ID (timestamp + random hash)
- Brand name
- Product count (approved/rejected)
- Timestamp
- Data sources (Trinity Swarm agents)
- Quality metrics

This allows the UI to track which version of data is being displayed
and revert if needed.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib
import uuid

logger = logging.getLogger("IngestionVersioning")

VERSIONS_DIR = Path(
    "/workspaces/Halilit-Support-Center/backend/data/ingestion/versions")


class IngestionVersion:
    """Represents a single versioned ingestion"""

    def __init__(
        self,
        brand: str,
        batch_id: str,
        approved_count: int,
        rejected_count: int,
        total_processed: int,
        execution_time_seconds: float,
        data_completeness: float = 0.0,
        quality_score: float = 0.0,
        recommendations: Optional[List[str]] = None,
    ):
        self.brand = brand
        self.batch_id = batch_id
        self.version_id = f"{brand}_{batch_id}"
        self.timestamp = datetime.utcnow()
        self.approved_count = approved_count
        self.rejected_count = rejected_count
        self.total_processed = total_processed
        self.execution_time_seconds = execution_time_seconds
        self.data_completeness = data_completeness
        self.quality_score = quality_score
        self.recommendations = recommendations or []
        self.is_active = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version_id": self.version_id,
            "brand": self.brand,
            "batch_id": self.batch_id,
            "timestamp": self.timestamp.isoformat(),
            "approved_count": self.approved_count,
            "rejected_count": self.rejected_count,
            "total_processed": self.total_processed,
            "execution_time_seconds": self.execution_time_seconds,
            "data_completeness": self.data_completeness,
            "quality_score": self.quality_score,
            "is_active": self.is_active,
            "recommendations": self.recommendations,
        }


class IngestionVersionManager:
    """Manages versioned ingestion tracking"""

    def __init__(self):
        self.versions_dir = VERSIONS_DIR
        self.versions_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.versions_dir / "index.json"
        logger.info(
            f"✅ IngestionVersionManager initialized at {self.versions_dir}")

    def save_version(self, version: IngestionVersion) -> str:
        """Save a new ingestion version and return version ID"""
        version.is_active = True

        # Save version file
        version_file = (
            self.versions_dir / f"v{version.brand}_{version.batch_id}.json"
        )
        with open(version_file, "w") as f:
            json.dump(version.to_dict(), f, indent=2)

        logger.info(f"💾 Saved version: {version.version_id}")

        # Update index
        self._update_index(version)

        return version.version_id

    def get_active_version(self, brand: str) -> Optional[Dict[str, Any]]:
        """Get the currently active version for a brand"""
        index = self._load_index()
        for entry in index.get("versions", []):
            if entry["brand"] == brand and entry.get("is_active"):
                return entry
        return None

    def get_version_history(self, brand: str) -> List[Dict[str, Any]]:
        """Get all versions for a brand, newest first"""
        index = self._load_index()
        versions = [
            v for v in index.get("versions", []) if v["brand"] == brand
        ]
        return sorted(versions, key=lambda x: x["timestamp"], reverse=True)

    def get_all_active_versions(self) -> Dict[str, Dict[str, Any]]:
        """Get all currently active versions by brand"""
        index = self._load_index()
        active = {}
        for entry in index.get("versions", []):
            if entry.get("is_active"):
                active[entry["brand"]] = entry
        return active

    def _update_index(self, version: IngestionVersion):
        """Update the master index file"""
        index = self._load_index()

        # Remove old version if exists
        index["versions"] = [
            v
            for v in index.get("versions", [])
            if not (v["brand"] == version.brand and v["version_id"] == version.version_id)
        ]

        # Add new version
        index["versions"].append(version.to_dict())

        # Update metadata
        index["last_updated"] = datetime.utcnow().isoformat()
        index["total_brands"] = len(set(v["brand"] for v in index["versions"]))
        index["total_products"] = sum(
            v["approved_count"]
            for v in index["versions"]
            if v.get("is_active")
        )

        with open(self.index_file, "w") as f:
            json.dump(index, f, indent=2)

        logger.info(
            f"📋 Updated index: {len(index['versions'])} versions tracked")

    def _load_index(self) -> Dict[str, Any]:
        """Load the master index file"""
        if self.index_file.exists():
            with open(self.index_file) as f:
                return json.load(f)
        return {
            "versions": [],
            "last_updated": datetime.utcnow().isoformat(),
            "total_brands": 0,
            "total_products": 0,
        }

    def export_for_frontend(self) -> Dict[str, Any]:
        """Export version info for frontend to display"""
        index = self._load_index()
        active_versions = self.get_all_active_versions()

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "total_brands": index["total_brands"],
            "total_products": index["total_products"],
            "active_versions": active_versions,
            "recent_versions": sorted(
                index.get("versions", []),
                key=lambda x: x["timestamp"],
                reverse=True,
            )[:10],
        }


# Singleton
_manager = None


def get_version_manager() -> IngestionVersionManager:
    """Get singleton IngestionVersionManager instance"""
    global _manager
    if _manager is None:
        _manager = IngestionVersionManager()
    return _manager
