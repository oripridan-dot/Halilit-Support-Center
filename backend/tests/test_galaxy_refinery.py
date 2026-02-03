"""
Integration Test: Galaxy Data Pipeline
Verifies that the data refinery properly validates and exports data,
and that the frontend can consume it.
"""

from backend.pipeline.data_refinery import DataRefinery
import json
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_refinery_initialization():
    """Test that refinery initializes properly."""
    refinery = DataRefinery()
    assert refinery.products == []
    assert refinery.validation_errors == []
    print("✅ Refinery initialization test passed")

def test_ingest_valid_data():
    """Test ingesting valid product data."""
    refinery = DataRefinery()

    valid_items = [
        {
            "name": "Test Synth",
            "brand": "Nord Keyboards",
            "category": "Synthesizers",
            "price": 2000,
            "image_url": "https://example.com/test.jpg",
            "specs": {"polyphony": "128"},
            "tags": ["analog", "warm"]
        }
    ]

    count = refinery.ingest_raw_data(valid_items)
    assert count == 1
    assert len(refinery.products) == 1
    assert refinery.products[0]['brand'] == "Nord"
    assert refinery.products[0]['tier'] == 'pro'  # 2000 falls in pro tier
    print("✅ Valid data ingestion test passed")

def test_validate_missing_brand():
    """Test that validation rejects items without brands."""
    refinery = DataRefinery()

    invalid_items = [
        {
            "name": "Test Product",
            "brand": "",  # Empty brand
            "category": "Test",
            "price": 1000
        }
    ]

    count = refinery.ingest_raw_data(invalid_items)
    assert count == 0  # Should be rejected
    assert len(refinery.validation_errors) > 0
    print("✅ Missing brand validation test passed")

def test_validate_missing_name():
    """Test that validation rejects items without names."""
    refinery = DataRefinery()

    invalid_items = [
        {
            "name": "",  # Empty name
            "brand": "Test Brand",
            "category": "Test",
            "price": 1000
        }
    ]

    count = refinery.ingest_raw_data(invalid_items)
    assert count == 0  # Should be rejected
    assert len(refinery.validation_errors) > 0
    print("✅ Missing name validation test passed")

def test_tier_calculation():
    """Test that tier is correctly calculated based on price."""
    refinery = DataRefinery()

    test_items = [
        {"name": "Entry", "brand": "Brand A", "price": 100},
        {"name": "Mid", "brand": "Brand B", "price": 1000},
        {"name": "Pro", "brand": "Brand C", "price": 2500},
        {"name": "Flagship", "brand": "Brand D", "price": 5000},
    ]

    refinery.ingest_raw_data(test_items)

    assert refinery.products[0]['tier'] == 'entry'
    assert refinery.products[1]['tier'] == 'mid'
    assert refinery.products[2]['tier'] == 'pro'
    assert refinery.products[3]['tier'] == 'flagship'
    print("✅ Tier calculation test passed")

def test_search_token_generation():
    """Test that search tokens are properly generated."""
    refinery = DataRefinery()

    test_items = [
        {
            "name": "Juno-60",
            "brand": "Roland",
            "category": "Synthesizers",
            "price": 2000,
            "tags": ["analog", "vintage"]
        }
    ]

    refinery.ingest_raw_data(test_items)
    product = refinery.products[0]

    # Check that search tokens contain all relevant info
    assert "juno-60" in product['searchTokens']
    assert "roland" in product['searchTokens']
    assert "synthesizers" in product['searchTokens']
    assert "analog" in product['searchTokens']
    print("✅ Search token generation test passed")

def test_export_golden_json(tmp_path):
    """Test that the refinery can export valid JSON."""
    refinery = DataRefinery()

    test_items = [
        {
            "name": "Test Synth",
            "brand": "Test Brand",
            "category": "Synths",
            "price": 1500,
            "specs": {"keys": "61"}
        }
    ]

    refinery.ingest_raw_data(test_items)

    # Export to temp file
    output_path = tmp_path / "test_galaxy_db.json"
    success = refinery.export_golden_json(str(output_path))

    assert success
    assert output_path.exists()

    # Verify JSON structure
    with open(output_path) as f:
        data = json.load(f)

    assert 'generatedAt' in data
    assert 'version' in data
    assert 'products' in data
    assert 'categories' in data
    assert len(data['products']) == 1
    print("✅ Export golden JSON test passed")

def test_category_tree_extraction():
    """Test that categories are properly extracted."""
    refinery = DataRefinery()

    test_items = [
        {"name": "Item A", "brand": "Brand A",
            "category": "Synths", "subCategory": "Mono"},
        {"name": "Item B", "brand": "Brand B",
            "category": "Synths", "subCategory": "Poly"},
        {"name": "Item C", "brand": "Brand C",
            "category": "Drums", "subCategory": "Machines"},
    ]

    refinery.ingest_raw_data(test_items)
    tree = refinery._extract_category_tree()

    assert 'Synths' in tree
    assert 'Drums' in tree
    assert 'Mono' in tree['Synths']
    assert 'Poly' in tree['Synths']
    assert 'Machines' in tree['Drums']
    print("✅ Category tree extraction test passed")

def run_all_tests():
    """Run all integration tests."""
    print("\n" + "="*60)
    print("🧪 GALAXY DATA PIPELINE INTEGRATION TESTS")
    print("="*60 + "\n")

    try:
        test_refinery_initialization()
        test_ingest_valid_data()
        test_validate_missing_brand()
        test_validate_missing_name()
        test_tier_calculation()
        test_search_token_generation()

        with TemporaryDirectory() as tmp_dir:
            test_export_golden_json(Path(tmp_dir))

        test_category_tree_extraction()

        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60 + "\n")
        return True
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
