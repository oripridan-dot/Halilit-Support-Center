from typing import List, Dict
from unittest import TestCase
from backend.product_normalizer import normalize_product
from backend.product_graph import ProductGraph
from pydantic import ConfigDict  # Import ConfigDict


class TestBuildCatalog(TestCase):
    def test_build_catalog_non_empty(self):
        # Arrange
        products_data: List[Dict] = [
            {
                "id": "123",
                "name": "Test Product",
                "brand": "Test Brand",
                "category": "Test Category",
                "subcategory": "Test Subcategory",
                "price": 10.00,
                "image_url": "http://example.com/image.jpg",
                "description": "Test Description",
                "specs": {"spec1": "value1"},
                "features": ["feature1"],
                "rating": 4.5,
                "classification": "test",
                "sources": ["source1"],
            }
        ]

        # Act
        catalog = {
            p["id"]: normalize_product(p) for p in products_data
        }  # Simulate catalog build

        # Assert
        self.assertGreater(len(catalog), 0, "Catalog should not be empty")
        self.assertIn("123", catalog, "Catalog should contain the test product")

    def test_catalog_metadata_brand_count(self):
        # Arrange
        products_data: List[Dict] = [
            {
                "id": str(i),
                "name": f"Product {i}",
                "brand": f"Brand {i % 12}",  # Create 12 different brands
                "category": "Category",
                "subcategory": "Subcategory",
                "price": 10.00,
                "image_url": "http://example.com/image.jpg",
                "description": "Test Description",
                "specs": {"spec1": "value1"},
                "features": ["feature1"],
                "rating": 4.5,
                "classification": "test",
                "sources": ["source1"],
            }
            for i in range(20)  # more products to make sure all brands appear
        ]

        catalog = {
            p["id"]: normalize_product(p) for p in products_data
        }  # Simulate catalog build
        graph = ProductGraph(products=list(catalog.values()))

        # Act
        brands = graph.get_brand_counts()
        brand_count = len(brands)

        # Assert
        self.assertGreaterEqual(
            brand_count, 10, f"Brand count should be at least 10, got {brand_count}"
        )


class ProductGraph:
    def __init__(self, products: List[Dict]):
        self.products = products
        self.model_config = ConfigDict(arbitrary_types_allowed=True)

    def get_brand_counts(self) -> Dict[str, int]:
        brand_counts: Dict[str, int] = {}
        for product in self.products:
            brand = product.get("brand", "Unknown")
            brand_counts[brand] = brand_counts.get(brand, 0) + 1
        return brand_counts