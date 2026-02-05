import fs from 'fs';

// Load the mapping logic directly
const categories = new Map(Object.entries({
  "keyboards & synthesizers": "synthesizers",
  "keyboards synthesizers": "synthesizers",
  "drums & percussion": "electronic-drums",
  "drums percussion": "electronic-drums",
  "microphones & recording": "studio-microphones",
  "audio interfaces & mixers": "audio-interfaces",
  "studio monitors & speakers": "studio-monitors",
  "amplifiers & effects": "guitar-pedals",
  "headphones & earphones": "headphones",
  "cables & connectors": "cables",
}));

function mapCategoryToSpectrum(category) {
  const categoryLower = category.toLowerCase().trim();
  if (categories.has(categoryLower)) {
    return categories.get(categoryLower);
  }
  return "accessories-utility";
}

// Test with real data
const products = JSON.parse(fs.readFileSync('frontend/public/data/nord.json', 'utf-8'));

console.log('\n=== CATEGORIZATION VALIDATION ===');
const spectrumCounts = {};

products.forEach(p => {
  const spectrum = mapCategoryToSpectrum(p.category || '');
  spectrumCounts[spectrum] = (spectrumCounts[spectrum] || 0) + 1;
});

console.log('\nNord products by spectrum:');
Object.entries(spectrumCounts).forEach(([spectrum, count]) => {
  console.log(`  ${spectrum}: ${count} products`);
});

// Test all brands
console.log('\n=== ALL BRANDS ===');
const allSpectra = {};
['nord', 'roland', 'moog', 'shure', 'rode', 'universal-audio', 'drumdots'].forEach(brand => {
  try {
    const brandProducts = JSON.parse(fs.readFileSync(`frontend/public/data/${brand}.json`, 'utf-8'));
    brandProducts.forEach(p => {
      const spectrum = mapCategoryToSpectrum(p.category || '');
      allSpectra[spectrum] = (allSpectra[spectrum] || 0) + 1;
    });
  } catch (e) {
    console.log(`Error reading ${brand}: ${e.message}`);
  }
});

console.log('\nTotal distribution:');
Object.entries(allSpectra).sort((a, b) => b[1] - a[1]).forEach(([spectrum, count]) => {
  console.log(`  ${spectrum}: ${count} products`);
});
