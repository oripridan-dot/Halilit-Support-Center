const fs = require('fs');
const path = require('path');

// Simulate what catalogLoader does
async function testCatalogLoad() {
  const indexPath = path.join(__dirname, 'frontend/public/data/index.json');
  const indexData = JSON.parse(fs.readFileSync(indexPath, 'utf-8'));
  
  let allProducts = [];
  
  console.log('\n=== LOADING BRANDS ===');
  for (const brand of indexData.brands) {
    const filePath = path.join(__dirname, `frontend/public/data/${brand.data_file}`);
    try {
      const brandData = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
      const products = Array.isArray(brandData) ? brandData : (brandData.products || []);
      
      // Ensure each product has brand_id set
      const enriched = products.map(p => ({
        ...p,
        brand_id: p.brand_id || brand.id
      }));
      
      allProducts = allProducts.concat(enriched);
      console.log(`✓ ${brand.name}: loaded ${products.length} products`);
    } catch (e) {
      console.log(`✗ ${brand.name}: ERROR - ${e.message}`);
    }
  }
  
  console.log(`\nTotal products loaded: ${allProducts.length}`);
  
  // Check distribution by attribute
  console.log('\n=== PRODUCT DISTRIBUTION ===');
  const brandCount = {};
  const categoryCount = {};
  const tierCount = {};
  
  allProducts.forEach(p => {
    const brand = p.brand_id || p.brand || 'unknown';
    const category = p.category || p.main_category || 'uncategorized';
    const tier = p.tier || 'no-tier';
    
    brandCount[brand] = (brandCount[brand] || 0) + 1;
    categoryCount[category] = (categoryCount[category] || 0) + 1;
    tierCount[tier] = (tierCount[tier] || 0) + 1;
  });
  
  console.log('\nBy Brand:');
  Object.entries(brandCount).sort((a, b) => b[1] - a[1]).forEach(([k, v]) => {
    console.log(`  ${k}: ${v}`);
  });
  
  console.log('\nBy Tier:');
  Object.entries(tierCount).sort((a, b) => b[1] - a[1]).forEach(([k, v]) => {
    console.log(`  ${k}: ${v}`);
  });
  
  console.log('\nBy Category (top 10):');
  Object.entries(categoryCount).sort((a, b) => b[1] - a[1]).slice(0, 10).forEach(([k, v]) => {
    console.log(`  ${k}: ${v}`);
  });
  
  // Check if any products are missing critical fields
  console.log('\n=== DATA QUALITY CHECK ===');
  const issues = {
    noId: allProducts.filter(p => !p.id).length,
    noName: allProducts.filter(p => !p.name).length,
    noCategory: allProducts.filter(p => !p.category && !p.main_category).length,
    nullPrice: allProducts.filter(p => p.price === null || p.price === undefined).length,
    bronzeTier: allProducts.filter(p => p.tier === 'bronze').length,
  };
  
  Object.entries(issues).forEach(([k, v]) => {
    if (v > 0) console.log(`⚠️ ${k}: ${v} products`);
  });
}

testCatalogLoad().catch(console.error);
