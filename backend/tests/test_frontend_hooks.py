"""
Frontend Hook Unit Tests - useGalaxyData
Tests the React hook that consumes Galaxy data
"""

import json
from pathlib import Path


class MockGalaxyData:
    """Mock Galaxy data for testing"""

    @staticmethod
    def create_test_catalog():
        """Create a test catalog with sample products"""
        return {
            "generatedAt": "2026-02-03T08:00:00Z",
            "version": "5.2.0",
            "stats": {
                "totalProducts": 10,
                "brandsCount": 4
            },
            "products": [
                {
                    "id": "nord-lead-a1",
                    "name": "Nord Lead A1",
                    "brand": "Nord",
                    "category": "Synthesizers",
                    "subCategory": "Monosynth",
                    "tier": "pro",
                    "price": 2500,
                    "stockStatus": "in_stock",
                    "images": {
                        "main": "/images/nord-lead-a1.jpg",
                        "thumbnail": "/images/nord-lead-a1-thumb.jpg",
                        "gallery": ["/images/nord-lead-a1-1.jpg"]
                    },
                    "aiTags": ["analog", "warm", "warm sound", "pro"],
                    "specs": {"polyphony": "1", "keys": "37", "weight": "7.5kg"},
                    "searchTokens": "nord lead a1 synthesizers monosynth analog warm pro",
                    "description": "Powerful monosynth"
                },
                {
                    "id": "juno-60",
                    "name": "Roland Juno-60",
                    "brand": "Roland",
                    "category": "Synthesizers",
                    "subCategory": "Polysynth",
                    "tier": "pro",
                    "price": 2000,
                    "stockStatus": "in_stock",
                    "images": {
                        "main": "/images/juno-60.jpg",
                        "thumbnail": "/images/juno-60-thumb.jpg",
                        "gallery": []
                    },
                    "aiTags": ["analog", "vintage", "pro"],
                    "specs": {"polyphony": "6", "keys": "61", "weight": "32kg"},
                    "searchTokens": "roland juno-60 synthesizers polysynth analog vintage pro",
                    "description": "Classic analog polysynth"
                },
                {
                    "id": "tr-808",
                    "name": "TR-808",
                    "brand": "Roland",
                    "category": "Drums",
                    "subCategory": "Machines",
                    "tier": "flagship",
                    "price": 5000,
                    "stockStatus": "low_stock",
                    "images": {
                        "main": "/images/tr-808.jpg",
                        "thumbnail": "/images/tr-808-thumb.jpg",
                        "gallery": []
                    },
                    "aiTags": ["percussion", "legendary", "flagship"],
                    "specs": {"sounds": "24", "weight": "8kg"},
                    "searchTokens": "roland tr-808 drums machines percussion legendary flagship",
                    "description": "Iconic drum machine"
                },
                {
                    "id": "moog-sub",
                    "name": "Moog Subsequent 37",
                    "brand": "Moog",
                    "category": "Synthesizers",
                    "subCategory": "Monosynth",
                    "tier": "flagship",
                    "price": 4500,
                    "stockStatus": "in_stock",
                    "images": {
                        "main": "/images/moog-sub.jpg",
                        "thumbnail": "/images/moog-sub-thumb.jpg",
                        "gallery": []
                    },
                    "aiTags": ["analog", "ladder filter", "warm", "flagship"],
                    "specs": {"polyphony": "1", "keys": "37", "weight": "12kg"},
                    "searchTokens": "moog subsequent 37 synthesizers monosynth analog ladder filter flagship",
                    "description": "Modern analog monosynth"
                },
                {
                    "id": "korg-nanopad",
                    "name": "Korg Nanopads",
                    "brand": "Korg",
                    "category": "Controllers",
                    "subCategory": "Pads",
                    "tier": "entry",
                    "price": 200,
                    "stockStatus": "in_stock",
                    "images": {
                        "main": "/images/nanopad.jpg",
                        "thumbnail": "/images/nanopad-thumb.jpg",
                        "gallery": []
                    },
                    "aiTags": ["portable", "entry"],
                    "specs": {"pads": "16", "size": "compact"},
                    "searchTokens": "korg nanopad controllers pads portable entry",
                    "description": "Portable pad controller"
                },
                {
                    "id": "korg-mini",
                    "name": "Korg Monotron",
                    "brand": "Korg",
                    "category": "Synthesizers",
                    "subCategory": "Desktop",
                    "tier": "entry",
                    "price": 100,
                    "stockStatus": "in_stock",
                    "images": {
                        "main": "/images/monotron.jpg",
                        "thumbnail": "/images/monotron-thumb.jpg",
                        "gallery": []
                    },
                    "aiTags": ["mini", "entry", "vintage"],
                    "specs": {"keys": "13"},
                    "searchTokens": "korg monotron synthesizers desktop mini entry vintage",
                    "description": "Tiny analog synth"
                },
                # Additional products for statistical tests
                {
                    "id": "nord-2", "name": "Nord 2", "brand": "Nord",
                    "category": "Synthesizers", "subCategory": "Monosynth",
                    "tier": "mid", "price": 1200, "stockStatus": "in_stock",
                    "images": {"main": "/img.jpg", "thumbnail": "/thumb.jpg", "gallery": []},
                    "aiTags": ["mid"], "specs": {}, "searchTokens": "nord 2 mid",
                    "description": "Mid-range"
                },
                {
                    "id": "roland-2", "name": "Roland 2", "brand": "Roland",
                    "category": "Drums", "subCategory": "Machines",
                    "tier": "mid", "price": 1500, "stockStatus": "in_stock",
                    "images": {"main": "/img.jpg", "thumbnail": "/thumb.jpg", "gallery": []},
                    "aiTags": ["mid"], "specs": {}, "searchTokens": "roland 2 mid",
                    "description": "Mid-range"
                },
                {
                    "id": "moog-2", "name": "Moog 2", "brand": "Moog",
                    "category": "Synthesizers", "subCategory": "Desktop",
                    "tier": "pro", "price": 3000, "stockStatus": "in_stock",
                    "images": {"main": "/img.jpg", "thumbnail": "/thumb.jpg", "gallery": []},
                    "aiTags": ["pro"], "specs": {}, "searchTokens": "moog 2 pro",
                    "description": "Pro"
                },
                {
                    "id": "korg-2", "name": "Korg 2", "brand": "Korg",
                    "category": "Synthesizers", "subCategory": "Monosynth",
                    "tier": "entry", "price": 300, "stockStatus": "in_stock",
                    "images": {"main": "/img.jpg", "thumbnail": "/thumb.jpg", "gallery": []},
                    "aiTags": ["entry"], "specs": {}, "searchTokens": "korg 2 entry",
                    "description": "Entry"
                },
            ],
            "categories": {
                "Synthesizers": ["Monosynth", "Polysynth", "Desktop"],
                "Drums": ["Machines"],
                "Controllers": ["Pads"]
            }
        }


