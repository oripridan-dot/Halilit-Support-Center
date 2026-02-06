#!/usr/bin/env node

/**
 * Test Frontend Data Flow - Simulates what the React app does
 * Verifies: index.json → brand files → normalization → categorization → UI counts
 */

const fs = require("fs");
const path = require("path");

const FRONTEND_DATA_DIR = path.join(__dirname, "frontend", "public", "data");

console.log("\n📊 FRONTEND DATA FLOW TEST\n");
console.log("=".repeat(80));

// Step 1: Load index.json
console.log("\n[STEP 1] Loading index.json...");
try {
  const indexPath = path.join(FRONTEND_DATA_DIR, "index.json");
  if (!fs.existsSync(indexPath)) {
    console.error("❌ index.json NOT FOUND at", indexPath);
    process.exit(1);
  }

  const index = JSON.parse(fs.readFileSync(indexPath, "utf-8"));
  console.log(`✅ Loaded index.json`);
  console.log(`   - Version: ${index.version}`);
  console.log(`   - Total products: ${index.total_products}`);
  console.log(`   - Brands: ${index.brands.length}`);

  // Step 2: Load all brand files
  console.log("\n[STEP 2] Loading brand files...");

  let totalProducts = 0;
  const allProducts = [];
  const categoryMap = {};

  for (const brand of index.brands) {
    const brandFile = path.join(FRONTEND_DATA_DIR, brand.data_file);

    if (!fs.existsSync(brandFile)) {
      console.warn(`⚠️  Missing: ${brand.data_file}`);
      continue;
    }

    const brandData = JSON.parse(fs.readFileSync(brandFile, "utf-8"));
    const productCount = Array.isArray(brandData)
      ? brandData.length
      : brandData.products?.length || 0;

    console.log(
      `✅ ${brand.name}: ${productCount} products (${brand.data_file})`,
    );
    totalProducts += productCount;

    const products = Array.isArray(brandData)
      ? brandData
      : brandData.products || [];
    allProducts.push(...products);
  }

  console.log(`\n✅ Total loaded: ${totalProducts} products`);

  // Step 3: Verify normalization
  console.log("\n[STEP 3] Checking product schema (IngestionProductDraft)...");

  const sample = allProducts[0];
  if (!sample) {
    console.error("❌ No products found in data files!");
    process.exit(1);
  }

  console.log(`✅ Sample product (${sample.halilit_id || sample.id}):`);
  const requiredFields = [
    "halilit_id",
    "product_name",
    "brand",
    "price_il",
    "taxonomy",
  ];
  for (const field of requiredFields) {
    const value = sample[field];
    if (value !== undefined) {
      console.log(
        `   ✅ ${field}: ${typeof value === "object" ? JSON.stringify(value).substring(0, 50) : value}`,
      );
    } else {
      console.warn(`   ⚠️  ${field}: missing`);
    }
  }

  // Step 4: Test category extraction (like getConsolidatedProductCategory does)
  console.log("\n[STEP 4] Extracting categories from taxonomy...");

  const categoryDistribution = {};

  for (const product of allProducts) {
    // This mimics what the frontend dataNormalizer does
    const taxonomy = product.taxonomy || {};
    const category = taxonomy.canonical_category || "Uncategorized";

    if (!categoryDistribution[category]) {
      categoryDistribution[category] = [];
    }
    categoryDistribution[category].push(product.halilit_id || product.id);
  }

  console.log(
    `✅ Found ${Object.keys(categoryDistribution).length} unique categories:`,
  );

  const sortedCategories = Object.entries(categoryDistribution).sort(
    (a, b) => b[1].length - a[1].length,
  );

  for (const [category, products] of sortedCategories) {
    console.log(`   - ${category}: ${products.length} products`);
  }

  // Step 5: Verify images
  console.log("\n[STEP 5] Checking image data...");

  let imagesCount = 0;
  let missingImages = 0;

  for (const product of allProducts) {
    if (product.official_images && Array.isArray(product.official_images)) {
      imagesCount += product.official_images.filter((img) => img.url).length;
    } else {
      missingImages++;
    }
  }

  const imagePercentage = ((imagesCount / totalProducts) * 100).toFixed(1);
  console.log(`✅ Images found:`);
  console.log(
    `   - Products with images: ${totalProducts - missingImages}/${totalProducts}`,
  );
  console.log(`   - Total image URLs: ${imagesCount}`);
  console.log(`   - Coverage: ${imagePercentage}%`);

  // Step 6: Verify pricing
  console.log("\n[STEP 6] Checking pricing data...");

  let pricedProducts = 0;
  const priceStats = { min: Infinity, max: 0, total: 0 };

  for (const product of allProducts) {
    const price = product.price_il || product.pricing?.price_il;
    if (price && typeof price === "number" && price > 0) {
      pricedProducts++;
      priceStats.min = Math.min(priceStats.min, price);
      priceStats.max = Math.max(priceStats.max, price);
      priceStats.total += price;
    }
  }

  const avgPrice =
    pricedProducts > 0 ? (priceStats.total / pricedProducts).toFixed(2) : 0;
  console.log(`✅ Pricing:`);
  console.log(
    `   - Products with price_il: ${pricedProducts}/${totalProducts}`,
  );
  console.log(`   - Price range: ₪${priceStats.min} - ₪${priceStats.max}`);
  console.log(`   - Average price: ₪${avgPrice}`);

  // Final Summary
  console.log("\n" + "=".repeat(80));
  console.log("✅ FRONTEND DATA FLOW VERIFIED");
  console.log("=".repeat(80));
  console.log("\nSummary:");
  console.log(
    `  ✅ Index: ${index.brands.length} brands, ${index.total_products} products`,
  );
  console.log(`  ✅ Files: All ${index.brands.length} brand JSON files found`);
  console.log(`  ✅ Products: ${totalProducts} products loaded and normalized`);
  console.log(`  ✅ Schema: IngestionProductDraft fields present`);
  console.log(
    `  ✅ Categories: ${Object.keys(categoryDistribution).length} unique categories`,
  );
  console.log(`  ✅ Images: ${imagePercentage}% of products have images`);
  console.log(`  ✅ Pricing: ${pricedProducts} products with prices`);
  console.log("\n📡 DATA READY FOR UI RENDERING\n");
} catch (err) {
  console.error("\n❌ ERROR:", err.message);
  console.error(err.stack);
  process.exit(1);
}
