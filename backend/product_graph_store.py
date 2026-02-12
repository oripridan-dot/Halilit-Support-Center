"""
╔══════════════════════════════════════════════════════════════════════════════╗
║        PRODUCT GRAPH STORE — Dual Persistence (PostgreSQL + JSON)          ║
║                                                                             ║
║  PostgreSQL is the authoritative source of truth for:                       ║
║    - Product families                                                       ║
║    - Product relationships (AI-discovered + manually curated)               ║
║    - Canonical product data                                                 ║
║                                                                             ║
║  JSON snapshots in backend/data/graph/ provide fast cold-start reads        ║
║  without requiring a database connection during development.                ║
║                                                                             ║
║  VERSION: 1.0                                                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.product_graph import (
    CanonicalProduct,
    ProductFamily,
    ProductGraph,
    ProductRelationship,
    RelationshipDirection,
    RelationshipType,
)

logger = logging.getLogger("GraphStore")

# JSON snapshot directory
GRAPH_DATA_DIR = Path(__file__).parent / "data" / "graph"


class GraphStore:
    """
    Dual-persistence layer for the Canonical Product Graph.

    Write path:  mutation → PostgreSQL → JSON snapshot refresh
    Read path:   JSON snapshot (fast) → fallback to PostgreSQL if stale
    """

    def __init__(self, db_url: Optional[str] = None):
        self.db_url = db_url or os.getenv(
            "DATABASE_URL",
            "postgresql://halilit_user:secure_password_change_me@localhost:5432/halilit_tasks"
        )
        self._graph: Optional[ProductGraph] = None
        GRAPH_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # ═══════════════════════════════════════════════════════════════════
    # JSON SNAPSHOT PERSISTENCE (Fast reads, development-friendly)
    # ═══════════════════════════════════════════════════════════════════

    def export_json_snapshot(self, graph: ProductGraph) -> Path:
        """
        Write the entire graph to a JSON snapshot file.
        Used as a read cache and for development without PostgreSQL.
        """
        snapshot_path = GRAPH_DATA_DIR / "product_graph.json"
        backup_path = GRAPH_DATA_DIR / \
            f"product_graph_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"

        # Build serializable snapshot
        snapshot = {
            "version": graph.version,
            "exported_at": datetime.utcnow().isoformat(),
            "stats": graph.get_graph_stats(),
            "families": {
                fid: family.model_dump()
                for fid, family in graph.families.items()
            },
            "relationships": [
                rel.model_dump() for rel in graph.relationships
            ],
            # Products are NOT stored here — they come from the catalog pipeline.
            # Only graph-specific data (families + relationships) is persisted.
        }

        # Atomic write with backup
        try:
            if snapshot_path.exists():
                # Keep previous version as backup
                snapshot_path.rename(backup_path)

            with open(snapshot_path, "w") as f:
                json.dump(snapshot, f, indent=2, default=str)

            logger.info(
                f"Graph snapshot exported: {len(graph.families)} families, "
                f"{len(graph.relationships)} relationships → {snapshot_path}"
            )
            return snapshot_path

        except Exception as e:
            logger.error(f"Failed to export graph snapshot: {e}")
            # Restore backup if write failed
            if backup_path.exists() and not snapshot_path.exists():
                backup_path.rename(snapshot_path)
            raise

    def import_json_snapshot(self) -> Optional[Dict[str, Any]]:
        """
        Load the graph snapshot from JSON.
        Returns raw dict with families + relationships, or None if no snapshot.
        """
        snapshot_path = GRAPH_DATA_DIR / "product_graph.json"
        if not snapshot_path.exists():
            logger.info("No graph snapshot found — starting with empty graph")
            return None

        try:
            with open(snapshot_path, "r") as f:
                snapshot = json.load(f)

            logger.info(
                f"Graph snapshot loaded: v{snapshot.get('version', '?')}, "
                f"exported {snapshot.get('exported_at', '?')}"
            )
            return snapshot

        except Exception as e:
            logger.error(f"Failed to load graph snapshot: {e}")
            return None

    def load_graph_overlay(self, graph: ProductGraph) -> ProductGraph:
        """
        Load families and relationships from the JSON snapshot and
        overlay them onto an existing graph (which already has products
        from the catalog pipeline).
        """
        snapshot = self.import_json_snapshot()
        if not snapshot:
            return graph

        # Load families
        for fid, fam_data in snapshot.get("families", {}).items():
            try:
                family = ProductFamily(**fam_data)
                # Only keep variant_ids that actually exist in the product catalog
                family.variant_ids = [
                    vid for vid in family.variant_ids
                    if vid in graph.products
                ]
                if family.variant_ids:  # Don't add empty families
                    graph.add_family(family)
                    # Tag products with their family_id
                    for vid in family.variant_ids:
                        if vid in graph.products:
                            graph.products[vid].family_id = family.id
            except Exception as e:
                logger.warning(f"Failed to load family {fid}: {e}")

        # Load relationships
        for rel_data in snapshot.get("relationships", []):
            try:
                rel = ProductRelationship(**rel_data)
                # Only keep relationships where both products exist
                if rel.source_id in graph.products and rel.target_id in graph.products:
                    graph.add_relationship(rel)
            except Exception as e:
                logger.warning(f"Failed to load relationship: {e}")

        graph.rebuild_indexes()
        stats = graph.get_graph_stats()
        logger.info(
            f"Graph overlay applied: {stats['total_families']} families, "
            f"{stats['total_relationships']} relationships, "
            f"{stats['products_in_families']} products in families"
        )
        return graph

    # ═══════════════════════════════════════════════════════════════════
    # POSTGRESQL PERSISTENCE (Authoritative source of truth)
    # ═══════════════════════════════════════════════════════════════════

    async def save_to_postgres(self, graph: ProductGraph) -> Dict[str, int]:
        """
        Persist the graph to PostgreSQL (families + relationships).
        Uses upsert semantics — safe to call repeatedly.

        Returns counts of rows written.
        """
        try:
            import asyncpg
        except ImportError:
            logger.warning("asyncpg not installed — skipping PostgreSQL save. "
                           "Install with: pip install asyncpg")
            # Fall back to JSON-only persistence
            self.export_json_snapshot(graph)
            return {"families": 0, "relationships": 0, "fallback": "json"}

        conn = None
        counts = {"families": 0, "relationships": 0}

        try:
            conn = await asyncpg.connect(self.db_url)

            # Upsert families
            for fid, family in graph.families.items():
                await conn.execute("""
                    INSERT INTO product_families (id, brand, family_name, series,
                                                  generation, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, NOW(), NOW())
                    ON CONFLICT (id) DO UPDATE SET
                        family_name = EXCLUDED.family_name,
                        series = EXCLUDED.series,
                        generation = EXCLUDED.generation,
                        updated_at = NOW()
                """, fid, family.brand, family.family_name,
                                   family.series, family.generation)
                counts["families"] += 1

            # Clear and re-insert relationships (simpler than diffing)
            await conn.execute("DELETE FROM product_relationships")

            for rel in graph.relationships:
                await conn.execute("""
                    INSERT INTO product_relationships
                        (source_product_id, target_product_id, relationship_type,
                         confidence, ai_discovered, manually_curated,
                         compatibility_notes, bidirectional, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW())
                """, rel.source_id, rel.target_id, rel.relationship_type.value,
                                   rel.confidence, rel.ai_discovered, rel.manually_curated,
                                   rel.compatibility_notes,
                                   rel.direction == RelationshipDirection.BIDIRECTIONAL)
                counts["relationships"] += 1

            logger.info(
                f"Graph saved to PostgreSQL: {counts['families']} families, "
                f"{counts['relationships']} relationships"
            )

        except Exception as e:
            logger.error(f"PostgreSQL save failed: {e}")
            logger.info("Falling back to JSON snapshot only")

        finally:
            if conn:
                await conn.close()

        # Always update JSON snapshot too
        self.export_json_snapshot(graph)
        return counts

    async def load_from_postgres(self, graph: ProductGraph) -> ProductGraph:
        """
        Load families and relationships from PostgreSQL and overlay
        onto the existing graph. Falls back to JSON if DB unavailable.
        """
        try:
            import asyncpg
        except ImportError:
            logger.info("asyncpg not installed — using JSON snapshot only")
            return self.load_graph_overlay(graph)

        conn = None
        try:
            conn = await asyncpg.connect(self.db_url)

            # Load families
            rows = await conn.fetch("SELECT * FROM product_families")
            for row in rows:
                family = ProductFamily(
                    id=str(row["id"]),
                    brand=row["brand"],
                    family_name=row["family_name"],
                    series=row.get("series", ""),
                    generation=row.get("generation"),
                )
                # Variant IDs need to be rebuilt from product data
                family.variant_ids = [
                    pid for pid, p in graph.products.items()
                    if p.family_id == str(row["id"])
                ]
                if family.variant_ids:
                    graph.add_family(family)

            # Load relationships
            rows = await conn.fetch(
                "SELECT * FROM product_relationships ORDER BY confidence DESC"
            )
            for row in rows:
                try:
                    rel = ProductRelationship(
                        source_id=row["source_product_id"],
                        target_id=row["target_product_id"],
                        relationship_type=RelationshipType(
                            row["relationship_type"]),
                        confidence=float(row["confidence"]),
                        ai_discovered=row["ai_discovered"],
                        manually_curated=row["manually_curated"],
                        compatibility_notes=row.get("compatibility_notes", ""),
                        direction=(RelationshipDirection.BIDIRECTIONAL
                                   if row.get("bidirectional") else
                                   RelationshipDirection.UNIDIRECTIONAL),
                    )
                    if rel.source_id in graph.products and rel.target_id in graph.products:
                        graph.add_relationship(rel)
                except Exception as e:
                    logger.warning(f"Skipping invalid relationship: {e}")

            graph.rebuild_indexes()
            stats = graph.get_graph_stats()
            logger.info(
                f"Graph loaded from PostgreSQL: {stats['total_families']} families, "
                f"{stats['total_relationships']} relationships"
            )

        except Exception as e:
            logger.warning(
                f"PostgreSQL load failed ({e}), falling back to JSON snapshot")
            return self.load_graph_overlay(graph)

        finally:
            if conn:
                await conn.close()

        return graph

    # ═══════════════════════════════════════════════════════════════════
    # CURATION OPERATIONS (for the curation API)
    # ═══════════════════════════════════════════════════════════════════

    def add_curated_relationship(self, graph: ProductGraph,
                                 source_id: str, target_id: str,
                                 rel_type: RelationshipType,
                                 notes: str = "") -> ProductRelationship:
        """Add a manually curated relationship."""
        rel = ProductRelationship(
            source_id=source_id,
            target_id=target_id,
            relationship_type=rel_type,
            confidence=1.0,
            ai_discovered=False,
            manually_curated=True,
            compatibility_notes=notes,
        )
        graph.add_relationship(rel)
        # Persist immediately
        self.export_json_snapshot(graph)
        return rel

    def confirm_relationship(self, graph: ProductGraph,
                             source_id: str, target_id: str,
                             rel_type: RelationshipType) -> bool:
        """Confirm an AI-discovered relationship (sets manually_curated=True)."""
        for rel in graph.relationships:
            if (rel.source_id == source_id and rel.target_id == target_id
                    and rel.relationship_type == rel_type):
                rel.manually_curated = True
                rel.confidence = max(rel.confidence, 0.95)
                rel.updated_at = datetime.utcnow().isoformat()
                self.export_json_snapshot(graph)
                return True
        return False

    def reject_relationship(self, graph: ProductGraph,
                            source_id: str, target_id: str,
                            rel_type: RelationshipType) -> bool:
        """Reject and remove a relationship."""
        removed = graph.remove_relationship(source_id, target_id, rel_type)
        if removed:
            self.export_json_snapshot(graph)
        return removed

    def get_pending_relationships(self, graph: ProductGraph) -> List[Dict[str, Any]]:
        """Get all AI-discovered relationships that need human review."""
        _unknown = CanonicalProduct(id="", name="Unknown", brand="Unknown")
        pending = []
        for rel in graph.relationships:
            if rel.needs_review:
                source = graph.products.get(rel.source_id, _unknown)
                target = graph.products.get(rel.target_id, _unknown)
                pending.append({
                    **rel.model_dump(),
                    "source_name": source.name,
                    "target_name": target.name,
                    "source_brand": source.brand,
                    "target_brand": target.brand,
                    "source_image": source.image_url or "",
                    "target_image": target.image_url or "",
                })
        return sorted(pending, key=lambda x: -x["confidence"])

    def get_curation_stats(self, graph: ProductGraph) -> Dict[str, Any]:
        """Coverage metrics for the curation dashboard."""
        stats = graph.get_graph_stats()
        total_products = len(graph.products)

        stats["family_coverage_pct"] = round(
            100 * stats["products_in_families"] / max(total_products, 1), 1
        )

        products_with_accessories = set()
        for rel in graph.relationships:
            if rel.relationship_type == RelationshipType.ACCESSORY_FOR:
                products_with_accessories.add(rel.target_id)
        stats["products_with_accessories"] = len(products_with_accessories)
        stats["accessory_coverage_pct"] = round(
            100 * len(products_with_accessories) / max(total_products, 1), 1
        )

        return stats


# ═══════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════

_store_instance: Optional[GraphStore] = None


def get_graph_store() -> GraphStore:
    """Get the singleton GraphStore instance."""
    global _store_instance
    if _store_instance is None:
        _store_instance = GraphStore()
    return _store_instance