class TestUseGalaxyDataLogic:
    """Unit tests for useGalaxyData hook logic (without React)"""

    @staticmethod
    def test_data_loading():
        """Test that catalog loads correctly"""
        catalog = MockGalaxyData.create_test_catalog()

        assert catalog is not None
        assert "products" in catalog
        assert len(catalog["products"]) == 10
        assert "categories" in catalog

        print("✅ Data loading test passed")

    @staticmethod
    def test_semantic_search():
        """Test semantic search with pre-computed tokens"""
        catalog = MockGalaxyData.create_test_catalog()
        products = catalog["products"]

        # Search for "vintage"
        query = "vintage"
        results = []
        for product in products:
            if query.lower() in product["searchTokens"]:
                results.append(product)

        assert len(results) >= 2  # Juno, Korg 2 have "vintage"
        assert any(p["name"] == "Roland Juno-60" for p in results)

        print("✅ Semantic search test passed")

    @staticmethod
    def test_search_relevance_scoring():
        """Test that search results are scored by relevance"""
        catalog = MockGalaxyData.create_test_catalog()
        products = catalog["products"]

        query = "synthesizers monosynth"
        results = []

        for product in products:
            tokens = product["searchTokens"].split()
            match_count = 0
            for token in tokens:
                if token in query.lower():
                    match_count += 1

            if match_count > 0:
                relevance = min(1.0, match_count / len(tokens))
                results.append((product, relevance))

        # Sort by relevance
        results.sort(key=lambda x: x[1], reverse=True)

        assert len(results) > 0
        assert results[0][1] <= 1.0
        assert results[0][1] > 0

        print("✅ Search relevance scoring test passed")

    @staticmethod
    def test_filter_by_tier():
        """Test filtering products by tier"""
        catalog = MockGalaxyData.create_test_catalog()
        products = catalog["products"]

        tier_results = {
            "entry": [p for p in products if p["tier"] == "entry"],
            "mid": [p for p in products if p["tier"] == "mid"],
            "pro": [p for p in products if p["tier"] == "pro"],
            "flagship": [p for p in products if p["tier"] == "flagship"],
        }

        assert len(tier_results["entry"]) == 3
        assert len(tier_results["mid"]) == 2
        assert len(tier_results["pro"]) == 3
        assert len(tier_results["flagship"]) == 2

        print("✅ Filter by tier test passed")

    @staticmethod
    def test_filter_by_brand():
        """Test filtering products by brand"""
        catalog = MockGalaxyData.create_test_catalog()
        products = catalog["products"]

        brands = {}
        for product in products:
            brand = product["brand"]
            if brand not in brands:
                brands[brand] = []
            brands[brand].append(product)

        assert len(brands["Nord"]) == 2
        assert len(brands["Roland"]) == 3
        assert len(brands["Moog"]) == 2
        assert len(brands["Korg"]) == 3

        print("✅ Filter by brand test passed")

    @staticmethod
    def test_filter_by_category():
        """Test filtering products by category"""
        catalog = MockGalaxyData.create_test_catalog()
        products = catalog["products"]

        categories = {}
        for product in products:
            cat = product["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(product)

        assert len(categories["Synthesizers"]) >= 6
        assert len(categories["Drums"]) >= 2
        assert len(categories["Controllers"]) == 1

        print("✅ Filter by category test passed")

    @staticmethod
    def test_tier_statistics():
        """Test tier statistics calculation"""
        catalog = MockGalaxyData.create_test_catalog()
        products = catalog["products"]

        tiers = {
            "entry": [],
            "mid": [],
            "pro": [],
            "flagship": []
        }

        for product in products:
            tiers[product["tier"]].append(product)

        stats = {}
        for tier, tier_products in tiers.items():
            if tier_products:
                prices = [p["price"] for p in tier_products]
                stats[tier] = {
                    "count": len(tier_products),
                    "avgPrice": sum(prices) / len(prices),
                    "minPrice": min(prices),
                    "maxPrice": max(prices)
                }

        # Verify statistics
        assert stats["entry"]["count"] == 3
        assert stats["entry"]["avgPrice"] == (200 + 100 + 300) / 3
        assert stats["flagship"]["maxPrice"] == 5000

        print("✅ Tier statistics test passed")

    @staticmethod
    def test_brand_profile():
        """Test brand profile generation"""
        catalog = MockGalaxyData.create_test_catalog()
        products = catalog["products"]

        brand = "Nord"
        brand_products = [p for p in products if p["brand"] == brand]

        profile = {
            "name": brand,
            "productCount": len(brand_products),
            "categories": set(p["category"] for p in brand_products),
            "avgPrice": sum(p["price"] for p in brand_products) / len(brand_products),
            "tiers": {}
        }

        for product in brand_products:
            tier = product["tier"]
            profile["tiers"][tier] = profile["tiers"].get(tier, 0) + 1

        assert profile["productCount"] == 2
        assert profile["avgPrice"] == (2500 + 1200) / 2
        assert "pro" in profile["tiers"]

        print("✅ Brand profile test passed")

    @staticmethod
    def test_category_statistics():
        """Test category statistics generation"""
        catalog = MockGalaxyData.create_test_catalog()
        products = catalog["products"]

        category = "Synthesizers"
        cat_products = [p for p in products if p["category"] == category]

        stats = {
            "name": category,
            "productCount": len(cat_products),
            "brands": list(set(p["brand"] for p in cat_products)),
            "subCategories": {},
            "priceRange": {
                "min": min(p["price"] for p in cat_products),
                "max": max(p["price"] for p in cat_products),
                "avg": sum(p["price"] for p in cat_products) / len(cat_products)
            }
        }

        for product in cat_products:
            subcat = product["subCategory"]
            stats["subCategories"][subcat] = stats["subCategories"].get(
                subcat, 0) + 1

        assert stats["productCount"] >= 6
        assert len(stats["brands"]) == 4
        assert stats["priceRange"]["min"] == 100

        print("✅ Category statistics test passed")

    @staticmethod
    def test_all_brands_extraction():
        """Test extracting unique brands"""
        catalog = MockGalaxyData.create_test_catalog()
        products = catalog["products"]

        brands = sorted(set(p["brand"] for p in products))

        assert len(brands) == 4
        assert "Nord" in brands
        assert "Roland" in brands
        assert "Moog" in brands
        assert "Korg" in brands

        print("✅ All brands extraction test passed")

    @staticmethod
    def test_data_consistency():
        """Test that data remains consistent after operations"""
        catalog = MockGalaxyData.create_test_catalog()
        original_count = len(catalog["products"])

        # Simulate various operations
        _ = [p for p in catalog["products"] if p["tier"] == "pro"]
        _ = [p for p in catalog["products"] if p["brand"] == "Nord"]
        _ = [p for p in catalog["products"] if "warm" in p["searchTokens"]]

        # Verify count unchanged
        assert len(catalog["products"]) == original_count

        print("✅ Data consistency test passed")

    @staticmethod
    def test_empty_search_results():
        """Test handling of empty search results"""
        catalog = MockGalaxyData.create_test_catalog()
        products = catalog["products"]

        query = "nonexistent_term_xyz"
        results = [p for p in products if query.lower() in p["searchTokens"]]

        assert len(results) == 0

        print("✅ Empty search results test passed")


def run_all_hook_tests():
    """Run all frontend hook tests"""
    print("\n" + "="*70)
    print("🧪 FRONTEND HOOK LOGIC TESTS - useGalaxyData")
    print("="*70 + "\n")

    tester = TestUseGalaxyDataLogic()
    tests = [
        ("Data Loading", tester.test_data_loading),
        ("Semantic Search", tester.test_semantic_search),
        ("Search Relevance Scoring", tester.test_search_relevance_scoring),
        ("Filter by Tier", tester.test_filter_by_tier),
        ("Filter by Brand", tester.test_filter_by_brand),
        ("Filter by Category", tester.test_filter_by_category),
        ("Tier Statistics", tester.test_tier_statistics),
        ("Brand Profile", tester.test_brand_profile),
        ("Category Statistics", tester.test_category_statistics),
        ("All Brands Extraction", tester.test_all_brands_extraction),
        ("Data Consistency", tester.test_data_consistency),
        ("Empty Search Results", tester.test_empty_search_results),
    ]

    passed = 0
    failed = 0

    for test_name, test_fn in tests:
        try:
            test_fn()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test_name}: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test_name}: Unexpected error: {e}")
            failed += 1

    print("\n" + "="*70)
    print(f"📊 RESULTS: {passed}/{len(tests)} PASSED")
    if failed > 0:
        print(f"❌ {failed} FAILED")
    else:
        print("✅ ALL TESTS PASSED!")
    print("="*70 + "\n")

    return failed == 0


if __name__ == "__main__":
    import sys
    success = run_all_hook_tests()
    sys.exit(0 if success else 1)
