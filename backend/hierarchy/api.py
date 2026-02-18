"""
API endpoints for hierarchy-based product structure
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/hierarchy", tags=["hierarchy"])


@router.get("/items")
async def get_hierarchy_items():
    """
    Get products organized by the new hierarchy structure:
    Category → Sub Category → Product Type → Brand → Family → Model → Variants
    
    Returns same structure as /api/structured-items but uses hierarchy tables.
    Falls back to structured_items if hierarchy tables are empty.
    """
    try:
        import psycopg2
        from urllib.parse import urlparse
        import os
        
        database_url = os.getenv(
            "DATABASE_URL",
            "postgresql://halilit_user:secure_password_change_me@localhost:5432/halilit_tasks"
        )
        
        parsed = urlparse(database_url)
        conn = psycopg2.connect(
            host=parsed.hostname or "localhost",
            port=parsed.port or 5432,
            database=parsed.path.lstrip("/"),
            user=parsed.username,
            password=parsed.password
        )
        
        cur = conn.cursor()
        
        # Check if hierarchy tables have data
        cur.execute("SELECT COUNT(*) FROM categories")
        category_count = cur.fetchone()[0]
        
        if category_count == 0:
            # Fallback to old structured_items
            logger.info("Hierarchy tables empty, falling back to structured_items")
            cur.close()
            conn.close()
            from backend.server import get_structured_items
            return await get_structured_items()
        
        # Build hierarchy structure from database
        result = {
            "_hierarchy": ["brand", "category", "subcategory", "product_type", "family", "model", "variants"],
            "brands": [],
            "products_by_id": {}
        }
        
        # Get all brands with their categories
        cur.execute("""
            SELECT DISTINCT b.id, b.name, b.slug
            FROM brands b
            ORDER BY b.name
        """)
        
        brands_data = cur.fetchall()
        
        for brand_id, brand_name, brand_slug in brands_data:
            brand_item = {
                "brand": brand_name,
                "brand_key": brand_slug or brand_id,
                "categories": []
            }
            
            # Get categories for this brand
            cur.execute("""
                SELECT DISTINCT c.id, c.name
                FROM categories c
                JOIN products p ON p.category_id = c.id
                WHERE p.brand_id = %s
                ORDER BY c.display_order, c.name
            """, (brand_id,))
            
            categories_data = cur.fetchall()
            
            for cat_id, cat_name in categories_data:
                category_item = {
                    "galaxy_id": cat_id,
                    "galaxy_label": cat_name,
                    "spectrum_id": cat_id,
                    "spectrum_label": cat_name,
                    "relations": []
                }
                
                # Get product families for this brand + category
                cur.execute("""
                    SELECT DISTINCT pf.id, pf.family_name
                    FROM product_families pf
                    JOIN products p ON p.family_id = pf.id
                    WHERE p.brand_id = %s AND p.category_id = %s
                    ORDER BY pf.family_name
                """, (brand_id, cat_id))
                
                families_data = cur.fetchall()
                
                for family_id, family_name in families_data:
                    # Get variants (products) for this family
                    cur.execute("""
                        SELECT p.id, p.name, p.product_data
                        FROM products p
                        WHERE p.family_id = %s
                        ORDER BY p.name
                    """, (family_id,))
                    
                    variants_data = cur.fetchall()
                    variant_ids = []
                    
                    for prod_id, prod_name, product_data in variants_data:
                        variant_ids.append(prod_id)
                        pd = product_data or {}
                        result["products_by_id"][prod_id] = {
                            "id": prod_id,
                            "name": prod_name,
                            "image_url": pd.get("image_url"),
                            "price": pd.get("price"),
                            "brand": pd.get("brand") or brand_name
                        }
                    
                    # Get accessories and related products
                    cur.execute("""
                        SELECT DISTINCT target_product_id
                        FROM product_relationships
                        WHERE source_product_id IN %s
                        AND relationship_type = 'accessory_for'
                    """, (tuple(variant_ids[:10]),) if variant_ids else ((),))
                    
                    accessory_ids = [row[0] for row in cur.fetchall()]
                    
                    cur.execute("""
                        SELECT DISTINCT target_product_id
                        FROM product_relationships
                        WHERE source_product_id IN %s
                        AND relationship_type IN ('related_to', 'alternative_to')
                    """, (tuple(variant_ids[:10]),) if variant_ids else ((),))
                    
                    related_ids = [row[0] for row in cur.fetchall()]
                    
                    relation_item = {
                        "series_key": family_id,
                        "series_label": family_name,
                        "families": [{
                            "family_id": family_id,
                            "family_name": family_name,
                            "hero_image": (variants_data[0][2] or {}).get("image_url") if variants_data else None,
                            "variant_count": len(variant_ids),
                            "variants": [
                                {
                                    "id": vid,
                                    "name": result["products_by_id"][vid]["name"],
                                    "image_url": result["products_by_id"][vid]["image_url"],
                                    "price": result["products_by_id"][vid]["price"]
                                }
                                for vid in variant_ids[:5]
                            ]
                        }],
                        "variant_ids": variant_ids,
                        "direct_accessory_ids": accessory_ids,
                        "related_ids": related_ids
                    }
                    
                    category_item["relations"].append(relation_item)
                
                if category_item["relations"]:
                    brand_item["categories"].append(category_item)
            
            if brand_item["categories"]:
                result["brands"].append(brand_item)
        
        cur.close()
        conn.close()
        
        return result
        
    except ImportError:
        logger.warning("psycopg2 not available, falling back to structured_items")
        from backend.server import get_structured_items
        return await get_structured_items()
    except Exception as e:
        logger.error(f"Error building hierarchy items: {e}")
        # Fallback to old structured_items
        from backend.server import get_structured_items
        return await get_structured_items()
