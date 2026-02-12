"""
Diff-Based Publisher — Phase 7 Improvement

Replaces full catalog rewrites with intelligent diff-based publishing:
- Content-hash per product for change detection
- Only writes when something actually changed
- Versioned snapshots for rollback capability
- Atomic writes (write to temp, then rename)
- Publish manifest for frontend cache invalidation

Integrates with the existing IngestionDatabase for persistence, adding
a smarter publish layer on top for the public-facing catalog files.

Usage:
    publisher = DiffPublisher()
    result = publisher.publish(products)
    print(result.diff.summary)  # "+3 added, ~5 updated, -1 removed, =42 unchanged"
"""

import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Optional, List

logger = logging.getLogger("DiffPublisher")


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class PublishDiff:
    """Represents changes between two catalog versions."""
    added: List[str] = field(default_factory=list)
    updated: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    unchanged: List[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.updated or self.removed)

    @property
    def total_changed(self) -> int:
        return len(self.added) + len(self.updated) + len(self.removed)

    @property
    def summary(self) -> str:
        return (
            f"+{len(self.added)} added, "
            f"~{len(self.updated)} updated, "
            f"-{len(self.removed)} removed, "
            f"={len(self.unchanged)} unchanged"
        )

    def to_dict(self) -> dict:
        return {
            "added": len(self.added),
            "updated": len(self.updated),
            "removed": len(self.removed),
            "unchanged": len(self.unchanged),
            "has_changes": self.has_changes,
            "summary": self.summary,
        }


@dataclass
class PublishResult:
    """Result of a publish operation."""
    success: bool
    version: str
    diff: PublishDiff
    catalog_path: str
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "version": self.version,
            "catalog_path": self.catalog_path,
            "timestamp": self.timestamp,
            "diff": self.diff.to_dict(),
            "error": self.error,
        }


# ---------------------------------------------------------------------------
# Diff Publisher
# ---------------------------------------------------------------------------

