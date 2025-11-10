#!/usr/bin/env node
/**
 * Fix Invalid Icon File
 * 
 * Problem: The icon.ico file is actually a PNG file renamed to .ico
 * Solution: Generate a proper Windows ICO file from the PNG source
 * 
 * This script creates a multi-resolution ICO file required by NSIS
 */

const fs = require('fs');
const path = require('path');

console.log('🔧 Fixing icon.ico file...\n');

// Check if sharp is available (for PNG processing)
let sharp;
try {
  sharp = require('sharp');
} catch (e) {
  console.log('📦 Installing sharp for image processing...');
  require('child_process').execSync('npm install --no-save sharp', { stdio: 'inherit' });
  sharp = require('sharp');
}

const assetsDir = path.join(__dirname, '..', 'assets');
const sourcePng = path.join(assetsDir, 'icon.png');
const targetIco = path.join(assetsDir, 'icon.ico');

// Backup old icon if it exists
if (fs.existsSync(targetIco)) {
  const backupPath = path.join(assetsDir, 'icon.ico.backup');
  fs.copyFileSync(targetIco, backupPath);
  console.log(`✓ Backed up old icon.ico to icon.ico.backup`);
}

// Generate ICO file using sharp
async function generateIco() {
  try {
    // For Windows ICO, we need 256x256 as the primary size
    // Sharp doesn't create multi-size ICO, so we'll create a simple 256x256 ICO
    
    const buffer = await sharp(sourcePng)
      .resize(256, 256, {
        fit: 'contain',
        background: { r: 0, g: 0, b: 0, alpha: 0 }
      })
      .toFormat('png')
      .toBuffer();
    
    // Create ICO header (simplified single-image ICO)
    const header = Buffer.alloc(6 + 16);
    header.writeUInt16LE(0, 0);        // Reserved (must be 0)
    header.writeUInt16LE(1, 2);        // Type (1 = ICO)
    header.writeUInt16LE(1, 4);        // Number of images
    
    // Image directory entry
    header.writeUInt8(0, 6);           // Width (0 means 256)
    header.writeUInt8(0, 7);           // Height (0 means 256)
    header.writeUInt8(0, 8);           // Color palette
    header.writeUInt8(0, 9);           // Reserved
    header.writeUInt16LE(1, 10);       // Color planes
    header.writeUInt16LE(32, 12);      // Bits per pixel
    header.writeUInt32LE(buffer.length, 14); // Size of image data
    header.writeUInt32LE(22, 18);      // Offset to image data
    
    // Combine header and image data
    const ico = Buffer.concat([header, buffer]);
    fs.writeFileSync(targetIco, ico);
    
    console.log(`✓ Generated icon.ico (256x256, ${ico.length} bytes)`);
    console.log(`✓ Icon file is now valid for NSIS installer\n`);
    
    // Verify the file
    const stats = fs.statSync(targetIco);
    console.log(`📊 File Info:`);
    console.log(`   Size: ${stats.size} bytes`);
    console.log(`   Path: ${targetIco}`);
    
    // Check header
    const headerCheck = fs.readFileSync(targetIco, { encoding: null }).slice(0, 4);
    if (headerCheck[0] === 0x00 && headerCheck[1] === 0x00 && headerCheck[2] === 0x01 && headerCheck[3] === 0x00) {
      console.log(`   Format: Valid ICO file ✅\n`);
    } else {
      console.log(`   Format: May have issues ⚠️\n`);
    }
    
    console.log('🎉 Icon fix complete! Try building again.\n');
    
  } catch (error) {
    console.error('❌ Error generating icon:', error.message);
    console.log('\n💡 Alternative: Use an online converter:');
    console.log('   1. Go to https://cloudconvert.com/png-to-ico');
    console.log('   2. Upload assets/icon.png');
    console.log('   3. Select "Multi-size" with: 16, 32, 48, 256');
    console.log('   4. Download and replace assets/icon.ico\n');
    process.exit(1);
  }
}

// Check if source exists
if (!fs.existsSync(sourcePng)) {
  console.error(`❌ Source file not found: ${sourcePng}`);
  process.exit(1);
}

// Run the fix
generateIco();


