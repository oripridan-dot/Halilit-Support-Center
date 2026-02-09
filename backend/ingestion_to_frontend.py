import json
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class FrontendAdapter:
    """
    Transforms internal backend data structures into the
    Galaxy Dashboard JSON format.
    """

    @staticmethod
    def transform_catalog(products: List[Dict]) -> Dict[str, Any]:
        """
        Groups products by Category -> Subcategory -> Brand.
        Returns the structure expected by GalaxyDashboard.tsx
        """
        galaxy_structure = {}

        for p in products:
            # Safely get fields with defaults
            cat = p.get('category', 'Uncategorized')
            sub = p.get('subcategory', 'General')
            brand = p.get('brand', 'Generic')

            # Initialize Hierarchy
            if cat not in galaxy_structure:
                galaxy_structure[cat] = {
                    "id": cat.lower().replace(" ", "-"),
                    "name": cat,
                    "subcategories": {},
                    "total_products": 0
                }

            # Initialize Subcategory
            if sub not in galaxy_structure[cat]["subcategories"]:
                galaxy_structure[cat]["subcategories"][sub] = {
                    "id": sub.lower().replace(" ", "-"),
                    "name": sub,
                    "brands": {},
                    "count": 0
                }

            # Initialize Brand track inside Subcategory
            sub_node = galaxy_structure[cat]["subcategories"][sub]
            if brand not in sub_node["brands"]:
                sub_node["brands"][brand] = {
                    "name": brand,
                    "products": []
                }

            # Add Product
            # Adapter v7.5: Map unified data model to frontend DTO
            # OfficialScout: Prefer official name if available per user request
            display_name = p.get('official_name') or p.get(
                'product_name') or p.get('name')
            brand_slug = brand.lower().replace(" ", "-") if brand else "generic"
            # Try to match common image extensions
            # In a real app we might check file existence, but for SPA we construct the path
            brand_logo_url = f"/assets/logos/{brand_slug}_logo.png"

            product_dto = {
                "id": p.get('id') or p.get('halilit_id'),
                "name": display_name,
                "brand": brand,
                "brand_logo": brand_logo_url,
                "image": p.get('image_url') or p.get('display', {}).get('hero_image', {}).get('url'),
                "price_ils": p.get('price') or p.get('price_il') or p.get('pricing', {}).get('price_il'),
                "competitor_price": p.get('pricing', {}).get('price_eur'),
                "gap": p.get('gap'),  # Likely computed elsewhere or None
                "status": p.get('status', 'pending'),
                # Mock risk score from quality
                "risk_score": p.get('quality_score', 1.0) * 100,
                "description": p.get('description_short') or "",
                # Pass full verification data
                "provenance": p.get('provenance', {}),
                "official_specs": p.get('specifications', {})
            }

            sub_node["brands"][brand]["products"].append(product_dto)
            sub_node["count"] += 1
            galaxy_structure[cat]["total_products"] += 1

        # Flatten for frontend array consumption if needed,
        # or return the tree. The Galaxy Dashboard usually expects an array of Categories.
        return list(galaxy_structure.values())


def get_frontend_data():
    # Helper to load from your unified service
    from backend.unified_data_service_v75 import unified_data_service
    raw_data = unified_data_service.get_all_products()
    return FrontendAdapter.transform_catalog(raw_data)
