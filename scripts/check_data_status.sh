#!/bin/bash
# Quick check: Are products enriched with specs?

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔍 Checking Data Enrichment Status..."
echo ""

# Check a sample product
SAMPLE_BRAND="roland"
SAMPLE_FILE="frontend/public/data/${SAMPLE_BRAND}.json"

if [ ! -f "$SAMPLE_FILE" ]; then
    echo "❌ Sample file not found: $SAMPLE_FILE"
    exit 1
fi

echo "📦 Checking: $SAMPLE_FILE"
python3 << 'PYTHON'
import json
import sys

try:
    with open('frontend/public/data/roland.json', 'r') as f:
        data = json.load(f)
    
    # Handle both list and dict formats
    if isinstance(data, list):
        product = data[0] if data else {}
    else:
        products = data.get('products', [])
        product = products[0] if products else {}
    
    if not product:
        print("❌ No products found in file")
        sys.exit(1)
    
    print(f"✅ Product found: {product.get('product_name', 'N/A')}")
    print(f"   ID: {product.get('halilit_id', 'N/A')}")
    print("")
    
    # Check for enrichment fields
    has_official_specs = bool(product.get('official_specs') and isinstance(product.get('official_specs'), dict) and any(product.get('official_specs', {}).values()))
    has_specs = bool(product.get('specs'))
    has_specifications = bool(product.get('specifications'))
    has_official_desc = bool(product.get('official_description') and len(str(product.get('official_description', '')).strip()) > 50)
    has_official_images = bool(product.get('official_images'))
    has_official_url = bool(product.get('official_url'))
    
    print("📊 Enrichment Status:")
    print(f"   official_specs: {'✅ YES' if has_official_specs else '❌ NO'}")
    print(f"   specs: {'✅ YES' if has_specs else '❌ NO'}")
    print(f"   specifications: {'✅ YES' if has_specifications else '❌ NO'}")
    print(f"   official_description: {'✅ YES' if has_official_desc else '❌ NO'}")
    print(f"   official_images: {'✅ YES' if has_official_images else '❌ NO'}")
    print(f"   official_url: {'✅ YES' if has_official_url else '❌ NO'}")
    print("")
    
    if has_official_specs:
        spec_keys = list(product.get('official_specs', {}).keys())[:5]
        print(f"   Spec keys: {spec_keys}")
    elif has_specifications:
        spec_keys = list(product.get('specifications', {}).keys())[:5]
        print(f"   Specification keys: {spec_keys}")
    
    print("")
    
    # Overall status
    enriched_fields = sum([
        has_official_specs or has_specs or has_specifications,
        has_official_desc,
        has_official_images,
        has_official_url
    ])
    
    if enriched_fields == 0:
        print("❌ STATUS: NOT ENRICHED")
        print("   → Run: python backend/conductor_main.py enrich")
        print("   → Then: python backend/conductor_main.py rebuild-catalog")
        sys.exit(1)
    elif enriched_fields < 3:
        print("⚠️  STATUS: PARTIALLY ENRICHED")
        print("   → Some fields missing, consider re-running enrichment")
    else:
        print("✅ STATUS: ENRICHED")
        print("   → Data looks good!")
        
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
PYTHON

echo ""
echo "📋 Next Steps:"
echo "   1. If NOT ENRICHED: python backend/conductor_main.py enrich"
echo "   2. Rebuild catalog: python backend/conductor_main.py rebuild-catalog"
echo "   3. Restart servers: ./start_console.sh"
