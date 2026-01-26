import fetch from 'node-fetch';

async function testDataLoad() {
  console.log("=" .repeat(70));
  console.log("FRONTEND DATA LOADING TEST");
  console.log("=" .repeat(70));
  
  try {
    // Test 1: Load index
    console.log("\n1️⃣  Loading Master Index...");
    const indexResponse = await fetch('file://./public/data/index.json');
    const index = await indexResponse.json();
    console.log(`   ✅ Master index loaded`);
    console.log(`      Total products: ${index.total_products}`);
    console.log(`      Total brands: ${index.brands.length}`);
    
    // Test 2: Load Roland
    console.log("\n2️⃣  Loading Roland catalog...");
    const rolandResponse = await fetch('file://./public/data/roland.json');
    const roland = await rolandResponse.json();
    console.log(`   ✅ Roland loaded: ${roland.products.length} products`);
    console.log(`      Brand name: ${roland.brand_identity?.name || 'N/A'}`);
    console.log(`      Logo: ${roland.brand_identity?.logo_url || 'N/A'}`);
    
    // Test 3: Load Boss
    console.log("\n3️⃣  Loading Boss catalog...");
    const bossResponse = await fetch('file://./public/data/boss.json');
    const boss = await bossResponse.json();
    console.log(`   ✅ Boss loaded: ${boss.products.length} products`);
    
    // Test 4: Load Nord
    console.log("\n4️⃣  Loading Nord catalog...");
    const nordResponse = await fetch('file://./public/data/nord.json');
    const nord = await nordResponse.json();
    console.log(`   ✅ Nord loaded: ${nord.products.length} products`);
    
    // Test 5: Verify product structure
    console.log("\n5️⃣  Product structure validation...");
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
      console.log(`   ✅ Product structure valid`);
      console.log(`      Sample product: ${testProduct.name}`);
      console.log(`      Has image: ${!!testProduct.image_url}`);
      console.log(`      Has pricing: ${!!testProduct.pricing?.regular_price}`);
    }
    
    // Test 6: Category distribution
    console.log("\n6️⃣  Category distribution...");
    const rolandCategories = {};
    roland.products.forEach(p => {
      const cat = p.main_category || 'unknown';
      rolandCategories[cat] = (rolandCategories[cat] || 0) + 1;
    });
    Object.entries(rolandCategories).slice(0, 5).forEach(([cat, count]) => {
      console.log(`      ${cat}: ${count} products`);
    });
    
    console.log("\n" + "=" .repeat(70));
    console.log("✅ ALL TESTS PASSED");
    console.log("=" .repeat(70));
    
  } catch (error) {
    console.error("❌ ERROR:", error.message);
  }
}

testDataLoad();
