#!/usr/bin/env python3
"""
Data Migration Script - Process Existing Products to New Hierarchy

This script:
1. Loads all existing products
2. Extracts hierarchy information
3. Creates families, models, and variants
4. Migrates products to new structure
5. Validates the migration

IMPORTANT: Run this script with your virtual environment activated:
    source .venv/bin/activate
    python3 run-data-migration.py
"""

import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import defaultdict

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Check for pydantic early
try:
    import pydantic
except ImportError:
    print("❌ ERROR: pydantic not found!")
    print("")
    print("💡 SOLUTION: Activate your virtual environment first:")
    print("   source .venv/bin/activate")
    print("   python3 run-data-migration.py")
    print("")
    print("   OR run: ./install-deps.sh")
    sys.exit(1)

from backend.hierarchy.migration_helper import HierarchyMigrationHelper
from backend.hierarchy.service import get_hierarchy_service
from backend.hierarchy.models import Category, SubCategory, ProductType, Brand, ProductFamily, ProductModel, Product
from backend.ingestion.ingestion_database import get_ingestion_database

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DataMigration")


def extract_family_from_name(name: str, brand: str) -> tuple[str, Optional[int], Optional[str]]:
    """
    Extract family, model number, and variant from product name.
    
    Examples:
        "Nord Stage 4 88" -> ("Stage", 4, "88")
        "Nord Piano 5" -> ("Piano", 5, None)
        "Roland Fantom 08" -> ("Fantom", None, "08")
    """
    name_lower = name.lower()
    brand_lower = brand.lower()
    
    # Remove brand name
    without_brand = name_lower.replace(brand_lower, "").strip()
    
    # Try to find model number pattern: "Stage 4", "Piano 5", etc.
    import re
    match = re.match(r'^([a-z]+)\s+(\d+)(?:\s+(.+))?$', without_brand)
    if match:
        family_name = match.group(1).capitalize()
        model_number = int(match.group(2))
        variant = match.group(3) if match.group(3) else None
        return family_name, model_number, variant
    
    # Try variant-only pattern: "Stage 88", "Piano Compact"
    match = re.match(r'^([a-z]+)(?:\s+(.+))?$', without_brand)
    if match:
        family_name = match.group(1).capitalize()
        variant = match.group(2) if match.group(2) else None
        return family_name, None, variant
    
    return "", None, None


