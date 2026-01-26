"""
🤖 AI-Enhanced Scraping Pipeline
=================================

This module provides AI-powered data validation and enrichment for the scraping pipeline.
It transforms the scraping process from a brittle manual operation into a self-healing,
high-confidence data checkpoint system.

Usage:
    from services.ai_pipeline import AIPipeline
    
    pipeline = AIPipeline()
    validated_catalog = await pipeline.validate_and_enrich("roland")
"""

import json
import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)


class ValidationStatus(Enum):
    """Status of data validation"""
    VALID = "valid"
    WARNING = "warning"  # Fixable issues
    ERROR = "error"      # Blocking issues
    SKIPPED = "skipped"  # Not enough data to validate


@dataclass
class ValidationIssue:
    """A single validation issue"""
    field: str
    product_id: str
    severity: ValidationStatus
    message: str
    suggested_fix: Optional[str] = None


@dataclass
class ValidationReport:
    """Complete validation report for a catalog"""
    brand: str
    total_products: int
    valid_count: int
    warning_count: int
    error_count: int
    issues: List[ValidationIssue]
    
    @property
    def is_production_ready(self) -> bool:
        """Can this catalog be deployed to production?"""
        return self.error_count == 0


class DataCheckpoint:
    """
    AI-powered data validation checkpoint.
    
    Runs before deploying to production to ensure data quality.
    """
    
    def __init__(self, images_dir: Path, catalogs_dir: Path):
        self.images_dir = images_dir
        self.catalogs_dir = catalogs_dir
    
    def validate_catalog(self, catalog_path: Path) -> ValidationReport:
        """
        Comprehensive catalog validation.
        
        Checks:
        1. ✅ All products have valid image paths
        2. ✅ All referenced images exist on disk
        3. ✅ Categories match known taxonomy
        4. ✅ Prices are within expected ranges
        5. ✅ No duplicate products
        6. ✅ Brand identity is complete
        """
        issues = []
        
        with open(catalog_path, 'r', encoding='utf-8') as f:
            catalog = json.load(f)
        
        brand = catalog.get('brand_name', catalog_path.stem)
        brand_slug = brand.lower().replace(' ', '-')
        products = catalog.get('products', [])
        
        # Track unique IDs to detect duplicates
        seen_ids = set()
        
        for product in products:
            product_id = product.get('id', 'unknown')
            
            # Check for duplicates
            if product_id in seen_ids:
                issues.append(ValidationIssue(
                    field='id',
                    product_id=product_id,
                    severity=ValidationStatus.ERROR,
                    message=f"Duplicate product ID: {product_id}",
                    suggested_fix="Remove duplicate or regenerate unique ID"
                ))
            seen_ids.add(product_id)
            
            # Validate image paths
            image_issues = self._validate_images(product, brand_slug)
            issues.extend(image_issues)
            
            # Validate category
            category_issues = self._validate_category(product)
            issues.extend(category_issues)
            
            # Validate pricing
            price_issues = self._validate_pricing(product)
            issues.extend(price_issues)
        
        # Validate brand identity
        brand_issues = self._validate_brand_identity(catalog)
        issues.extend(brand_issues)
        
        # Count by severity
        valid_count = sum(1 for p in products if not any(
            i.product_id == p.get('id') and i.severity == ValidationStatus.ERROR 
            for i in issues
        ))
        warning_count = sum(1 for i in issues if i.severity == ValidationStatus.WARNING)
        error_count = sum(1 for i in issues if i.severity == ValidationStatus.ERROR)
        
        return ValidationReport(
            brand=brand,
            total_products=len(products),
            valid_count=valid_count,
            warning_count=warning_count,
            error_count=error_count,
            issues=issues
        )
    
    def _validate_images(self, product: dict, brand_slug: str) -> List[ValidationIssue]:
        """Validate that product images exist on disk"""
        issues = []
        product_id = product.get('id', 'unknown')
        
        # Check main image
        image_url = product.get('image_url') or product.get('image')
        if not image_url:
            issues.append(ValidationIssue(
                field='image_url',
                product_id=product_id,
                severity=ValidationStatus.ERROR,
                message="No image URL defined",
                suggested_fix="Run VisualFactory to generate thumbnail"
            ))
        elif image_url.startswith('/data/'):
            # Local path - check if file exists
            relative_path = image_url.replace('/data/', '')
            full_path = self.images_dir.parent / relative_path
            
            if not full_path.exists():
                issues.append(ValidationIssue(
                    field='image_url',
                    product_id=product_id,
                    severity=ValidationStatus.ERROR,
                    message=f"Image file not found: {image_url}",
                    suggested_fix=f"Expected at: {full_path}"
                ))
        
        # Check images object
        images = product.get('images', {})
        if isinstance(images, dict):
            for key in ['thumbnail', 'main', 'high_res']:
                img_path = images.get(key)
                if img_path and img_path.startswith('/data/'):
                    relative_path = img_path.replace('/data/', '')
                    full_path = self.images_dir.parent / relative_path
                    
                    if not full_path.exists():
                        issues.append(ValidationIssue(
                            field=f'images.{key}',
                            product_id=product_id,
                            severity=ValidationStatus.WARNING if key != 'thumbnail' else ValidationStatus.ERROR,
                            message=f"Image file not found: {img_path}",
                            suggested_fix="Run VisualFactory to regenerate"
                        ))
        
        return issues
    
    def _validate_category(self, product: dict) -> List[ValidationIssue]:
        """Validate product category against OFFICIAL brand taxonomy"""
        issues = []
        product_id = product.get('id', 'unknown')
        brand = (product.get('brand') or '').lower()
        
        # Import the official taxonomy
        from models.brand_taxonomy import validate_category, get_all_brand_categories, normalize_category
        
        category = product.get('category') or product.get('main_category')
        if not category:
            issues.append(ValidationIssue(
                field='category',
                product_id=product_id,
                severity=ValidationStatus.WARNING,
                message="No category defined",
                suggested_fix="Set category based on product URL path or breadcrumbs"
            ))
        else:
            # Validate against the brand's official taxonomy
            if brand and not validate_category(brand, category):
                # Get all valid categories for this brand
                valid_categories = get_all_brand_categories(brand)
                
                # Try to normalize the category
                normalized = normalize_category(brand, category)
                
                if normalized:
                    issues.append(ValidationIssue(
                        field='category',
                        product_id=product_id,
                        severity=ValidationStatus.WARNING,
                        message=f"Category '{category}' should be '{normalized}' per {brand.upper()} taxonomy",
                        suggested_fix=f"Use official label: {normalized}"
                    ))
                else:
                    suggested = valid_categories[:5] if valid_categories else ["Accessories"]
                    issues.append(ValidationIssue(
                        field='category',
                        product_id=product_id,
                        severity=ValidationStatus.WARNING,
                        message=f"Category '{category}' not in {brand.upper()} official taxonomy",
                        suggested_fix=f"Valid categories: {', '.join(suggested)}"
                    ))
        
        return issues
    
    def _validate_pricing(self, product: dict) -> List[ValidationIssue]:
        """Validate pricing is reasonable"""
        issues = []
        product_id = product.get('id', 'unknown')
        
        # Get price from various possible locations
        price = None
        pricing = product.get('pricing', {})
        if isinstance(pricing, dict):
            price = pricing.get('regular_price') or pricing.get('price')
        if price is None:
            price = product.get('halilit_price') or product.get('price')
        
        if price is not None:
            try:
                price = float(price)
                
                # Sanity checks
                if price <= 0:
                    issues.append(ValidationIssue(
                        field='price',
                        product_id=product_id,
                        severity=ValidationStatus.ERROR,
                        message=f"Invalid price: {price}",
                        suggested_fix="Price must be positive"
                    ))
                elif price < 50:
                    issues.append(ValidationIssue(
                        field='price',
                        product_id=product_id,
                        severity=ValidationStatus.WARNING,
                        message=f"Suspiciously low price: ₪{price}",
                        suggested_fix="Verify price is correct (not missing zeros?)"
                    ))
                elif price > 100000:
                    issues.append(ValidationIssue(
                        field='price',
                        product_id=product_id,
                        severity=ValidationStatus.WARNING,
                        message=f"Very high price: ₪{price}",
                        suggested_fix="Verify this is correct for premium equipment"
                    ))
            except (ValueError, TypeError):
                issues.append(ValidationIssue(
                    field='price',
                    product_id=product_id,
                    severity=ValidationStatus.ERROR,
                    message=f"Invalid price format: {price}",
                    suggested_fix="Price must be a number"
                ))
        
        return issues
    
    def _validate_brand_identity(self, catalog: dict) -> List[ValidationIssue]:
        """Validate brand identity completeness"""
        issues = []
        
        brand_identity = catalog.get('brand_identity', {})
        brand_name = catalog.get('brand_name', 'Unknown')
        
        if not brand_identity.get('id'):
            issues.append(ValidationIssue(
                field='brand_identity.id',
                product_id='_brand',
                severity=ValidationStatus.ERROR,
                message="Brand identity missing 'id' field",
                suggested_fix="Add brand slug as id"
            ))
        
        if not brand_identity.get('logo_url'):
            issues.append(ValidationIssue(
                field='brand_identity.logo_url',
                product_id='_brand',
                severity=ValidationStatus.WARNING,
                message=f"No logo URL for {brand_name}",
                suggested_fix="Add logo to /assets/logos/"
            ))
        
        brand_colors = brand_identity.get('brand_colors', {})
        if not brand_colors.get('primary'):
            issues.append(ValidationIssue(
                field='brand_identity.brand_colors.primary',
                product_id='_brand',
                severity=ValidationStatus.WARNING,
                message="No primary brand color defined",
                suggested_fix="Add brand color to BRAND_THEMES in forge_backbone.py"
            ))
        
        return issues


