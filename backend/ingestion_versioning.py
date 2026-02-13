"""
Ingestion Versioning System - v8.5

Manages version tracking for ingested product data across the Trinity Swarm pipeline.
Tracks when data was harvested, enriched, validated, and approved.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from pathlib import Path
import json
import logging

logger = logging.getLogger("VersionManager")


class IngestionPhase(Enum):
    """Phases of the ingestion pipeline"""
    HARVESTED = "harvested"          # CommercialScout extracted
    ENRICHED = "enriched"             # OfficialVerifier added specs
    TIERED = "tiered"                 # PricingEngine categorized
    PREPARED = "prepared"             # DataWarehouse prepared
    VALIDATED = "validated"           # ExternalValidator audited
    APPROVED = "approved"             # Ready for frontend
    FAILED = "failed"                 # Quality gates rejected


@dataclass
class IngestionVersion:
    """
    Represents a single version of ingested product data.
    Tracks lifecycle from harvest through approval.
    """

    brand: str
    version_id: str                    # e.g., "20260207-001"
    batch_id: str = ""                 # Unique batch run identifier
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc))
    phase: IngestionPhase = field(default=IngestionPhase.HARVESTED)

    # Product counts at each phase
    product_count: int = 0
    products_enriched: int = 0
    products_validated: int = 0
    products_approved: int = 0

    # Agent responsible for current phase
    agent_responsible: str = ""

    # Quality metrics
    completeness_score: float = 0.0
    accuracy_score: float = 0.0
    compliance_score: float = 0.0

    # Metadata
    # "commercial_scout", "manual_upload", etc.
    source: str = ""
    notes: str = ""
    errors: List[str] = field(default_factory=list)

    def is_approved(self) -> bool:
        """Check if version is ready for frontend"""
        return self.phase == IngestionPhase.APPROVED and self.compliance_score >= 85.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for JSON serialization"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['phase'] = self.phase.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IngestionVersion':
        """Reconstruct from dict"""
        data = data.copy()
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['phase'] = IngestionPhase(data['phase'])
        return cls(**data)


class VersionManager:
    """
    Central version store for all ingestion operations.
    Tracks every version of every brand through the pipeline.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize version manager"""
        if storage_path is None:
            storage_path = Path(
                "/workspaces/Halilit-Support-Center/backend/data/ingestion/versions")

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.versions: Dict[str, List[IngestionVersion]] = {}
        self._load_all_versions()

    def _load_all_versions(self):
        """Load all persisted versions from disk"""
        if not self.storage_path.exists():
            return

        for version_file in self.storage_path.glob("*.json"):
            try:
                with open(version_file) as f:
                    data = json.load(f)
                    version = IngestionVersion.from_dict(data)
                    brand = version.brand
                    if brand not in self.versions:
                        self.versions[brand] = []
                    self.versions[brand].append(version)
                    logger.info(
                        f"Loaded version: {brand}/{version.version_id}")
            except Exception as e:
                logger.warning(f"Failed to load {version_file}: {e}")

    def create_version(
        self,
        brand: str,
        source: str = "conductor_cli",
        notes: str = ""
    ) -> IngestionVersion:
        """Create a new version for a brand"""
        # Generate version ID from timestamp
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        version_id = f"{timestamp}-{brand}"

        version = IngestionVersion(
            brand=brand,
            version_id=version_id,
            source=source,
            notes=notes,
            phase=IngestionPhase.HARVESTED,
            agent_responsible="conductor_cli"
        )

        if brand not in self.versions:
            self.versions[brand] = []
        self.versions[brand].append(version)
        self._persist_version(version)

        logger.info(f"Created version: {version_id}")
        return version

    def update_version(self, version: IngestionVersion) -> None:
        """Update an existing version"""
        self._persist_version(version)
        logger.info(f"Updated version: {version.version_id}")

    def _persist_version(self, version: IngestionVersion) -> None:
        """Save version to disk"""
        filename = f"{version.brand}_{version.version_id.replace('/', '_')}.json"
        filepath = self.storage_path / filename

        with open(filepath, 'w') as f:
            json.dump(version.to_dict(), f, indent=2)

    def get_latest_version(self, brand: str) -> Optional[IngestionVersion]:
        """Get the latest version for a brand"""
        if brand not in self.versions or not self.versions[brand]:
            return None
        return sorted(
            self.versions[brand],
            key=lambda v: v.created_at,
            reverse=True
        )[0]

    def get_approved_versions(self) -> Dict[str, IngestionVersion]:
        """Get latest approved version for each brand"""
        approved = {}
        for brand, versions in self.versions.items():
            approved_versions = [v for v in versions if v.is_approved()]
            if approved_versions:
                approved[brand] = sorted(
                    approved_versions,
                    key=lambda v: v.created_at,
                    reverse=True
                )[0]
        return approved

    def get_all_brands(self) -> List[str]:
        """Get all brands with versions"""
        return sorted(self.versions.keys())

    def export_for_frontend(self) -> Dict[str, Any]:
        """Export version info for frontend consumption"""
        approved = self.get_approved_versions()

        return {
            "total_brands": len(self.versions),
            "approved_brands": len(approved),
            "total_versions": sum(len(v) for v in self.versions.values()),
            "active_versions": {
                brand: {
                    "version_id": v.version_id,
                    "phase": v.phase.value,
                    "product_count": v.product_count,
                    "created_at": v.created_at.isoformat(),
                    "completeness_score": v.completeness_score,
                    "accuracy_score": v.accuracy_score,
                    "compliance_score": v.compliance_score,
                }
                for brand, v in approved.items()
            }
        }

    def stats_summary(self) -> Dict[str, Any]:
        """Get summary statistics"""
        all_versions = []
        for versions in self.versions.values():
            all_versions.extend(versions)

        if not all_versions:
            return {
                "total_versions": 0,
                "total_brands": 0,
                "phases": {}
            }

        phases = {}
        for phase in IngestionPhase:
            count = len([v for v in all_versions if v.phase == phase])
            if count > 0:
                phases[phase.value] = count

        return {
            "total_versions": len(all_versions),
            "total_brands": len(self.versions),
            "phases": phases,
            "latest_version": (
                sorted(all_versions, key=lambda v: v.created_at,
                       reverse=True)[0].version_id
                if all_versions else None
            )
        }


# Singleton instance
_version_manager: Optional[VersionManager] = None


def get_version_manager() -> VersionManager:
    """Get or create the global version manager"""
    global _version_manager

    if _version_manager is None:
        _version_manager = VersionManager()

    return _version_manager


def reset_version_manager() -> None:
    """Reset the version manager (for testing)"""
    global _version_manager
    _version_manager = None


if __name__ == "__main__":
    # Test the version manager
    manager = get_version_manager()

    # Create a test version
    test_version = manager.create_version(
        brand="test_brand",
        source="test",
        notes="Test version creation"
    )

    print(f"Created: {test_version.version_id}")
    print(f"Stats: {manager.stats_summary()}")
    print(
        f"Frontend export: {json.dumps(manager.export_for_frontend(), indent=2)}")
