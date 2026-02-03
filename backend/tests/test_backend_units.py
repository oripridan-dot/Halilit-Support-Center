"""
Backend Unit Tests - Galaxy Data Pipeline
Tests all backend components: refinery, data processing, validation
"""

from backend.pipeline.data_refinery import DataRefinery
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestDataRefinery:
    """Unit tests for DataRefinery class"""

    def test_brand_normalization(self):
        """Test that brands are properly normalized"""
        refinery = DataRefinery()

        test_cases = [
            ("Nord Keyboards", "Nord"),
            ("Roland Inc.", "Roland"),
            ("Yamaha Ltd.", "Yamaha"),
            ("KORG Synths", "Korg"),
            # "Instruments" is stripped as suffix
            ("Native Instruments", "Native"),
        ]

        for input_brand, expected in test_cases:
            result = refinery._normalize_brand(input_brand)
            assert result == expected, f"Failed: {input_brand} → {result} (expected {expected})"

        print("✅ Brand normalization tests passed")

    def test_price_parsing(self):
        """Test that prices are correctly parsed from various formats"""
        refinery = DataRefinery()

        test_cases = [
            (2500, 2500.0),
            ("2500", 2500.0),
            ("2500.00", 2500.0),
            ("€1999.99", 1999.99),
            ("£1500", 1500.0),
            ("free", 0.0),
            ("", 0.0),
        ]

        for input_price, expected in test_cases:
            result = refinery._parse_price(input_price)
            assert result == expected, f"Failed: {input_price} → {result} (expected {expected})"

        print("✅ Price parsing tests passed")

    def test_tier_calculation(self):
        """Test that product tiers are correctly calculated"""
        refinery = DataRefinery()

        test_cases = [
            (100, "entry"),
            (400, "entry"),
            (499, "entry"),
            (500, "mid"),  # Boundary: 500 to 1499
            (1000, "mid"),
            (1499, "mid"),
            (1500, "pro"),  # Boundary: 1500 to 3999
            (2000, "pro"),
            (3999, "pro"),
            (4000, "flagship"),  # Boundary: 4000+
            (10000, "flagship"),
        ]

        for price, expected_tier in test_cases:
            tier = refinery._determine_tier(price)
            assert tier == expected_tier, f"Failed: ${price} → {tier} (expected {expected_tier})"

        print("✅ Tier calculation tests passed")

    def test_search_token_generation(self):
        """Test that search tokens are generated correctly"""
        refinery = DataRefinery()

        item = {
            "name": "Juno-60",
            "brand": "Roland",
            "category": "Synthesizers",
            "subCategory": "Analog",
            "tags": ["warm", "vintage"],
            "description": "Classic analog synthesizer"
        }

        tokens = refinery._generate_search_tokens(item, "Roland", "pro")

        # Verify all key terms are present
        assert "juno-60" in tokens
        assert "roland" in tokens
        assert "synthesizers" in tokens
        assert "analog" in tokens
        assert "warm" in tokens
        assert "vintage" in tokens
        assert "pro" in tokens

        print("✅ Search token generation tests passed")

    def test_refinement_completeness(self):
        """Test that refined items have all required fields"""
        refinery = DataRefinery()

        raw_item = {
            "name": "Test Product",
            "brand": "Test Brand",
            "price": 1500,
            "category": "Synths"
        }

        refined = refinery._refine_item(raw_item)

        # Check all required fields exist
        required_fields = [
            "id", "name", "brand", "category", "subCategory",
            "tier", "images", "price", "stockStatus", "aiTags",
            "specs", "searchTokens", "description"
        ]

        for field in required_fields:
            assert field in refined, f"Missing field: {field}"

        # Check nested structures
        assert "main" in refined["images"]
        assert "thumbnail" in refined["images"]
        assert "gallery" in refined["images"]

        print("✅ Refinement completeness tests passed")

    def test_validation_strict_mode(self):
        """Test that validation properly rejects invalid items"""
        refinery = DataRefinery()

        invalid_items = [
            {"name": "", "brand": "Brand"},  # Empty name
            {"name": "Product", "brand": ""},  # Empty brand
            {"name": "A", "brand": "Brand"},  # Name too short
        ]

        for item in invalid_items:
            refined = refinery._refine_item(item)
            result = refinery._validate_item(refined)
            assert not result, f"Should reject: {item}"

        print("✅ Validation strict mode tests passed")

    def test_validation_soft_warnings(self):
        """Test that validation generates soft warnings for non-critical issues"""
        refinery = DataRefinery()

        item = {
            "name": "Test Product",
            "brand": "Test Brand",
            "price": 0,  # Should warn
            "category": "Synths"
            # Missing image_url should warn
        }

        refined = refinery._refine_item(item)
        refinery._validate_item(refined)

        # Should have warnings but still validate
        assert len(refinery.validation_warnings) > 0

        print("✅ Validation soft warnings tests passed")

    def test_category_tree_extraction(self):
        """Test that category trees are properly extracted"""
        refinery = DataRefinery()

        items = [
            {
                "name": "Synth 1",
                "brand": "Roland",
                "category": "Synthesizers",
                "subCategory": "Mono",
                "price": 1000
            },
            {
                "name": "Synth 2",
                "brand": "Nord",
                "category": "Synthesizers",
                "subCategory": "Poly",
                "price": 2000
            },
            {
                "name": "Drum 1",
                "brand": "Elektron",
                "category": "Drums",
                "subCategory": "Machines",
                "price": 800
            }
        ]

        refinery.ingest_raw_data(items)
        tree = refinery._extract_category_tree()

        assert "Synthesizers" in tree
        assert "Drums" in tree
        assert "Mono" in tree["Synthesizers"]
        assert "Poly" in tree["Synthesizers"]
        assert "Machines" in tree["Drums"]

        print("✅ Category tree extraction tests passed")

    def test_bulk_ingestion(self):
        """Test ingestion of large batches"""
        refinery = DataRefinery()

        items = [
            {
                "name": f"Product {i}",
                "brand": f"Brand {i % 5}",
                "category": "Test",
                "price": 100 + i * 100
            }
            for i in range(50)
        ]

        count = refinery.ingest_raw_data(items)

        assert count == 50, f"Should accept all 50 items, got {count}"
        assert len(refinery.products) == 50

        print("✅ Bulk ingestion tests passed")

    def test_export_json_structure(self):
        """Test that exported JSON has correct structure"""
        with TemporaryDirectory() as tmpdir:
            refinery = DataRefinery()

            items = [
                {
                    "name": "Test Product",
                    "brand": "Test Brand",
                    "category": "Test",
                    "price": 1000
                }
            ]

            refinery.ingest_raw_data(items)

            output_path = Path(tmpdir) / "test.json"
            success = refinery.export_golden_json(str(output_path))

            assert success

            with open(output_path) as f:
                data = json.load(f)

            # Verify structure
            assert "generatedAt" in data
            assert "version" in data
            assert "stats" in data
            assert "products" in data
            assert "categories" in data

            # Verify stats
            assert data["stats"]["totalProducts"] == 1
            assert data["stats"]["brandsCount"] == 1

            print("✅ Export JSON structure tests passed")

    def test_empty_refinery_export(self):
        """Test that empty refinery rejects export"""
        refinery = DataRefinery()

        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "empty.json"
            success = refinery.export_golden_json(str(output_path))

            assert not success

        print("✅ Empty refinery export tests passed")

    def test_special_characters_handling(self):
        """Test that special characters are properly handled"""
        refinery = DataRefinery()

        items = [
            {
                "name": "Juno-60 X™",
                "brand": "Roland®",
                "category": "Synthesizers",
                "price": 1500,
                "specs": {"note": "Product with special chars ñ é ü"}
            }
        ]

        count = refinery.ingest_raw_data(items)

        assert count == 1
        assert refinery.products[0]["name"] == "Juno-60 X™"

        print("✅ Special characters handling tests passed")

    def test_duplicate_handling(self):
        """Test that duplicates are processed correctly"""
        refinery = DataRefinery()

        items = [
            {
                "id": "product-1",
                "name": "Product A",
                "brand": "Brand A",
                "category": "Test",
                "price": 1000
            },
            {
                "id": "product-1",  # Same ID
                "name": "Product A",
                "brand": "Brand A",
                "category": "Test",
                "price": 1000
            }
        ]

        count = refinery.ingest_raw_data(items)

        # Both should be accepted (refinery doesn't deduplicate)
        assert count == 2

        print("✅ Duplicate handling tests passed")


def run_all_backend_tests():
    """Run all backend unit tests"""
    print("\n" + "="*70)
    print("🧪 BACKEND UNIT TESTS - Galaxy Data Pipeline")
    print("="*70 + "\n")

    tester = TestDataRefinery()
    tests = [
        ("Brand Normalization", tester.test_brand_normalization),
        ("Price Parsing", tester.test_price_parsing),
        ("Tier Calculation", tester.test_tier_calculation),
        ("Search Token Generation", tester.test_search_token_generation),
        ("Refinement Completeness", tester.test_refinement_completeness),
        ("Validation Strict Mode", tester.test_validation_strict_mode),
        ("Validation Soft Warnings", tester.test_validation_soft_warnings),
        ("Category Tree Extraction", tester.test_category_tree_extraction),
        ("Bulk Ingestion", tester.test_bulk_ingestion),
        ("Export JSON Structure", tester.test_export_json_structure),
        ("Empty Refinery Export", tester.test_empty_refinery_export),
        ("Special Characters", tester.test_special_characters_handling),
        ("Duplicate Handling", tester.test_duplicate_handling),
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
    success = run_all_backend_tests()
    sys.exit(0 if success else 1)
