#!/bin/bash
# Final Comprehensive Pipeline Verification

echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║         HALILIT SUPPORT CENTER - PIPELINE VERIFICATION v2.0          ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"

# 1. Verify data file integrity
echo ""
echo "📊 1. DATA FILE INTEGRITY CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

PRODUCTS_COUNT=$(curl -s http://localhost:8000/data/galaxy_db.json | python3 -c "import json, sys; print(len(json.load(sys.stdin)))")
echo "✓ Total products available: $PRODUCTS_COUNT"

# Sample a product
curl -s http://localhost:8000/data/galaxy_db.json | python3 << 'EOF'
import json, sys
data = json.load(sys.stdin)
p = data[0]
print(f"✓ Sample product loaded:")
print(f"  - Name: {p.get('product_name', 'N/A')[:40]}...")
print(f"  - Brand: {p.get('brand', 'N/A')}")
print(f"  - Category: {p.get('category', 'MISSING')}")
print(f"  - Has images: {bool(p.get('official_images'))}")
print(f"  - Has pricing: {p.get('price_il', 'N/A')}")
EOF

# 2. Verify all galaxies are populated
echo ""
echo "🌌 2. GALAXY POPULATION CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

curl -s http://localhost:8000/data/galaxy_db.json | python3 << 'EOF'
import json, sys
data = json.load(sys.stdin)

galaxies = {
    'guitars-bass': '🎸 Guitars & Bass',
    'drums-percussion': '🥁 Drums & Percussion',
    'keys-production': '🎹 Keys & Synths',
    'studio-recording': '🎙️ Studio & Recording',
    'live-dj': '🔊 Live Sound & DJ',
    'accessories-utility': '🔌 Accessories & Utility',
}

galaxy_counts = {}
for p in data:
    cat = p.get('category', 'uncategorized')
    galaxy_counts[cat] = galaxy_counts.get(cat, 0) + 1

print("Galaxy Distribution:")
total = 0
for gid, glabel in galaxies.items():
    count = galaxy_counts.get(gid, 0)
    bar = '█' * (count // 10) + '░' * (5 - (count // 10))
    total += count
    status = '✓' if count > 0 else '✗'
    print(f"  {status} {glabel:20} {bar:10} {count:3} products")
print(f"\n  Total: {total}/{len(data)} products accounted for")
EOF

# 3. Sample products from each galaxy
echo ""
echo "📦 3. SAMPLE PRODUCTS BY GALAXY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

curl -s http://localhost:8000/data/galaxy_db.json | python3 << 'EOF'
import json, sys
data = json.load(sys.stdin)

galaxies = ['drums-percussion', 'keys-production', 'studio-recording', 'live-dj', 'guitars-bass']

for galaxy in galaxies:
    products = [p for p in data if p.get('category') == galaxy]
    if products:
        p = products[0]
        name = p.get('product_name', '')[:35].ljust(35)
        brand = p.get('brand', '?')[:12].ljust(12)
        print(f"  {galaxy:18} | {name} | {brand}")
EOF

# 4. Verify API endpoints
echo ""
echo "🔌 4. API ENDPOINT VERIFICATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test root endpoint
RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8000/)
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ Frontend root endpoint: HTTP 200 OK"
else
    echo "✗ Frontend root endpoint: HTTP $HTTP_CODE"
fi

# Test data endpoint
RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8000/data/galaxy_db.json)
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ Data API endpoint: HTTP 200 OK"
else
    echo "✗ Data API endpoint: HTTP $HTTP_CODE"
fi

# Test index
RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8000/data/index.json)
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ Index endpoint: HTTP 200 OK"
else
    echo "✗ Index endpoint: HTTP $HTTP_CODE"
fi

# 5. Final validation
echo ""
echo "✅ VERIFICATION COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

curl -s http://localhost:8000/data/galaxy_db.json | python3 << 'EOF'
import json, sys
data = json.load(sys.stdin)

# Check completeness
has_all_fields = all(
    p.get('category') and 
    p.get('spectrum') and 
    p.get('product_name') and 
    p.get('brand')
    for p in data
)

galaxies_covered = len(set(
    p.get('category') for p in data 
    if p.get('category') in [
        'guitars-bass', 'drums-percussion', 'keys-production',
        'studio-recording', 'live-dj', 'accessories-utility'
    ]
))

print("")
print("STATUS:")
print(f"  {'✓' if has_all_fields else '✗'} All products have required fields")
print(f"  {'✓' if galaxies_covered == 6 else '✗'} All {galaxies_covered}/6 galaxies populated")
print(f"  ✓ Total products: {len(data)}")
print("")
if galaxies_covered == 6 and has_all_fields:
    print("🎉 PIPELINE IS READY FOR PRODUCTION")
    print("")
    print("Next steps:")
    print("  1. Open http://localhost:8000 in your browser")
    print("  2. You should see 6 galaxy cards in GalaxyDashboard")
    print("  3. Each galaxy should show product counts")
    print("  4. Clicking a galaxy will load and display products")
else:
    print("⚠️  WARNINGS DETECTED - Manual review required")
EOF

echo ""
echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║                     END OF VERIFICATION REPORT                         ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
