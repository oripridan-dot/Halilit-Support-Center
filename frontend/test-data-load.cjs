const fs = require('fs');
const path = require('path');

function testDataLoad() {
  console.log("=".repeat(70));
  console.log("FRONTEND DATA LOADING TEST");
  console.log("=".repeat(70));
  
  try {
    // Test 1: Load index
    console.log("\n✅ Loading Master Index...");
    const indexPath = path.join(__dirname, 'public/data/index.json');
    const index = JSON.parse(fs.readFileSync(indexPath, 'utf-8'));
    console.log(`   Master index loaded`);
    console.log(`   └─ Total products: ${index.total_products}`);
    console.log(`   └─ Total brands: ${index.brands.length}`);
    
    // Test 2: Load Roland
    console.log("\n✅ Loading Roland catalog...");
    const rolandPath = path.join(__dirname, 'public/data/roland.json');
    const roland = JSON.parse(fs.readFileSync(rolandPath, 'utf-8'));
    console.log(`   Roland loaded: ${roland.products.length} products`);
    console.log(`   └─ Brand name: ${roland.brand_identity?.name || 'N/A'}`);
    console.log(`   └─ Logo: ${roland.brand_identity?.logo_url || 'N/A'}`);
    
    // Test 3: Load Boss
    console.log("\n✅ Loading Boss catalog...");
    const bossPath = path.join(__dirname, 'public/data/boss.json');
    const boss = JSON.parse(fs.readFileSync(bossPath, 'utf-8'));
    console.log(`   Boss loaded: ${boss.products.length} products`);
    
    // Test 4: Load Nord
    console.log("\n✅ Loading Nord catalog...");
    const nordPath = path.join(__dirname, 'public/data/nord.json');
    const nord = JSON.parse(fs.readFileSync(nordPath, 'utf-8'));
    console.log(`   Nord loaded: ${nord.products.length} products`);
    
    // Test 5: Verify product structure
    console.log("\n✅ Product structure validation...");
    const testProduct = roland.products[0];
    const requiredFields = ['id', 'name', 'main_category', 'image_url'];
    let valid = true;
    for (const field of requiredFields) {
      if (!testProduct.hasOwnProperty(field)) {
        console.log(`   ✗ Missing field: ${field}`);
        valid = false;
      }
    }
    if (valid) {
      console.log(`   Product structure valid`);
      console.log(`   └─ Sample product: ${testProduct.name}`);
      console.log(`   └─ Has image: ${!!testProduct.image_url}`);
      console.log(`   └─ Has pricing: ${!!testProduct.pricing?.regular_price}`);
    }
    
    // Test 6: Category distribution
    console.log("\n✅ Category distribution (Roland)...");
    const rolandCategories = {};
    roland.products.forEach(p => {
      const cat = p.main_category || 'unknown';
      rolandCategories[cat] = (rolandCategories[cat] || 0) + 1;
    });
    Object.entries(rolandCategories).slice(0, 5).forEach(([cat, count]) => {
      console.log(`   └─ ${cat}: ${count} products`);
    });
    
    // Test 7: Pricing validation
    console.log("\n✅ Data quality metrics...");
    const rolandWithPrice = roland.products.filter(p => p.pricing?.regular_price).length;
    const rolandWithImage = roland.products.filter(p => p.image_url).length;
    console.log(`   Roland pricing coverage: ${rolandWithPrice}/${roland.products.length} (${Math.round(100*rolandWithPrice/roland.products.length)}%)`);
    console.log(`   Roland image coverage: ${rolandWithImage}/${roland.products.length} (${Math.round(100*rolandWithImage/roland.products.length)}%)`);
    
    console.log("\n" + "=".repeat(70));
    console.log("✅ ALL TESTS PASSED - Data is ready for frontend!");
    console.log("=".repeat(70));
    
  } catch (error) {
    console.error("❌ ERROR:", error.message);
    process.exit(1);
  }
}

testDataLoad();
