#!/usr/bin/env node
/**
 * SEO Validation Script
 * Validates that all required SEO elements are present in index.html
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// ANSI color codes
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  blue: '\x1b[34m',
  bold: '\x1b[1m'
};

// Required SEO elements
const requiredElements = {
  'Basic Meta Tags': [
    { name: 'charset', pattern: /<meta charset="UTF-8"/, required: true },
    { name: 'viewport', pattern: /<meta\s+name="viewport"/, required: true },
    { name: 'description', pattern: /<meta\s+name="description"/, required: true },
    { name: 'keywords', pattern: /<meta\s+name="keywords"/, required: true },
    { name: 'author', pattern: /<meta\s+name="author"/, required: true },
    { name: 'title', pattern: /<title>.*<\/title>/, required: true }
  ],
  'Open Graph': [
    { name: 'og:title', pattern: /<meta\s+property="og:title"/, required: true },
    { name: 'og:description', pattern: /<meta\s+property="og:description"/, required: true },
    { name: 'og:type', pattern: /<meta\s+property="og:type"/, required: true },
    { name: 'og:url', pattern: /<meta\s+property="og:url"/, required: true },
    { name: 'og:image', pattern: /<meta\s+property="og:image"/, required: true },
    { name: 'og:site_name', pattern: /<meta\s+property="og:site_name"/, required: false }
  ],
  'Twitter Card': [
    { name: 'twitter:card', pattern: /<meta\s+name="twitter:card"/, required: true },
    { name: 'twitter:title', pattern: /<meta\s+name="twitter:title"/, required: true },
    { name: 'twitter:description', pattern: /<meta\s+name="twitter:description"/, required: true },
    { name: 'twitter:image', pattern: /<meta\s+name="twitter:image"/, required: true }
  ],
  'Structured Data': [
    { name: 'JSON-LD Schema', pattern: /<script type="application\/ld\+json">/, required: true }
  ],
  'Resources': [
    { name: 'Canonical URL', pattern: /<link rel="canonical"/, required: true },
    { name: 'Favicon', pattern: /<link rel="icon"/, required: true },
    { name: 'Manifest', pattern: /<link rel="manifest"/, required: true },
    { name: 'Sitemap Reference', pattern: /sitemap\.xml/, required: false }
  ],
  'Performance': [
    { name: 'DNS Prefetch', pattern: /<link rel="dns-prefetch"/, required: false },
    { name: 'Preconnect', pattern: /<link rel="preconnect"/, required: false },
    { name: 'Preload', pattern: /<link rel="preload"/, required: false }
  ]
};

function validateSEO() {
  console.log(`\n${colors.bold}${colors.blue}🔍 SEO Validation Report${colors.reset}\n`);

  const indexPath = path.join(__dirname, '..', 'index.html');
  
  if (!fs.existsSync(indexPath)) {
    console.error(`${colors.red}❌ Error: index.html not found at ${indexPath}${colors.reset}`);
    return false;
  }

  const html = fs.readFileSync(indexPath, 'utf8');
  
  let allPassed = true;
  let totalChecks = 0;
  let passedChecks = 0;
  let warnings = [];

  // Check each category
  Object.entries(requiredElements).forEach(([category, elements]) => {
    console.log(`${colors.bold}${category}:${colors.reset}`);
    
    elements.forEach(({ name, pattern, required }) => {
      totalChecks++;
      const found = pattern.test(html);
      
      if (found) {
        passedChecks++;
        console.log(`  ${colors.green}✓${colors.reset} ${name}`);
      } else if (required) {
        allPassed = false;
        console.log(`  ${colors.red}✗${colors.reset} ${name} ${colors.red}(REQUIRED)${colors.reset}`);
      } else {
        warnings.push(name);
        console.log(`  ${colors.yellow}⚠${colors.reset} ${name} ${colors.yellow}(recommended)${colors.reset}`);
      }
    });
    
    console.log('');
  });

  // Summary
  console.log(`${colors.bold}Summary:${colors.reset}`);
  console.log(`  Checks passed: ${passedChecks}/${totalChecks}`);
  console.log(`  Success rate: ${Math.round((passedChecks / totalChecks) * 100)}%`);

  if (warnings.length > 0) {
    console.log(`\n${colors.yellow}⚠️  Recommendations:${colors.reset}`);
    warnings.forEach(w => {
      console.log(`  - Consider adding: ${w}`);
    });
  }

  // Additional validations
  console.log(`\n${colors.bold}Additional Checks:${colors.reset}`);
  
  // Check for multiple h1 tags (should only have one)
  const h1Count = (html.match(/<h1/g) || []).length;
  if (h1Count === 0) {
    console.log(`  ${colors.yellow}⚠${colors.reset} No <h1> tag found (recommended for SEO)`);
  } else if (h1Count > 1) {
    console.log(`  ${colors.yellow}⚠${colors.reset} Multiple <h1> tags found (${h1Count}). Recommended: 1`);
  } else {
    console.log(`  ${colors.green}✓${colors.reset} Single <h1> tag found`);
  }

  // Check for proper image alt attributes (in HTML, not dynamic content)
  const imgTags = html.match(/<img[^>]*>/g) || [];
  const imgsWithoutAlt = imgTags.filter(img => !img.includes('alt=')).length;
  if (imgsWithoutAlt > 0) {
    console.log(`  ${colors.yellow}⚠${colors.reset} ${imgsWithoutAlt} image(s) without alt attribute`);
  } else if (imgTags.length > 0) {
    console.log(`  ${colors.green}✓${colors.reset} All ${imgTags.length} images have alt attributes`);
  }

  // Check for lang attribute
  if (html.includes('<html lang=')) {
    console.log(`  ${colors.green}✓${colors.reset} HTML lang attribute present`);
  } else {
    console.log(`  ${colors.yellow}⚠${colors.reset} HTML lang attribute missing`);
  }

  // Check structured data validity
  const jsonLdMatches = html.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g);
  if (jsonLdMatches) {
    console.log(`  ${colors.green}✓${colors.reset} ${jsonLdMatches.length} JSON-LD schema(s) found`);
    
    // Try to parse each JSON-LD
    let validJsonLd = 0;
    jsonLdMatches.forEach((match, index) => {
      const jsonContent = match.replace(/<script type="application\/ld\+json">|<\/script>/g, '').trim();
      try {
        JSON.parse(jsonContent);
        validJsonLd++;
      } catch (e) {
        console.log(`  ${colors.red}✗${colors.reset} JSON-LD #${index + 1} has invalid JSON syntax`);
        allPassed = false;
      }
    });
    
    if (validJsonLd === jsonLdMatches.length) {
      console.log(`  ${colors.green}✓${colors.reset} All JSON-LD schemas are valid`);
    }
  }

  console.log('');

  if (allPassed && warnings.length === 0) {
    console.log(`${colors.green}${colors.bold}✅ All SEO checks passed!${colors.reset}\n`);
  } else if (allPassed) {
    console.log(`${colors.yellow}${colors.bold}⚠️  SEO validation passed with recommendations${colors.reset}\n`);
  } else {
    console.log(`${colors.red}${colors.bold}❌ SEO validation failed${colors.reset}\n`);
  }

  return allPassed;
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const success = validateSEO();
  process.exit(success ? 0 : 1);
}

export { validateSEO };