class AIImageValidator:
    """
    AI-powered image validation.
    
    Future: Use vision models to validate product images.
    Current: Rule-based validation.
    """
    
    async def validate_image(self, image_path: Path, product_name: str) -> Tuple[bool, str]:
        """
        Validate that an image contains the expected product.
        
        Future implementation will use:
        - Vision LLM to describe image contents
        - Compare description to product name
        - Detect background quality
        - Measure image resolution and quality
        
        Returns:
            Tuple of (is_valid, reason)
        """
        # Current: Basic file validation
        if not image_path.exists():
            return False, "Image file does not exist"
        
        # Check file size
        size = image_path.stat().st_size
        if size < 1000:  # Less than 1KB
            return False, "Image file too small (possibly corrupt)"
        if size > 10_000_000:  # More than 10MB
            return False, "Image file too large (needs optimization)"
        
        # Check extension
        if not image_path.suffix.lower() in ['.webp', '.jpg', '.jpeg', '.png']:
            return False, f"Unsupported image format: {image_path.suffix}"
        
        # Future: Add vision model validation here
        # - Use Claude Vision or similar to describe image
        # - Match description to product_name
        # - Check for white/clean background
        
        return True, "Image passed basic validation"


class AIPipeline:
    """
    Main AI-enhanced pipeline for catalog validation and enrichment.
    
    Usage:
        pipeline = AIPipeline()
        report = pipeline.validate_catalog("roland")
        
        if report.is_production_ready:
            print("✅ Catalog ready for deployment")
        else:
            for issue in report.issues:
                print(f"❌ {issue.message}")
    """
    
    def __init__(self):
        self.frontend_data = Path("/workspaces/hsc-jit-v3/frontend/public/data")
        self.backend_data = Path("/workspaces/hsc-jit-v3/backend/data/catalogs_brand")
        
        self.checkpoint = DataCheckpoint(
            images_dir=self.frontend_data / "product_images",
            catalogs_dir=self.frontend_data
        )
        self.image_validator = AIImageValidator()
    
    def validate_catalog(self, brand_slug: str) -> ValidationReport:
        """Validate a specific brand catalog"""
        catalog_path = self.frontend_data / f"{brand_slug}.json"
        
        if not catalog_path.exists():
            return ValidationReport(
                brand=brand_slug,
                total_products=0,
                valid_count=0,
                warning_count=0,
                error_count=1,
                issues=[ValidationIssue(
                    field='catalog',
                    product_id='_catalog',
                    severity=ValidationStatus.ERROR,
                    message=f"Catalog file not found: {catalog_path}",
                    suggested_fix="Run forge_backbone.py to generate catalog"
                )]
            )
        
        return self.checkpoint.validate_catalog(catalog_path)
    
    def validate_all_catalogs(self) -> Dict[str, ValidationReport]:
        """Validate all brand catalogs"""
        reports = {}
        
        for catalog_file in self.frontend_data.glob("*.json"):
            if catalog_file.name in ['index.json', 'scrape_progress.json']:
                continue
            
            brand_slug = catalog_file.stem
            reports[brand_slug] = self.checkpoint.validate_catalog(catalog_file)
        
        return reports
    
    def print_report(self, report: ValidationReport):
        """Print a validation report in human-readable format"""
        status = "✅ READY" if report.is_production_ready else "❌ NOT READY"
        
        print(f"\n{'='*60}")
        print(f"📊 Validation Report: {report.brand}")
        print(f"{'='*60}")
        print(f"Status: {status}")
        print(f"Products: {report.total_products}")
        print(f"  ✅ Valid: {report.valid_count}")
        print(f"  ⚠️  Warnings: {report.warning_count}")
        print(f"  ❌ Errors: {report.error_count}")
        
        if report.issues:
            print(f"\n📋 Issues:")
            for issue in report.issues[:10]:  # Show first 10
                icon = "⚠️" if issue.severity == ValidationStatus.WARNING else "❌"
                print(f"  {icon} [{issue.product_id}] {issue.field}: {issue.message}")
                if issue.suggested_fix:
                    print(f"      → Fix: {issue.suggested_fix}")
            
            if len(report.issues) > 10:
                print(f"  ... and {len(report.issues) - 10} more issues")


# CLI Entry Point
if __name__ == "__main__":
    import sys
    
    pipeline = AIPipeline()
    
    if len(sys.argv) > 1:
        # Validate specific brand
        brand = sys.argv[1]
        report = pipeline.validate_catalog(brand)
        pipeline.print_report(report)
    else:
        # Validate all
        print("🔍 Validating all catalogs...")
        reports = pipeline.validate_all_catalogs()
        
        total_ready = sum(1 for r in reports.values() if r.is_production_ready)
        
        print(f"\n{'='*60}")
        print(f"📊 Overall Summary: {total_ready}/{len(reports)} catalogs ready")
        print(f"{'='*60}")
        
        for brand, report in reports.items():
            status = "✅" if report.is_production_ready else "❌"
            print(f"  {status} {brand}: {report.valid_count}/{report.total_products} products valid")
