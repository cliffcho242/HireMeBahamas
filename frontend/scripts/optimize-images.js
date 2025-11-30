#!/usr/bin/env node

/**
 * Image Optimization Script for HireMeBahamas
 * 
 * This script:
 * 1. Generates WebP versions of all PNG/JPG images for better compression
 * 2. Compresses existing images to reduce file size
 * 3. Reports size savings
 * 
 * Usage: node scripts/optimize-images.js
 * 
 * Requirements: npm install sharp (dev dependency - already installed)
 */

import sharp from 'sharp';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const publicDir = path.resolve(__dirname, '../public');

// Configuration for image optimization
const CONFIG = {
  webpQuality: 85,       // WebP quality (0-100)
  pngCompressionLevel: 9, // PNG compression level (0-9)
  jpegQuality: 85,       // JPEG quality (0-100)
  avifQuality: 80,       // AVIF quality (0-100)
  minFileSizeForWebp: 1024, // Only create WebP for files > 1KB
  pngPaletteThreshold: 256, // Use palette mode for images <= this size (width/height)
  useMozjpeg: true,      // Use mozjpeg for better JPEG compression
};

/**
 * Get all image files from a directory recursively
 */
function getImageFiles(dir, fileList = []) {
  const files = fs.readdirSync(dir);
  
  for (const file of files) {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    
    if (stat.isDirectory()) {
      getImageFiles(filePath, fileList);
    } else if (/\.(png|jpg|jpeg)$/i.test(file)) {
      fileList.push(filePath);
    }
  }
  
  return fileList;
}

/**
 * Get file size in a human-readable format
 */
function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}

/**
 * Optimize a single image
 */
async function optimizeImage(imagePath) {
  const ext = path.extname(imagePath).toLowerCase();
  const originalSize = fs.statSync(imagePath).size;
  const results = { originalSize, webpSaved: 0, optimizedSaved: 0 };
  
  // Skip very small files (icons etc.)
  if (originalSize < CONFIG.minFileSizeForWebp) {
    return { ...results, skipped: true };
  }
  
  try {
    const image = sharp(imagePath);
    const metadata = await image.metadata();
    
    // Generate WebP version
    const webpPath = imagePath.replace(/\.(png|jpg|jpeg)$/i, '.webp');
    if (!fs.existsSync(webpPath)) {
      await image
        .webp({ quality: CONFIG.webpQuality, effort: 6 })
        .toFile(webpPath);
      
      const webpSize = fs.statSync(webpPath).size;
      results.webpSaved = originalSize - webpSize;
      results.webpPath = webpPath;
      results.webpSize = webpSize;
    }
    
    // Optimize original file in-place
    if (ext === '.png') {
      // Optimize PNG
      const tempPath = imagePath + '.tmp';
      await sharp(imagePath)
        .png({ 
          compressionLevel: CONFIG.pngCompressionLevel,
          palette: metadata.width <= CONFIG.pngPaletteThreshold && metadata.height <= CONFIG.pngPaletteThreshold
        })
        .toFile(tempPath);
      
      const newSize = fs.statSync(tempPath).size;
      if (newSize < originalSize) {
        fs.renameSync(tempPath, imagePath);
        results.optimizedSaved = originalSize - newSize;
      } else {
        fs.unlinkSync(tempPath);
      }
    } else if (ext === '.jpg' || ext === '.jpeg') {
      // Optimize JPEG
      const tempPath = imagePath + '.tmp';
      await sharp(imagePath)
        .jpeg({ quality: CONFIG.jpegQuality, mozjpeg: CONFIG.useMozjpeg })
        .toFile(tempPath);
      
      const newSize = fs.statSync(tempPath).size;
      if (newSize < originalSize) {
        fs.renameSync(tempPath, imagePath);
        results.optimizedSaved = originalSize - newSize;
      } else {
        fs.unlinkSync(tempPath);
      }
    }
    
    return results;
  } catch (err) {
    console.error(`  ⚠️  Error processing ${path.basename(imagePath)}: ${err.message}`);
    return { ...results, error: err.message };
  }
}

async function main() {
  console.log('🖼️  Image Optimization Script for HireMeBahamas\n');
  console.log(`Configuration:`);
  console.log(`  - WebP Quality: ${CONFIG.webpQuality}%`);
  console.log(`  - PNG Compression: Level ${CONFIG.pngCompressionLevel}`);
  console.log(`  - JPEG Quality: ${CONFIG.jpegQuality}%`);
  console.log(`  - Min file size for WebP: ${formatBytes(CONFIG.minFileSizeForWebp)}\n`);
  
  // Find all images
  console.log('🔍 Scanning for images...');
  const imageFiles = getImageFiles(publicDir);
  console.log(`  Found ${imageFiles.length} images to process\n`);
  
  if (imageFiles.length === 0) {
    console.log('No images found to optimize.');
    return;
  }
  
  // Process each image
  console.log('⚙️  Optimizing images...\n');
  let totalOriginalSize = 0;
  let totalWebpSaved = 0;
  let totalOptimizedSaved = 0;
  let processedCount = 0;
  let skippedCount = 0;
  let webpCreatedCount = 0;
  
  for (const imagePath of imageFiles) {
    const relativePath = path.relative(publicDir, imagePath);
    process.stdout.write(`  Processing ${relativePath}... `);
    
    const result = await optimizeImage(imagePath);
    totalOriginalSize += result.originalSize;
    
    if (result.skipped) {
      console.log('⏭️  (skipped - too small)');
      skippedCount++;
      continue;
    }
    
    if (result.error) {
      console.log('❌ (error)');
      continue;
    }
    
    processedCount++;
    
    const savings = [];
    if (result.webpPath) {
      webpCreatedCount++;
      totalWebpSaved += result.webpSaved;
      savings.push(`WebP: ${formatBytes(result.webpSize)}`);
    }
    if (result.optimizedSaved > 0) {
      totalOptimizedSaved += result.optimizedSaved;
      savings.push(`Optimized: -${formatBytes(result.optimizedSaved)}`);
    }
    
    if (savings.length > 0) {
      console.log(`✅ ${savings.join(', ')}`);
    } else {
      console.log('✅ (already optimal)');
    }
  }
  
  // Summary
  console.log('\n' + '='.repeat(60));
  console.log('📊 OPTIMIZATION SUMMARY');
  console.log('='.repeat(60));
  console.log(`\nImages processed: ${processedCount}`);
  console.log(`Images skipped: ${skippedCount}`);
  console.log(`WebP versions created: ${webpCreatedCount}`);
  console.log(`\nOriginal total size: ${formatBytes(totalOriginalSize)}`);
  console.log(`WebP savings: ${formatBytes(totalWebpSaved)} (${((totalWebpSaved / totalOriginalSize) * 100).toFixed(1)}%)`);
  console.log(`PNG/JPEG optimization: ${formatBytes(totalOptimizedSaved)} (${((totalOptimizedSaved / totalOriginalSize) * 100).toFixed(1)}%)`);
  console.log(`\n✅ Total savings: ${formatBytes(totalWebpSaved + totalOptimizedSaved)}`);
  console.log('\n💡 WebP images can be served to supporting browsers for faster loading!');
  console.log('   Use the <picture> element or server content negotiation for best results.');
}

// Run the script
main().catch(err => {
  console.error('❌ Error:', err);
  process.exit(1);
});
