"""
Curation Router — REST API for managing the Product Graph.

Provides endpoints for:
- Viewing pending AI-discovered relationships
- Confirming, rejecting, editing relationships
- Creating/merging families manually
- Coverage statistics for the curation dashboard
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger("CurationRouter")

router = APIRouter(prefix="/api/curation", tags=["Product Graph Curation"])


# ═══════════════════════════════════════════════════════════════════════════
# REQUEST / RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════════════════

class CreateRelationshipRequest(BaseModel):
    source_id: str
    target_id: str
    relationship_type: str  # "variant_of", "accessory_for", etc.
    notes: str = ""


class EditRelationshipRequest(BaseModel):
    source_id: str
    target_id: str
    relationship_type: str
    new_type: Optional[str] = None
    new_notes: Optional[str] = None


class CreateFamilyRequest(BaseModel):
    brand: str
    family_name: str
    series: str = ""
    generation: Optional[int] = None
    product_ids: List[str] = Field(default_factory=list)


class MergeFamiliesRequest(BaseModel):
    source_family_id: str
    target_family_id: str


# ═══════════════════════════════════════════════════════════════════════════
# GRAPH ACCESS HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def _get_current_graph():
    """
    Get the current product graph. Uses the server's cached catalog
    to avoid rebuilding on every curation API call.
    """
    from backend.product_graph import ProductGraph
    from backend.product_graph_store import get_graph_store

    store = get_graph_store()

    # Use the server's cached catalog (built at startup, cached 5 min)
    # Import here to avoid circular imports
    import backend.server as srv
    if srv._catalog_cache_json is not None:
        import json
        catalog = json.loads(srv._catalog_cache_json)
        products = catalog.get("products", [])
    else:
        # Fallback: build from scratch (first call before cache is ready)
        from backend.product_normalizer import build_catalog
        import os
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))
        data_dir = os.path.join(BASE_DIR, "frontend/public/data")
        catalog = build_catalog(data_dir)
        products = catalog.get("products", [])

    graph = ProductGraph.from_flat_products(products)
    graph = store.load_graph_overlay(graph)

    return graph, store


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/pending")
async def get_pending_relationships():
    """Get AI-discovered relationships that need human review (confidence 0.5-0.9)."""
    try:
        graph, store = _get_current_graph()
        pending = store.get_pending_relationships(graph)
        return {
            "pending": pending,
            "count": len(pending),
        }
    except Exception as e:
        logger.error(f"Failed to get pending relationships: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_curation_stats():
    """Get coverage metrics for the curation dashboard."""
    try:
        graph, store = _get_current_graph()
        stats = store.get_curation_stats(graph)
        return stats
    except Exception as e:
        logger.error(f"Failed to get curation stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/families")
async def list_families():
    """List all product families grouped by brand."""
    try:
        graph, _ = _get_current_graph()

        # Build brand → families mapping
        brand_groups: Dict[str, List[Dict[str, Any]]] = {}
        for fid, family in graph.families.items():
            members = graph.get_family_members(fid)
            family_data = {
                **family.model_dump(),
                "members": [
                    {"id": m.id, "name": m.name, "image_url": m.image_url,
                     "variant_key": m.variant.variant_key if m.variant else None}
                    for m in members
                ],
            }
            brand_key = family.brand.strip() or "Unknown"
            if brand_key not in brand_groups:
                brand_groups[brand_key] = []
            brand_groups[brand_key].append(family_data)

        # Sort brands alphabetically, families within each brand by name
        sorted_brands = []
        for brand_name in sorted(brand_groups.keys(), key=str.lower):
            families_list = sorted(brand_groups[brand_name],
                                   key=lambda f: f.get("family_name", "").lower())
            sorted_brands.append({
                "brand": brand_name,
                "family_count": len(families_list),
                "families": families_list,
            })

        # Also return flat list for backward compatibility
        all_families = []
        for bg in sorted_brands:
            all_families.extend(bg["families"])

        return {
            "brands": sorted_brands,
            "families": all_families,
            "count": len(all_families),
        }
    except Exception as e:
        logger.error(f"Failed to list families: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/relationships/{product_id}")
async def get_product_relationships(product_id: str):
    """Get all relationships for a specific product."""
    try:
        graph, _ = _get_current_graph()
        if product_id not in graph.products:
            raise HTTPException(
                status_code=404, detail=f"Product '{product_id}' not found")

        rels = graph.get_relationships_for(product_id)
        product = graph.products[product_id]

        # Enrich relationship data with product names
        enriched = []
        for rel in rels:
            source = graph.products.get(rel.source_id)
            target = graph.products.get(rel.target_id)
            enriched.append({
                **rel.model_dump(),
                "source_name": source.name if source else "Unknown",
                "target_name": target.name if target else "Unknown",
                "source_image": source.image_url if source else "",
                "target_image": target.image_url if target else "",
            })

        # Get family info
        family_info = None
        if product.family_id and product.family_id in graph.families:
            family = graph.families[product.family_id]
            variants = graph.get_variants(product_id)
            family_info = {
                **family.model_dump(),
                "variants": [
                    {"id": v.id, "name": v.name, "image_url": v.image_url,
                     "variant_key": v.variant.variant_key if v.variant else None}
                    for v in variants
                ],
            }

        accessories = graph.get_accessories(product_id)
        compatible = graph.get_compatible(product_id)

        return {
            "product_id": product_id,
            "product_name": product.name,
            "family": family_info,
            "relationships": enriched,
            "accessories": [
                {"id": a.id, "name": a.name, "image_url": a.image_url,
                 "price": a.price}
                for a in accessories
            ],
            "compatible": [
                {"id": c.id, "name": c.name, "image_url": c.image_url,
                 "brand": c.brand}
                for c in compatible
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get relationships for {product_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/relationships")
async def create_relationship(req: CreateRelationshipRequest):
    """Create or confirm a relationship manually."""
    try:
        from backend.product_graph import RelationshipType

        graph, store = _get_current_graph()

        if req.source_id not in graph.products:
            raise HTTPException(
                status_code=404, detail=f"Source product '{req.source_id}' not found")
        if req.target_id not in graph.products:
            raise HTTPException(
                status_code=404, detail=f"Target product '{req.target_id}' not found")

        try:
            rel_type = RelationshipType(req.relationship_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid relationship type '{req.relationship_type}'. "
                       f"Valid: {[t.value for t in RelationshipType]}"
            )

        # Try to confirm existing AI relationship first
        confirmed = store.confirm_relationship(
            graph, req.source_id, req.target_id, rel_type)
        if confirmed:
            return {"status": "confirmed", "message": "AI-discovered relationship confirmed"}

        # Create new curated relationship
        rel = store.add_curated_relationship(
            graph, req.source_id, req.target_id, rel_type, req.notes
        )
        return {"status": "created", "relationship": rel.model_dump()}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create relationship: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/relationships")
async def delete_relationship(source_id: str, target_id: str, relationship_type: str):
    """Reject and remove a relationship."""
    try:
        from backend.product_graph import RelationshipType

        graph, store = _get_current_graph()

        try:
            rel_type = RelationshipType(relationship_type)
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Invalid type: {relationship_type}")

        removed = store.reject_relationship(
            graph, source_id, target_id, rel_type)
        if not removed:
            raise HTTPException(
                status_code=404, detail="Relationship not found")

        return {"status": "removed"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete relationship: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/families")
async def create_family(req: CreateFamilyRequest):
    """Create a product family manually."""
    try:
        from backend.product_graph import ProductFamily
        import re

        graph, store = _get_current_graph()

        # Validate product IDs
        valid_ids = [pid for pid in req.product_ids if pid in graph.products]
        if not valid_ids:
            raise HTTPException(
                status_code=400, detail="No valid product IDs provided")

        family_id = f"{req.brand.lower()}-{re.sub(r'[^a-z0-9]+', '-', req.family_name.lower())}"

        family = ProductFamily(
            id=family_id,
            brand=req.brand,
            family_name=req.family_name,
            series=req.series,
            generation=req.generation,
            variant_ids=valid_ids,
        )

        graph.add_family(family)

        # Tag products with family
        for pid in valid_ids:
            if pid in graph.products:
                graph.products[pid].family_id = family_id

        store.export_json_snapshot(graph)

        return {
            "status": "created",
            "family": family.model_dump(),
            "member_count": len(valid_ids),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create family: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/families/{family_id}/merge")
async def merge_families(family_id: str, req: MergeFamiliesRequest):
    """Merge two families into one (keeps target, absorbs source)."""
    try:
        graph, store = _get_current_graph()

        source_fam = graph.families.get(req.source_family_id)
        target_fam = graph.families.get(req.target_family_id)

        if not source_fam:
            raise HTTPException(
                status_code=404, detail=f"Source family '{req.source_family_id}' not found")
        if not target_fam:
            raise HTTPException(
                status_code=404, detail=f"Target family '{req.target_family_id}' not found")

        # Move all variants from source to target
        for vid in source_fam.variant_ids:
            if vid not in target_fam.variant_ids:
                target_fam.variant_ids.append(vid)
            if vid in graph.products:
                graph.products[vid].family_id = req.target_family_id

        # Move accessories
        for aid in source_fam.accessory_ids:
            if aid not in target_fam.accessory_ids:
                target_fam.accessory_ids.append(aid)

        # Remove source family
        del graph.families[req.source_family_id]
        store.export_json_snapshot(graph)

        return {
            "status": "merged",
            "target_family": target_fam.model_dump(),
            "absorbed_from": req.source_family_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to merge families: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/graph/overview")
async def get_graph_overview():
    """Get a high-level overview of the entire product graph."""
    try:
        graph, store = _get_current_graph()
        stats = graph.get_graph_stats()

        # Brand breakdown
        brand_families: Dict[str, int] = {}
        for fam in graph.families.values():
            b = fam.brand.lower()
            brand_families[b] = brand_families.get(b, 0) + 1

        return {
            **stats,
            "total_products": len(graph.products),
            "brand_family_counts": brand_families,
            "graph_enabled": True,
        }
    except Exception as e:
        logger.error(f"Failed to get graph overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))
