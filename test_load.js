const fs = require('fs');
const path = require('path');

// Read index.json
const indexPath = path.join(__dirname, 'frontend/public/data/index.json');
const indexData = JSON.parse(fs.readFileSync(indexPath, 'utf-8'));

console.log('\n=== INDEX SUMMARY ===');
console.log(`Total products claimed: ${indexData.total_products}`);
console.log(`Total brands in index: ${indexData.brands.length}`);
console.log('\nBrands:');
indexData.brands.forEach(b => {
  console.log(`  - ${b.name}: ${b.product_count} products (${b.data_file})`);
});

console.log('\n=== ACTUAL FILE CHECKS ===');
let totalActual = 0;
indexData.brands.forEach(b => {
  const filePath = path.join(__dirname, `frontend/public/data/${b.data_file}`);
  try {
    const data = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
    const count = Array.isArray(data) ? data.length : (data.products ? data.products.length : 0);
    console.log(`${b.name}: ${count} actual products`);
    totalActual += count;
  } catch (e) {
    console.log(`${b.name}: ERROR - ${e.message}`);
  }
});

console.log(`\nTotal actual products across all brands: ${totalActual}`);
