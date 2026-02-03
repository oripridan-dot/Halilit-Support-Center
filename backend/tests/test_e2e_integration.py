"""
End-to-End Integration Tests - Galaxy Data Protocol
Tests the complete flow: Raw Data → Refinery → Export → Frontend Consumption
"""

import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class TestE2EIntegration:
    """End-to-end integration tests"""

    def test_raw_to_frontend_flow(self):
        """Test complete flow: raw data → refinery → frontend json"""
        with TemporaryDirectory() as tmpdir:
            # Step 1: Create raw data
            raw_data = [
                {
                    "name": "Nord Lead A1",
                    "brand": "Nord Keyboards",
                    "category": "Synthesizers",
                    "subCategory": "Monosynth",
                    "price": 2500,
                    "image_url": "https://example.com/nord.jpg",
                    "specs": {"polyphony": "1", "keys": "37"},
                    "tags": ["analog", "warm"],
                    "description": "Powerful monosynth"
                },
                {
                    "name": "TR-808",
                    "brand": "Roland",
                    "category": "Drums",
                    "subCategory": "Machines",
                    "price": 5000,
                    "image_url": "https://example.com/tr808.jpg",
                    "tags": ["legendary"],
                    "description": "Iconic drum machine"
                },
                {
                    "name": "Monotron",
                    "brand": "Korg Synths",
                    "category": "Synthesizers",
                    "subCategory": "Desktop",
                    "price": 100,
                    "tags": ["mini"],
                    "description": "Tiny synth"
                }
            ]

            # Step 2: Process through refinery
            refinery = DataRefinery()
            count = refinery.ingest_raw_data(raw_data)

            assert count == 3, f"Expected 3 products, got {count}"

            # Step 3: Export to JSON
            output_path = Path(tmpdir) / "galaxy_db.json"
            success = refinery.export_golden_json(str(output_path))

            assert success
            assert output_path.exists()

            # Step 4: Verify frontend can consume it
            with open(output_path) as f:
                catalog = json.load(f)

            # Verify structure
            assert catalog["stats"]["totalProducts"] == 3
            assert catalog["stats"]["brandsCount"] == 3

            # Verify products are normalized
            products = {p["id"]: p for p in catalog["products"]}

            # Check Nord (brand normalized)
            nord_products = [p for p in catalog["products"]
                             if p["brand"] == "Nord"]
            assert len(nord_products) == 1
            assert nord_products[0]["tier"] == "pro"

            # Check TR-808 (flagship tier)
            tr808 = [p for p in catalog["products"] if "808" in p["name"]][0]
            assert tr808["tier"] == "flagship"

            # Check Korg (brand normalized)
            korg_products = [p for p in catalog["products"]
                             if p["brand"] == "Korg"]
            assert len(korg_products) == 1
            assert korg_products[0]["tier"] == "entry"

            print("✅ Raw to frontend flow test passed")

    def test_search_pipeline(self):
        """Test that search works on exported data"""
        with TemporaryDirectory() as tmpdir:
            refinery = DataRefinery()

            raw_data = [
                {"name": "Warm Analog Synth", "brand": "Brand A",
                    "category": "Synths", "price": 2000, "tags": ["warm", "analog"]},
                {"name": "Digital Synth", "brand": "Brand B",
                    "category": "Synths", "price": 1000, "tags": ["digital"]},
                {"name": "Warm Pad Controller", "brand": "Brand C",
                    "category": "Controllers", "price": 300, "tags": ["warm"]},
            ]

            refinery.ingest_raw_data(raw_data)

            output_path = Path(tmpdir) / "search_test.json"
            refinery.export_golden_json(str(output_path))

            with open(output_path) as f:
                catalog = json.load(f)

            # Simulate frontend search for "warm"
            query = "warm"
            results = [p for p in catalog["products"]
                       if query in p["searchTokens"]]

            assert len(results) == 2  # Two products have "warm"
            assert any("Analog" in p["name"] for p in results)
            assert any("Pad" in p["name"] for p in results)

            print("✅ Search pipeline test passed")

    def test_category_navigation_pipeline(self):
        """Test that category navigation works end-to-end"""
        with TemporaryDirectory() as tmpdir:
            refinery = DataRefinery()

            raw_data = [
                {"name": "Synth 1", "brand": "Brand A", "category": "Synths",
                    "subCategory": "Mono", "price": 2000},
                {"name": "Synth 2", "brand": "Brand B", "category": "Synths",
                    "subCategory": "Poly", "price": 1500},
                {"name": "Drum 1", "brand": "Brand C", "category": "Drums",
                    "subCategory": "Machines", "price": 800},
            ]

            refinery.ingest_raw_data(raw_data)
            output_path = Path(tmpdir) / "category_test.json"
            refinery.export_golden_json(str(output_path))

            with open(output_path) as f:
                catalog = json.load(f)

            # Verify category tree
            assert "Synths" in catalog["categories"]
            assert "Drums" in catalog["categories"]
            assert "Mono" in catalog["categories"]["Synths"]
            assert "Poly" in catalog["categories"]["Synths"]
            assert "Machines" in catalog["categories"]["Drums"]

            # Simulate frontend navigation
            synth_products = [p for p in catalog["products"]
                              if p["category"] == "Synths"]
            mono_synths = [
                p for p in synth_products if p["subCategory"] == "Mono"]

            assert len(synth_products) == 2
            assert len(mono_synths) == 1

            print("✅ Category navigation pipeline test passed")

    def test_tier_filtering_pipeline(self):
        """Test that tier filtering works end-to-end"""
        with TemporaryDirectory() as tmpdir:
            refinery = DataRefinery()

            raw_data = [
                {"name": "Budget Synth", "brand": "Brand A",
                    "category": "Synths", "price": 200},
                {"name": "Mid Synth", "brand": "Brand B",
                    "category": "Synths", "price": 1200},
                {"name": "Pro Synth", "brand": "Brand C",
                    "category": "Synths", "price": 3000},
                {"name": "Flagship Synth", "brand": "Brand D",
                    "category": "Synths", "price": 6000},
            ]

            refinery.ingest_raw_data(raw_data)
            output_path = Path(tmpdir) / "tier_test.json"
            refinery.export_golden_json(str(output_path))

            with open(output_path) as f:
                catalog = json.load(f)

            # Test tier filtering
            tiers = {
                "entry": [p for p in catalog["products"] if p["tier"] == "entry"],
                "mid": [p for p in catalog["products"] if p["tier"] == "mid"],
                "pro": [p for p in catalog["products"] if p["tier"] == "pro"],
                "flagship": [p for p in catalog["products"] if p["tier"] == "flagship"],
            }

            assert len(tiers["entry"]) == 1
            assert len(tiers["mid"]) == 1
            assert len(tiers["pro"]) == 1
            assert len(tiers["flagship"]) == 1

            print("✅ Tier filtering pipeline test passed")

    def test_brand_aggregation_pipeline(self):
        """Test brand aggregation across products"""
        with TemporaryDirectory() as tmpdir:
            refinery = DataRefinery()

            raw_data = [
                {"name": "Nord 1", "brand": "Nord",
                    "category": "Synths", "price": 2000},
                {"name": "Nord 2", "brand": "Nord Keyboards",
                    "category": "Synths", "price": 1500},
                {"name": "Roland 1", "brand": "Roland",
                    "category": "Drums", "price": 800},
                {"name": "Moog 1", "brand": "Moog",
                    "category": "Synths", "price": 3000},
            ]

            refinery.ingest_raw_data(raw_data)
            output_path = Path(tmpdir) / "brand_test.json"
            refinery.export_golden_json(str(output_path))

            with open(output_path) as f:
                catalog = json.load(f)

            # Simulate brand aggregation
            brands = {}
            for product in catalog["products"]:
                brand = product["brand"]
                if brand not in brands:
                    brands[brand] = []
                brands[brand].append(product)

            assert len(brands["Nord"]) == 2  # Normalized brand
            assert len(brands["Roland"]) == 1
            assert len(brands["Moog"]) == 1

            print("✅ Brand aggregation pipeline test passed")

    def test_data_consistency_pipeline(self):
        """Test that data consistency is maintained through pipeline"""
        with TemporaryDirectory() as tmpdir:
            refinery = DataRefinery()

            original_data = {
                "name": "Test Product",
                "brand": "Test Brand",
                "category": "Test Cat",
                "subCategory": "Test SubCat",
                "price": 1500,  # This should be "pro" tier
                "specs": {"key": "value"},
                "tags": ["tag1", "tag2"],
                "description": "Test Description"
            }

            refinery.ingest_raw_data([original_data])
            output_path = Path(tmpdir) / "consistency_test.json"
            refinery.export_golden_json(str(output_path))

            with open(output_path) as f:
                catalog = json.load(f)

            exported_product = catalog["products"][0]

            # Verify original data is preserved
            assert exported_product["name"] == original_data["name"]
            assert exported_product["category"] == original_data["category"]
            assert exported_product["subCategory"] == original_data["subCategory"]
            assert exported_product["specs"] == original_data["specs"]
            assert exported_product["description"] == original_data["description"]

            # Verify enrichments were added
            assert "tier" in exported_product
            assert "searchTokens" in exported_product
            # 1500 falls into pro tier
            assert exported_product["tier"] == "pro"

            print("✅ Data consistency pipeline test passed")

    def test_validation_gates_pipeline(self):
        """Test that validation gates work throughout pipeline"""
        with TemporaryDirectory() as tmpdir:
            refinery = DataRefinery()

            mixed_data = [
                {"name": "Good Product", "brand": "Good Brand", "price": 1000},  # Good
                {"name": "", "brand": "Bad Brand", "price": 1000},  # Bad - no name
                {"name": "No Brand", "brand": "", "price": 1000},  # Bad - no brand
                {"name": "Good Product 2", "brand": "Good Brand 2",
                    "price": 2000},  # Good
            ]

            count = refinery.ingest_raw_data(mixed_data)

            # Only 2 good products should pass
            assert count == 2

            output_path = Path(tmpdir) / "validation_test.json"
            success = refinery.export_golden_json(str(output_path))

            assert success

            with open(output_path) as f:
                catalog = json.load(f)

            # Verify only valid products in export
            assert catalog["stats"]["totalProducts"] == 2

            print("✅ Validation gates pipeline test passed")

    def test_large_dataset_pipeline(self):
        """Test pipeline with large dataset"""
        with TemporaryDirectory() as tmpdir:
            refinery = DataRefinery()

            # Generate 1000 products
            raw_data = [
                {
                    "name": f"Product {i}",
                    "brand": f"Brand {i % 10}",
                    "category": f"Category {i % 5}",
                    "subCategory": f"SubCat {i % 20}",
                    "price": 100 + (i * 10 % 5000),
                    "tags": [f"tag{i % 3}"]
                }
                for i in range(1000)
            ]

            count = refinery.ingest_raw_data(raw_data)

            assert count == 1000

            output_path = Path(tmpdir) / "large_test.json"
            success = refinery.export_golden_json(str(output_path))

            assert success

            with open(output_path) as f:
                catalog = json.load(f)

            assert catalog["stats"]["totalProducts"] == 1000
            assert catalog["stats"]["brandsCount"] == 10

            # Verify searchability
            query = "product 500"
            results = [p for p in catalog["products"]
                       if query in p["searchTokens"]]
            assert len(results) > 0

            print("✅ Large dataset pipeline test passed")

    def test_json_export_validity(self):
        """Test that exported JSON is valid and parseable"""
        with TemporaryDirectory() as tmpdir:
            refinery = DataRefinery()

            raw_data = [
                {"name": f"Product {i}", "brand": f"Brand {i % 3}", "price": 1000}
                for i in range(50)
            ]

            refinery.ingest_raw_data(raw_data)
            output_path = Path(tmpdir) / "json_test.json"
            refinery.export_golden_json(str(output_path))

            # Try to load and re-parse
            with open(output_path) as f:
                data1 = json.load(f)

            # Dump and re-load to test serialization
            re_exported = json.dumps(data1)
            data2 = json.loads(re_exported)

            # Verify consistency
            assert data1["stats"]["totalProducts"] == data2["stats"]["totalProducts"]
            assert len(data1["products"]) == len(data2["products"])

            print("✅ JSON export validity test passed")

def run_all_e2e_tests():
    """Run all e2e integration tests"""
    print("\n" + "="*70)
    print("🧪 END-TO-END INTEGRATION TESTS - Galaxy Data Protocol")
    print("="*70 + "\n")

    tester = TestE2EIntegration()
    tests = [
        ("Raw to Frontend Flow", tester.test_raw_to_frontend_flow),
        ("Search Pipeline", tester.test_search_pipeline),
        ("Category Navigation Pipeline", tester.test_category_navigation_pipeline),
        ("Tier Filtering Pipeline", tester.test_tier_filtering_pipeline),
        ("Brand Aggregation Pipeline", tester.test_brand_aggregation_pipeline),
        ("Data Consistency Pipeline", tester.test_data_consistency_pipeline),
        ("Validation Gates Pipeline", tester.test_validation_gates_pipeline),
        ("Large Dataset Pipeline", tester.test_large_dataset_pipeline),
        ("JSON Export Validity", tester.test_json_export_validity),
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
    success = run_all_e2e_tests()
    sys.exit(0 if success else 1)