def load_all_products() -> List[Dict[str, Any]]:
    """Load all products from the database or JSON files, deduplicated by ID"""
    all_products = []
    unique_products = {}  # Deduplicate by ID
    
    # Try unified_data_service first (best source)
    try:
        from backend.unified_data_service import ConductorDataService
        service = ConductorDataService()
        products = service.get_all_products()
        if products:
            for p in products:
                pid = p.get("id") or p.get("halilit_id") or ""
                if pid and pid not in unique_products:
                    unique_products[pid] = p
            logger.info(f"✅ Loaded {len(products)} products from unified_data_service ({len(unique_products)} unique)")
            all_products = list(unique_products.values())
            return all_products
    except Exception as e:
        logger.warning(f"Failed to load from unified_data_service: {e}")
    
    # Try ingestion database
    try:
        db = get_ingestion_database()
        products_by_brand = db.get_all_approved_products()
        
        for brand, products in products_by_brand.items():
            for p in products:
                pid = p.get("id") or p.get("halilit_id") or ""
                if pid and pid not in unique_products:
                    unique_products[pid] = p
        
        if unique_products:
            logger.info(f"✅ Loaded {len(unique_products)} unique products from ingestion database")
            all_products = list(unique_products.values())
            return all_products
    except Exception as e:
        logger.warning(f"Failed to load from database: {e}")
    
    # Fallback: try loading from frontend data files
    frontend_data_dir = Path("frontend/public/data")
    if frontend_data_dir.exists():
        logger.info(f"📂 Loading from frontend/public/data...")
        total_items = 0
        for json_file in sorted(frontend_data_dir.glob("*.json")):
            if json_file.name == "index.json" or json_file.name.startswith("search_"):
                continue
            try:
                with open(json_file, encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        products = data
                    elif isinstance(data, dict) and "products" in data:
                        products = data["products"]
                    else:
                        continue
                    
                    total_items += len(products)
                    for p in products:
                        pid = p.get("id") or p.get("halilit_id") or ""
                        if pid and pid not in unique_products:
                            unique_products[pid] = p
            except Exception as e:
                logger.warning(f"Failed to load {json_file.name}: {e}")
        
        if unique_products:
            logger.info(f"✅ Loaded {total_items} items from JSON files, {len(unique_products)} unique products")
            all_products = list(unique_products.values())
            return all_products
    
    logger.error("❌ No products found in any source!")
    return []


def create_hierarchy_structure(products: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Create the hierarchy structure from existing products.
    
    Returns:
        {
            "categories": [...],
            "sub_categories": [...],
            "product_types": [...],
            "brands": [...],
            "families": [...],
            "models": [...]
        }
    """
    logger.info("🔍 Analyzing products to create hierarchy structure...")
    
    helper = HierarchyMigrationHelper()
    
    # Extract categories
    categories_data = helper.extract_categories_from_existing_products(products)
    logger.info(f"Found {len(categories_data)} categories")
    
    # Classify products
    classifications = helper.classify_all_products(products)
    logger.info(f"Classified {len(classifications)} products")
    
    # Group by hierarchy
    groups = helper.group_products_by_hierarchy(products, classifications)
    logger.info(f"Created {len(groups)} hierarchy groups")
    
    # Extract unique values
    categories = set()
    sub_categories = set()
    product_types = set()
    brands = set()
    families = defaultdict(set)  # brand -> {family_names}
    models = defaultdict(lambda: defaultdict(set))  # brand -> family -> {model_numbers}
    
    for product in products:
        product_id = product.get("id") or product.get("halilit_id", "")
        classification = classifications.get(product_id, {})
        
        if classification.get("category"):
            categories.add(classification["category"])
        if classification.get("sub_category"):
            sub_categories.add(classification["sub_category"])
        if classification.get("product_type"):
            product_types.add(classification["product_type"])
        
        brand = product.get("brand", "")
        if brand:
            brands.add(brand)
            
            # Extract family/model from name
            product_name = product.get("product_name") or product.get("name", "")
            family_name, model_number, variant_key = extract_family_from_name(product_name, brand)
            
            if family_name:
                families[brand].add(family_name)
                if model_number:
                    models[brand][family_name].add(model_number)
    
    return {
        "categories": sorted(list(categories)),
        "sub_categories": sorted(list(sub_categories)),
        "product_types": sorted(list(product_types)),
        "brands": sorted(list(brands)),
        "families": dict(families),
        "models": {brand: dict(families) for brand, families in models.items()},
        "classifications": classifications,
        "groups": groups,
    }


def main():
    """Main migration function"""
    logger.info("🚀 Starting data migration to new hierarchy structure...")
    
    # Step 1: Load products
    products = load_all_products()
    if not products:
        logger.error("❌ No products found! Cannot proceed with migration.")
        return
    
    logger.info(f"✅ Loaded {len(products)} products")
    
    # Step 2: Create hierarchy structure
    hierarchy_data = create_hierarchy_structure(products)
    
    # Step 3: Generate migration report
    helper = HierarchyMigrationHelper()
    report_file = Path("migration_report.json")
    report = helper.generate_migration_report(products, report_file)
    
    logger.info("")
    logger.info("📊 Migration Report:")
    logger.info(f"   Total Products: {report['total_products']}")
    logger.info(f"   Categories Found: {report['categories_found']}")
    logger.info(f"   Subcategories Found: {report['subcategories_found']}")
    logger.info(f"   Product Types Needed: {report['product_types_needed']}")
    logger.info(f"   Products Classified: {report['products_classified']}")
    logger.info(f"   Classification Rate: {report['classification_rate']:.1%}")
    logger.info(f"   Hierarchy Groups: {report['hierarchy_groups']}")
    logger.info("")
    logger.info(f"📄 Full report saved to: {report_file}")
    logger.info("")
    logger.info("✅ Migration analysis complete!")
    logger.info("")
    logger.info("📝 Next steps:")
    logger.info("   1. Review migration_report.json")
    logger.info("   2. Run database migration: ./run-migration.sh")
    logger.info("   3. Populate hierarchy tables with the extracted data")
    logger.info("   4. Migrate products to new structure")


if __name__ == "__main__":
    main()