class DiffPublisher:
    """
    Publishes catalogs with intelligent diff detection.

    Instead of rewriting the entire catalog JSON on every pipeline run,
    this publisher:

    1. Hashes each product's content deterministically
    2. Compares against previous hashes to find add/update/remove
    3. If nothing changed, skips the write entirely
    4. If changes exist, snapshots the old catalog and writes atomically
    5. Writes a manifest file the frontend can poll for cache invalidation

    Snapshots are kept for rollback (configurable max count).
    """

    # Fields excluded from hashing (volatile/meta fields)
    VOLATILE_FIELDS = frozenset([
        "last_updated", "updated_at", "created_at",
        "_pipeline_metadata", "_cross_validation",
        "pipeline_run_id", "ingestion_timestamp",
    ])

    def __init__(
        self,
        catalog_dir: Optional[Path] = None,
        max_snapshots: int = 5,
    ):
        self.catalog_dir = catalog_dir or Path("frontend/public/data")
        self.snapshots_dir = self.catalog_dir / "snapshots"
        self.hashes_path = self.catalog_dir / "product_hashes.json"
        self.max_snapshots = max_snapshots
        self.catalog_dir.mkdir(parents=True, exist_ok=True)

    def publish(
        self,
        products: List[dict],
        catalog_filename: str = "catalog.json",
    ) -> PublishResult:
        """
        Publish a new catalog version.

        Only writes if products actually changed. Creates a versioned
        snapshot of the previous catalog for rollback.

        Args:
            products: List of product dicts to publish
            catalog_filename: Output filename within catalog_dir

        Returns:
            PublishResult with diff information
        """
        version = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        try:
            # 1. Compute hashes for new products
            new_hashes: dict = {}
            products_by_id: dict = {}
            for p in products:
                pid = self._get_product_id(p)
                product_hash = self._hash_product(p)
                new_hashes[pid] = product_hash
                products_by_id[pid] = p

            # 2. Load previous hashes
            old_hashes = self._load_hashes()

            # 3. Compute diff
            diff = self._compute_diff(old_hashes, new_hashes)

            if not diff.has_changes:
                logger.info("No changes detected — skipping publish")
                return PublishResult(
                    success=True,
                    version=version,
                    diff=diff,
                    catalog_path=str(self.catalog_dir / catalog_filename),
                )

            logger.info(f"Publishing catalog v{version}: {diff.summary}")

            # 4. Snapshot current catalog for rollback
            self._create_snapshot(catalog_filename, version)

            # 5. Write new catalog atomically
            catalog_path = self.catalog_dir / catalog_filename
            temp_path = self.catalog_dir / f".{catalog_filename}.tmp"

            catalog_data = {
                "version": version,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_products": len(products),
                "diff_summary": diff.summary,
                "products": products,
            }

            temp_path.write_text(
                json.dumps(catalog_data, indent=2, default=str)
            )
            temp_path.rename(catalog_path)  # Atomic on POSIX

            # 6. Save new hashes
            self._save_hashes(new_hashes)

            # 7. Write publish manifest for frontend
            self._write_manifest(version, diff)

            # 8. Cleanup old snapshots
            self._cleanup_snapshots()

            return PublishResult(
                success=True,
                version=version,
                diff=diff,
                catalog_path=str(catalog_path),
            )

        except Exception as e:
            logger.error(f"Publish failed: {e}")
            return PublishResult(
                success=False,
                version=version,
                diff=PublishDiff(),
                catalog_path="",
                error=str(e),
            )

    def rollback(self, target_version: Optional[str] = None) -> bool:
        """
        Rollback to a previous catalog version.

        Args:
            target_version: Specific version to restore, or None for latest snapshot
        """
        if not self.snapshots_dir.exists():
            logger.error("No snapshots directory found")
            return False

        snapshots = sorted(
            self.snapshots_dir.iterdir(),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        if not snapshots:
            logger.error("No snapshots available for rollback")
            return False

        if target_version:
            target = next(
                (s for s in snapshots if target_version in s.name),
                None,
            )
            if not target:
                logger.error(
                    f"Snapshot for version {target_version} not found")
                return False
        else:
            target = snapshots[0]

        # Extract original filename from snapshot name (version_filename.json)
        parts = target.name.split("_", 2)
        if len(parts) >= 3:
            original_name = parts[2]
        else:
            original_name = "catalog.json"

        dest = self.catalog_dir / original_name
        dest.write_bytes(target.read_bytes())
        logger.info(f"Rolled back to snapshot: {target.name}")
        return True

    # ------------------------------------------------------------------
    # Internal methods
    # ------------------------------------------------------------------

    def _get_product_id(self, product: dict) -> str:
        """Extract a stable product ID."""
        for key in ("id", "sku", "halilit_id", "product_id"):
            val = product.get(key)
            if val:
                return str(val)
        # Fallback: hash the whole product
        return hashlib.sha256(
            json.dumps(product, sort_keys=True, default=str).encode()
        ).hexdigest()[:16]

    def _hash_product(self, product: dict) -> str:
        """Create a deterministic hash of product content (excluding volatile fields)."""
        stable = {
            k: v for k, v in product.items()
            if k not in self.VOLATILE_FIELDS
        }
        content = json.dumps(stable, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _load_hashes(self) -> dict:
        """Load previous product hashes from disk."""
        if self.hashes_path.exists():
            try:
                return json.loads(self.hashes_path.read_text())
            except (json.JSONDecodeError, OSError):
                pass
        return {}

    def _save_hashes(self, hashes: dict):
        """Save product hashes to disk."""
        self.hashes_path.write_text(json.dumps(hashes, indent=2))

    def _compute_diff(
        self, old: dict, new: dict
    ) -> PublishDiff:
        """Compute the diff between old and new product hashes."""
        diff = PublishDiff()
        old_ids = set(old.keys())
        new_ids = set(new.keys())

        diff.added = sorted(new_ids - old_ids)
        diff.removed = sorted(old_ids - new_ids)

        for pid in sorted(old_ids & new_ids):
            if old[pid] != new[pid]:
                diff.updated.append(pid)
            else:
                diff.unchanged.append(pid)

        return diff

    def _create_snapshot(self, catalog_filename: str, version: str):
        """Snapshot current catalog for potential rollback."""
        current = self.catalog_dir / catalog_filename
        if current.exists():
            self.snapshots_dir.mkdir(parents=True, exist_ok=True)
            snapshot_path = self.snapshots_dir / \
                f"{version}_{catalog_filename}"
            snapshot_path.write_bytes(current.read_bytes())
            logger.debug(f"Snapshot created: {snapshot_path.name}")

    def _cleanup_snapshots(self):
        """Keep only the N most recent snapshots."""
        if not self.snapshots_dir.exists():
            return
        snapshots = sorted(
            self.snapshots_dir.iterdir(),
            key=lambda p: p.stat().st_mtime,
        )
        while len(snapshots) > self.max_snapshots:
            old = snapshots.pop(0)
            old.unlink()
            logger.debug(f"Removed old snapshot: {old.name}")

    def _write_manifest(self, version: str, diff: PublishDiff):
        """
        Write a manifest file the frontend can poll for cache invalidation.

        The frontend can check manifest.version and reload if it changed.
        """
        manifest = {
            "version": version,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "changes": {
                "added": len(diff.added),
                "updated": len(diff.updated),
                "removed": len(diff.removed),
            },
            "changed_ids": diff.added + diff.updated,
        }
        manifest_path = self.catalog_dir / "publish_manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2))

    def get_available_snapshots(self) -> List[dict]:
        """List available snapshots for rollback."""
        if not self.snapshots_dir.exists():
            return []
        return [
            {
                "name": s.name,
                "size_kb": round(s.stat().st_size / 1024, 1),
                "modified": datetime.fromtimestamp(
                    s.stat().st_mtime, tz=timezone.utc
                ).isoformat(),
            }
            for s in sorted(
                self.snapshots_dir.iterdir(),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
        ]


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_diff_publisher: Optional[DiffPublisher] = None


def get_diff_publisher() -> DiffPublisher:
    """Get or create the singleton DiffPublisher."""
    global _diff_publisher
    if _diff_publisher is None:
        _diff_publisher = DiffPublisher()
    return _diff_publisher
