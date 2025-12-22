#!/usr/bin/env node
/**
 * Full production-proof deploy script
 *
 * 1. Update frontend API files
 * 2. Normalize VITE_API_BASE_URL
 * 3. Set env variable on Vercel
 * 4. Redeploy frontend
 * 5. Check backend CORS for required domains
 */

const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");
const fetch = global.fetch || require("node-fetch"); // fallback for Node <18

// Files to replace
const files = [
  path.join(__dirname, "frontend/src/lib/api.ts"),
  path.join(__dirname, "admin-panel/src/lib/apiUrl.ts"),
];

// Replacement content
const replacement = `/**
 * Robust API base URL getter
 */
export function getApiBaseUrl(): string {
  const baseUrl = import.meta.env.VITE_API_BASE_URL?.trim();
  const overrideUrl = import.meta.env.VITE_API_URL?.trim();
  const normalize = (url: string) => url.replace(/\/+$/, "");

  if (overrideUrl && overrideUrl.startsWith("http://localhost")) return normalize(overrideUrl);
  if (baseUrl) return normalize(baseUrl);
  return "";
}

export function buildApiUrl(path: string): string {
  const base = getApiBaseUrl();
  if (!path.startsWith("/")) path = "/" + path;
  return \`\${base}\${path}\`;
}
`;

console.log("🔹 Updating frontend API files...");
files.forEach((file) => {
  if (fs.existsSync(file)) {
    fs.writeFileSync(file, replacement, "utf8");
    console.log(\`✅ Updated: \${file}\`);
  } else {
    console.warn(\`⚠️ File not found: \${file}\`);
  }
});

// Normalize VITE_API_BASE_URL
const envVar = process.env.VITE_API_BASE_URL || "https://hiremebahamas-backend.onrender.com";
const normalized = envVar.replace(/\/+$/, "");
console.log(\`🔹 Normalized VITE_API_BASE_URL: \${normalized}\`);

// Set Vercel environment variable
try {
  console.log("🔹 Setting VITE_API_BASE_URL on Vercel...");
  execSync(\`vercel env add VITE_API_BASE_URL \${normalized} production --yes\`, { stdio: "inherit" });
  console.log("✅ VITE_API_BASE_URL set on Vercel (Production)");
} catch (err) {
  console.warn("⚠️ Failed to set Vercel env variable. Make sure Vercel CLI is installed and logged in.");
}

// Redeploy frontend
try {
  console.log("🔹 Redeploying frontend...");
  execSync("vercel --prod --confirm", { stdio: "inherit" });
  console.log("🎉 Frontend redeployed successfully!");
} catch (err) {
  console.error("❌ Frontend redeploy failed. Check Vercel CLI login and project directory.");
}

// CORS verification
(async () => {
  const corsCheckUrl = `${normalized}/openapi.json`; // FastAPI exposes OpenAPI by default
  console.log("🔹 Checking backend CORS...");
  try {
    const res = await fetch(corsCheckUrl, { method: "OPTIONS" });
    const allowOrigins = res.headers.get("access-control-allow-origin");
    if (!allowOrigins) {
      console.warn("⚠️ CORS header missing. Safari and iOS may block requests.");
    } else {
      const required = ["https://hiremebahamas.com", "https://www.hiremebahamas.com"];
      required.forEach((domain) => {
        if (!allowOrigins.includes(domain)) {
          console.warn(\`⚠️ Backend CORS missing domain: \${domain}\`);
        }
      });
      console.log(\`✅ CORS verified: \${allowOrigins}\`);
    }
  } catch (err) {
    console.warn("⚠️ Could not verify backend CORS. Check if backend is reachable.");
  }
})();
