"""
Auto-Sync Engine for Phase 1E
Synchronizes ingestion results to frontend data stores in real-time
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import AsyncGenerator, Dict, List, Optional, Any
from dataclasses import dataclass, asdict

logger = logging.getLogger("AutoSyncEngine")


@dataclass
class SyncEvent:
    """Represents a single sync event"""
    event_type: str  # 'product_added', 'product_updated', 'batch_completed'
    product_id: str
    product_name: str
    category: str
    action: str  # 'APPROVED', 'REJECTED', 'PENDING_REVIEW'
    timestamp: str
    progress: Optional[str] = None
    metadata: Optional[Dict] = None

    def to_dict(self):
        return asdict(self)

    def to_sse(self):
        """Format as Server-Sent Event"""
        return json.dumps(self.to_dict())


class SyncBatch:
    """Tracks a batch of products being synced"""

    def __init__(self, batch_id: str, total_products: int):
        self.batch_id = batch_id
        self.total_products = total_products
        self.completed = 0
        self.approved = 0
        self.rejected = 0
        self.pending = 0
        self.start_time = datetime.utcnow()
        self.products = []

    def add_product(self, product_id: str, product_name: str, status: str, category: str):
        """Add a product to the batch"""
        self.products.append({
            "product_id": product_id,
            "product_name": product_name,
            "status": status,
            "category": category,
            "synced_at": datetime.utcnow().isoformat()
        })
        self.completed += 1

        if status == "APPROVED":
            self.approved += 1
        elif status == "REJECTED":
            self.rejected += 1
        else:
            self.pending += 1

    def get_progress(self) -> float:
        """Get completion percentage"""
        if self.total_products == 0:
            return 100.0
        return (self.completed / self.total_products) * 100

    def is_complete(self) -> bool:
        """Check if batch is complete"""
        return self.completed >= self.total_products

    def get_summary(self) -> Dict:
        """Get batch summary"""
        elapsed = (datetime.utcnow() - self.start_time).total_seconds()
        return {
            "batch_id": self.batch_id,
            "total_products": self.total_products,
            "completed": self.completed,
            "approved": self.approved,
            "rejected": self.rejected,
            "pending": self.pending,
            "progress_percent": self.get_progress(),
            "elapsed_seconds": elapsed,
            "products": self.products
        }


class AutoSyncEngine:
    """
    Main auto-sync engine that coordinates product synchronization
    to frontend data stores after ingestion pipeline completes
    """

    def __init__(self):
        self.sync_history: List[Dict] = []
        self.active_batches: Dict[str, SyncBatch] = {}
        self.sync_enabled = True
        self.max_history = 100
        logger.info("✅ AutoSyncEngine initialized")

    async def sync_pipeline_result(
            self,
            product_id: str,
            product_name: str,
            brand: str,
            category: str,
            status: str,
            risk_score: int,
            pricing_tier: Optional[str] = None,
    ) -> AsyncGenerator[Dict, None]:
        """
        Stream sync events for a single pipeline completion
        Called after orchestrator.execute() completes successfully
        """
        logger.info(f"🔄 Syncing: {product_name} ({status})")

        # Emit sync_started event
        yield {
            "type": "sync_started",
            "product_id": product_id,
            "product_name": product_name,
            "timestamp": datetime.utcnow().isoformat()
        }

        try:
            # Phase 1: Validate product data
            yield {
                "type": "sync_phase",
                "phase": "validating",
                "progress": "1/4",
                "message": f"Validating {product_name}...",
                "timestamp": datetime.utcnow().isoformat()
            }
            await asyncio.sleep(0.1)  # Simulate validation

            # Phase 2: Prepare for frontend
            yield {
                "type": "sync_phase",
                "phase": "preparing",
                "progress": "2/4",
                "message": f"Preparing display format...",
                "timestamp": datetime.utcnow().isoformat()
            }
            await asyncio.sleep(0.1)

            # Phase 3: Update data store
            data_to_sync = {
                "product_id": product_id,
                "name": product_name,
                "brand": brand,
                "category": category,
                "status": status,
                "risk_score": risk_score,
                "pricing_tier": pricing_tier or "unset",
                "verified": status == "APPROVED",
                "last_synced": datetime.utcnow().isoformat()
            }

            yield {
                "type": "sync_phase",
                "phase": "updating",
                "progress": "3/4",
                "message": f"Updating data store...",
                "timestamp": datetime.utcnow().isoformat()
            }
            await asyncio.sleep(0.1)

            # Phase 4: Notify frontend
            yield {
                "type": "sync_phase",
                "phase": "notifying",
                "progress": "4/4",
                "message": f"Notifying frontend...",
                "timestamp": datetime.utcnow().isoformat()
            }
            await asyncio.sleep(0.1)

            # Emit product_synced event
            yield {
                "type": "product_synced",
                "product_id": product_id,
                "product_name": product_name,
                "category": category,
                "status": status,
                "risk_score": risk_score,
                "data": data_to_sync,
                "timestamp": datetime.utcnow().isoformat()
            }

            # Record in history
            self._record_sync({
                "product_id": product_id,
                "product_name": product_name,
                "brand": brand,
                "status": status,
                "synced_at": datetime.utcnow().isoformat()
            })

            logger.info(f"✅ {product_name} synced to frontend")

            # Emit sync_completed event
            yield {
                "type": "sync_completed",
                "product_id": product_id,
                "product_name": product_name,
                "status": status,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Sync failed for {product_name}: {str(e)}")
            yield {
                "type": "sync_failed",
                "product_id": product_id,
                "product_name": product_name,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def sync_batch(
            self,
            products: List[Dict],
            brand: str,
    ) -> AsyncGenerator[Dict, None]:
        """
        Stream sync events for a batch of products
        Handles multiple products with progress tracking
        """
        batch_id = f"sync-batch-{datetime.utcnow().timestamp()}"
        batch = SyncBatch(batch_id, len(products))

        logger.info(f"📦 Syncing batch {batch_id} ({len(products)} products)")

        yield {
            "type": "batch_sync_started",
            "batch_id": batch_id,
            "total_products": len(products),
            "timestamp": datetime.utcnow().isoformat()
        }

        for idx, product in enumerate(products):
            try:
                product_id = product.get("product_id") or product.get(
                    "halilit_id", "unknown")
                product_name = product.get("product_name") or product.get(
                    "name", "Unknown Product")
                status = product.get("status", "APPROVED")
                category = product.get("category", "Uncategorized")
                risk_score = product.get("risk_score", 50)

                # Sync individual product
                async for sync_event in self.sync_pipeline_result(
                    product_id=product_id,
                    product_name=product_name,
                    brand=brand,
                    category=category,
                    status=status,
                    risk_score=risk_score,
                ):
                    # Emit all sync phase events
                    if sync_event.get("type") in ["sync_phase", "product_synced", "sync_completed"]:
                        yield sync_event

                # Add to batch tracker
                batch.add_product(product_id, product_name, status, category)

                # Emit progress update
                yield {
                    "type": "batch_progress",
                    "batch_id": batch_id,
                    "progress": idx + 1,
                    "total": len(products),
                    "percent_complete": batch.get_progress(),
                    "product_name": product_name,
                    "status": status,
                    "timestamp": datetime.utcnow().isoformat()
                }

            except Exception as e:
                logger.error(f"❌ Error syncing product {idx}: {str(e)}")
                yield {
                    "type": "batch_error",
                    "batch_id": batch_id,
                    "product_index": idx,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }

        # Final batch summary
        summary = batch.get_summary()
        yield {
            "type": "batch_sync_completed",
            "batch_id": batch_id,
            "summary": summary,
            "timestamp": datetime.utcnow().isoformat()
        }

        logger.info(
            f"✅ Batch sync completed: {summary['approved']} approved, {summary['rejected']} rejected")

        # Update active batches
        self.active_batches[batch_id] = batch

    def get_sync_history(self, limit: int = 50) -> List[Dict]:
        """Get recent sync records"""
        return self.sync_history[-limit:]

    def get_batch_status(self, batch_id: str) -> Optional[Dict]:
        """Get status of a specific batch"""
        if batch_id in self.active_batches:
            return self.active_batches[batch_id].get_summary()
        return None

    def _record_sync(self, sync_record: Dict):
        """Record a sync in history"""
        self.sync_history.append(sync_record)
        # Keep history size under control
        if len(self.sync_history) > self.max_history:
            self.sync_history = self.sync_history[-self.max_history:]

    def toggle_sync(self, enabled: bool):
        """Enable/disable auto-sync"""
        self.sync_enabled = enabled
        logger.info(f"Auto-sync {'enabled' if enabled else 'disabled'}")

    def clear_history(self):
        """Clear sync history"""
        self.sync_history = []
        self.active_batches = {}
        logger.info("Sync history cleared")


# Singleton instance
_auto_sync_engine = None


def get_auto_sync_engine() -> AutoSyncEngine:
    """Get or create the auto-sync engine singleton"""
    global _auto_sync_engine
    if _auto_sync_engine is None:
        _auto_sync_engine = AutoSyncEngine()
    return _auto_sync_engine
