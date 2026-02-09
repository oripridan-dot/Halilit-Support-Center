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
            product_dto = {
                "id": p.get('id') or p.get('halilit_sku'),
                "name": p.get('name'),
                "image": p.get('image_url'),
                "price_ils": p.get('price_ils'),
                "competitor_price": p.get('competitor_price_eur'),
                "gap": p.get('gap'),
                "status": p.get('status', 'pending')
            }

            sub_node["brands"][brand]["products"].append(product_dto)
            sub_node["count"] += 1
            galaxy_structure[cat]["total_products"] += 1

        # Flatten for frontend array consumption if needed,
        # or return the tree. The Galaxy Dashboard usually expects an array of Categories.
        return list(galaxy_structure.values())


def get_frontend_data():
    # Helper to load from your unified service
    from backend.unified_data_service_v73 import unified_data_service
    raw_data = unified_data_service.get_all_products()
    return FrontendAdapter.transform_catalog(raw_data)
