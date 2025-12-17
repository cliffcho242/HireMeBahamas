#!/usr/bin/env node
/**
 * Dynamic Sitemap Generator for HireMeBahamas
 * Generates sitemap.xml with current timestamps and route definitions
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const BASE_URL = 'https://www.hiremebahamas.com';
const TODAY = new Date().toISOString().split('T')[0];

// Define all public routes with metadata
const routes = [
  {
    path: '/',
    changefreq: 'daily',
    priority: 1.0,
    description: 'Homepage'
  },
  {
    path: '/feed',
    changefreq: 'daily',
    priority: 0.9,
    description: 'Social Feed'
  },
  {
    path: '/jobs',
    changefreq: 'daily',
    priority: 0.9,
    description: 'Job Listings'
  },
  {
    path: '/login',
    changefreq: 'monthly',
    priority: 0.8,
    description: 'Login Page'
  },
  {
    path: '/register',
    changefreq: 'monthly',
    priority: 0.8,
    description: 'Registration Page'
  },
  {
    path: '/profile',
    changefreq: 'weekly',
    priority: 0.7,
    description: 'User Profile'
  },
  {
    path: '/messages',
    changefreq: 'daily',
    priority: 0.6,
    description: 'Messages'
  },
  {
    path: '/about',
    changefreq: 'monthly',
    priority: 0.7,
    description: 'About Us'
  },
  {
    path: '/contact',
    changefreq: 'monthly',
    priority: 0.7,
    description: 'Contact Us'
  }
];

function generateSitemap() {
  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
        http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
  ${routes.map(route => `
  <!-- ${route.description} -->
  <url>
    <loc>${BASE_URL}${route.path}</loc>
    <lastmod>${TODAY}</lastmod>
    <changefreq>${route.changefreq}</changefreq>
    <priority>${route.priority}</priority>
  </url>`).join('')}

</urlset>`;

  return xml;
}

function writeSitemap() {
  try {
    const sitemapPath = path.join(__dirname, '..', 'public', 'sitemap.xml');
    const sitemap = generateSitemap();
    
    fs.writeFileSync(sitemapPath, sitemap, 'utf8');
    
    console.log('✅ Sitemap generated successfully!');
    console.log(`📄 Location: ${sitemapPath}`);
    console.log(`📅 Last modified: ${TODAY}`);
    console.log(`🔗 ${routes.length} URLs included`);
    
    return true;
  } catch (error) {
    console.error('❌ Error generating sitemap:', error);
    return false;
  }
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const success = writeSitemap();
  process.exit(success ? 0 : 1);
}

export { generateSitemap, writeSitemap, routes };
