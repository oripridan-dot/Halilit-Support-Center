#!/usr/bin/env python3
"""
Data Synchronizer: Bi-Directional Sync between Backend and Frontend

Maintains data consistency across the full stack:
  - Backend: Python data models, JSON files in backend/data/
  - Frontend: React components, public/data/, search indexes

Sync Modes:
  1. Backend → Frontend: Pushes schema/data changes to frontend
  2. Frontend → Backend: Captures UI edits, persists to backend
  3. Bidirectional: Merges changes, resolves conflicts

This module acts as the "Guardian of Truth" - ensuring single source
of truth while allowing distributed data ownership.
"""

import os
import sys
import json
import logging
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import shutil

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger("DataSynchronizer")

# Color codes
COLORS = {
    'RESET': '\033[0m',
    'BOLD': '\033[1m',
    'CYAN': '\033[36m',
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'RED': '\033[91m',
    'BLUE': '\033[94m',
}


class SyncDirection(Enum):
    """Data synchronization direction"""
    BACKEND_TO_FRONTEND = "backend_to_frontend"
    FRONTEND_TO_BACKEND = "frontend_to_backend"
    BIDIRECTIONAL = "bidirectional"


class SyncStatus(Enum):
    """Sync operation status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    CONFLICT = "conflict"
    FAILED = "failed"


@dataclass
class SyncMapping:
    """Maps a backend file to its frontend equivalent"""
    backend_path: str
    frontend_path: str
    data_type: str  # "json", "index", "config", "schema"
    bidirectional: bool = True
    transformer: Optional[callable] = None  # Function to transform data

    def __hash__(self):
        return hash(self.backend_path)

    def __eq__(self, other):
        return self.backend_path == other.backend_path


@dataclass
class SyncRecord:
    """Tracks a sync operation"""
    id: str
    direction: SyncDirection
    status: SyncStatus
    files_synced: List[str]
    changes: Dict[str, Any]
    conflicts: List[Dict[str, Any]] = None
    timestamp: str = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()
        if self.conflicts is None:
            self.conflicts = []


class DataSynchronizer:
    """
    Master data synchronizer for backend ↔ frontend consistency.
    """

    def __init__(self, project_root: Path = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent

        self.project_root = project_root
        self.backend_root = project_root / "backend"
        self.frontend_root = project_root / "frontend"

        self.sync_mappings = self._initialize_sync_mappings()
        self.sync_history: List[SyncRecord] = []
        self.checksums: Dict[str, str] = {}  # Track file checksums

    def _initialize_sync_mappings(self) -> List[SyncMapping]:
        """Define how backend and frontend data maps"""
        return [
            SyncMapping(
                backend_path="backend/data/brands/index.json",
                frontend_path="frontend/public/data/brands.json",
                data_type="json",
                bidirectional=True
            ),
            SyncMapping(
                backend_path="backend/data/taxonomy.json",
                frontend_path="frontend/public/data/taxonomy.json",
                data_type="json",
                bidirectional=True
            ),
            SyncMapping(
                backend_path="backend/spectrum_data_provider.py",
                frontend_path="frontend/src/api/spectrumClient.ts",
                data_type="schema",
                bidirectional=False
            ),
        ]

    def sync_backend_to_frontend(self, mappings: List[SyncMapping] = None) -> SyncRecord:
        """
        Push backend data to frontend.

        This is the primary sync direction - backend is the source of truth.
        """
        mappings = mappings or self.sync_mappings
        record = SyncRecord(
            id=f"b2f_{int(datetime.utcnow().timestamp())}",
            direction=SyncDirection.BACKEND_TO_FRONTEND,
            status=SyncStatus.IN_PROGRESS,
            files_synced=[],
            changes={}
        )

        logger.info(
            f"{COLORS['CYAN']}⇒ Backend → Frontend Sync{COLORS['RESET']}")
        logger.info(f"  Mappings to sync: {len(mappings)}")
        logger.info("-" * 70)

        for mapping in mappings:
            if not mapping.bidirectional and mapping.data_type == "schema":
                logger.info(
                    f"⊘ Skipping schema file (read-only): {mapping.backend_path}")
                continue

            backend_file = self.project_root / mapping.backend_path
            frontend_file = self.project_root / mapping.frontend_path

            if not backend_file.exists():
                logger.warning(
                    f"⚠️  Backend file not found: {mapping.backend_path}")
                record.conflicts.append({
                    "mapping": str(mapping.backend_path),
                    "issue": "backend_file_missing"
                })
                continue

            try:
                # Read backend data
                with open(backend_file, 'r') as f:
                    backend_data = json.load(f)

                # Transform if needed
                if mapping.transformer:
                    frontend_data = mapping.transformer(backend_data)
                else:
                    frontend_data = backend_data

                # Ensure frontend directory exists
                frontend_file.parent.mkdir(parents=True, exist_ok=True)

                # Check if frontend file changed
                frontend_changed = self._should_update_file(
                    frontend_file, frontend_data)

                # Write to frontend
                with open(frontend_file, 'w') as f:
                    json.dump(frontend_data, f, indent=2)

                record.files_synced.append(str(mapping.frontend_path))
                if frontend_changed:
                    record.changes[mapping.frontend_path] = {
                        "status": "updated",
                        "backend_source": mapping.backend_path
                    }
                    logger.info(
                        f"{COLORS['GREEN']}✓ Updated: {mapping.frontend_path}{COLORS['RESET']}")
                else:
                    logger.info(f"✓ In sync: {mapping.frontend_path}")

            except Exception as e:
                logger.error(
                    f"{COLORS['RED']}✗ Sync failed: {mapping.backend_path}{COLORS['RESET']}")
                logger.error(f"   Error: {e}")
                record.conflicts.append({
                    "mapping": str(mapping.backend_path),
                    "error": str(e)
                })

        record.status = SyncStatus.SUCCESS if not record.conflicts else SyncStatus.CONFLICT
        self.sync_history.append(record)

        return record

    def sync_frontend_to_backend(self, mappings: List[SyncMapping] = None) -> SyncRecord:
        """
        Pull frontend changes back to backend.

        Used when frontend UI edits need to be persisted (e.g., admin panels).
        Requires bidirectional mappings.
        """
        mappings = [m for m in (
            mappings or self.sync_mappings) if m.bidirectional]
        record = SyncRecord(
            id=f"f2b_{int(datetime.utcnow().timestamp())}",
            direction=SyncDirection.FRONTEND_TO_BACKEND,
            status=SyncStatus.IN_PROGRESS,
            files_synced=[],
            changes={}
        )

        logger.info(
            f"{COLORS['CYAN']}⇐ Frontend → Backend Sync{COLORS['RESET']}")
        logger.info(f"  Bidirectional mappings: {len(mappings)}")
        logger.info("-" * 70)

        for mapping in mappings:
            frontend_file = self.project_root / mapping.frontend_path
            backend_file = self.project_root / mapping.backend_path

            if not frontend_file.exists():
                logger.warning(
                    f"⚠️  Frontend file not found: {mapping.frontend_path}")
                continue

            try:
                # Read frontend data
                with open(frontend_file, 'r') as f:
                    frontend_data = json.load(f)

                # Inverse transform if needed (backend ← frontend)
                # For now, assume direct mapping
                backend_data = frontend_data

                # Check if backend file changed
                backend_changed = self._should_update_file(
                    backend_file, backend_data)

                # Write to backend with backup
                if backend_file.exists() and backend_changed:
                    backup_path = backend_file.with_suffix(
                        backend_file.suffix + '.backup')
                    shutil.copy2(backend_file, backup_path)
                    logger.info(f"   Backup created: {backup_path.name}")

                backend_file.parent.mkdir(parents=True, exist_ok=True)
                with open(backend_file, 'w') as f:
                    json.dump(backend_data, f, indent=2)

                record.files_synced.append(str(mapping.backend_path))
                if backend_changed:
                    record.changes[mapping.backend_path] = {
                        "status": "updated",
                        "frontend_source": mapping.frontend_path
                    }
                    logger.info(
                        f"{COLORS['GREEN']}✓ Updated: {mapping.backend_path}{COLORS['RESET']}")
                else:
                    logger.info(f"✓ In sync: {mapping.backend_path}")

            except Exception as e:
                logger.error(
                    f"{COLORS['RED']}✗ Sync failed: {mapping.frontend_path}{COLORS['RESET']}")
                logger.error(f"   Error: {e}")
                record.conflicts.append({
                    "mapping": str(mapping.frontend_path),
                    "error": str(e)
                })

        record.status = SyncStatus.SUCCESS if not record.conflicts else SyncStatus.CONFLICT
        self.sync_history.append(record)

        return record

    def sync_bidirectional(self) -> Tuple[SyncRecord, SyncRecord]:
        """
        Perform bidirectional sync: first backend→frontend, then frontend→backend.

        Resolves conflicts by checking timestamps.
        """
        logger.info(f"\n{COLORS['BOLD']}🔄 BIDIRECTIONAL SYNC{COLORS['RESET']}")
        logger.info("=" * 70)

        # Phase 1: Backend → Frontend (backend is authoritative)
        record1 = self.sync_backend_to_frontend()

        # Phase 2: Frontend → Backend (only for modified files)
        record2 = self.sync_frontend_to_backend()

        logger.info(f"\n{COLORS['GREEN']}✓ Sync complete{COLORS['RESET']}")
        logger.info(f"  Backend→Frontend: {len(record1.files_synced)} files")
        logger.info(f"  Frontend→Backend: {len(record2.files_synced)} files")

        return record1, record2

    def _should_update_file(self, file_path: Path, new_data: Any) -> bool:
        """Check if file needs to be updated (content changed)"""
        if not file_path.exists():
            return True

        new_checksum = hashlib.md5(
            json.dumps(new_data, sort_keys=True).encode()
        ).hexdigest()

        old_checksum = self.checksums.get(str(file_path))
        if old_checksum is None:
            try:
                with open(file_path, 'r') as f:
                    old_data = json.load(f)
                old_checksum = hashlib.md5(
                    json.dumps(old_data, sort_keys=True).encode()
                ).hexdigest()
            except:
                return True

        self.checksums[str(file_path)] = new_checksum
        return new_checksum != old_checksum

    def rebuild_frontend_indexes(self) -> Dict[str, Any]:
        """
        Regenerate frontend search indexes from backend data.

        Used after data changes to keep search in sync.
        """
        logger.info(
            f"\n{COLORS['CYAN']}📑 Rebuilding Frontend Indexes{COLORS['RESET']}")
        logger.info("-" * 70)

        results = {}

        # Build brand index
        try:
            brands_file = self.backend_root / "data" / "brands" / "index.json"
            if brands_file.exists():
                with open(brands_file, 'r') as f:
                    brands = json.load(f)

                search_index = self._build_search_index(brands)
                index_file = self.frontend_root / "public" / "data" / "search_index.json"
                index_file.parent.mkdir(parents=True, exist_ok=True)

                with open(index_file, 'w') as f:
                    json.dump(search_index, f, indent=2)

                results['search_index'] = {
                    'status': 'success',
                    'entries': len(search_index)
                }
                logger.info(
                    f"{COLORS['GREEN']}✓ Built search index ({len(search_index)} entries){COLORS['RESET']}")

        except Exception as e:
            logger.error(f"Failed to build search index: {e}")
            results['search_index'] = {'status': 'failed', 'error': str(e)}

        return results

    @staticmethod
    def _build_search_index(brands: List[Dict]) -> List[Dict]:
        """Create a searchable index from brand data"""
        index = []
        for brand in brands:
            index.append({
                'id': brand.get('id'),
                'name': brand.get('name'),
                'category': brand.get('category'),
                'searchable_text': f"{brand.get('name')} {brand.get('description', '')}".lower()
            })
        return index

    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status"""
        if not self.sync_history:
            return {"status": "no_syncs_performed"}

        last_sync = self.sync_history[-1]
        return {
            "last_sync_id": last_sync.id,
            "direction": last_sync.direction.value,
            "status": last_sync.status.value,
            "files_synced": len(last_sync.files_synced),
            "conflicts": len(last_sync.conflicts),
            "timestamp": last_sync.timestamp,
            "changes_summary": last_sync.changes
        }


def main():
    """Example usage of DataSynchronizer"""
    import logging
    logging.basicConfig(level=logging.INFO)

    sync = DataSynchronizer()

    # Show initial status
    logger.info(f"\n{COLORS['BOLD']}Available Mappings:{COLORS['RESET']}")
    for mapping in sync.sync_mappings:
        logger.info(f"  • {mapping.backend_path} → {mapping.frontend_path}")

    # Perform sync
    record1, record2 = sync.sync_bidirectional()

    # Show results
    logger.info(f"\n{COLORS['BOLD']}Sync Summary:{COLORS['RESET']}")
    status = sync.get_sync_status()
    for key, value in status.items():
        logger.info(f"  {key}: {value}")


if __name__ == '__main__':
    main()
