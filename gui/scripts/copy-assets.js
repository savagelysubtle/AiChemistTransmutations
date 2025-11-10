// Pre-build script to ensure all necessary assets are in public directory
const fs = require('fs');
const path = require('path');

console.log('📦 Copying assets to public directory...');

const assetsDir = path.join(__dirname, '..', 'assets');
const publicAssetsDir = path.join(__dirname, '..', 'public', 'assets');

// Ensure public/assets exists
if (!fs.existsSync(publicAssetsDir)) {
  fs.mkdirSync(publicAssetsDir, { recursive: true });
}

// Assets to copy
const assetsToCopy = [
  'icon-256x256.png',
  'icon-512x512.png',
  'favicon-32x32.png',
  'favicon-16x16.png',
  'favicon.svg',
  'icon.svg',
  'logo.svg',
];

let copiedCount = 0;
let errorCount = 0;

assetsToCopy.forEach((asset) => {
  const src = path.join(assetsDir, asset);
  const dest = path.join(publicAssetsDir, asset);

  try {
    if (fs.existsSync(src)) {
      fs.copyFileSync(src, dest);
      console.log(`  ✓ Copied: ${asset}`);
      copiedCount++;
    } else {
      console.warn(`  ⚠ Missing: ${asset}`);
    }
  } catch (error) {
    console.error(`  ✗ Error copying ${asset}:`, error.message);
    errorCount++;
  }
});

console.log('');
console.log(`✅ Assets copied: ${copiedCount}`);
if (errorCount > 0) {
  console.log(`❌ Errors: ${errorCount}`);
  process.exit(1);
}
console.log('');
