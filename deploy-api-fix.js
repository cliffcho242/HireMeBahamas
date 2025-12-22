#!/usr/bin/env node
/**
 * One-command frontend fix & redeploy
 * - Replaces api.ts and apiUrl.ts with a robust API URL handler
 * - Normalizes VITE_API_BASE_URL (removes trailing slash)
 * - Redeploys Vercel frontend
 */

const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

// List of frontend API files to replace
const files = [
  path.join(__dirname, "frontend/src/lib/api.ts"),
  path.join(__dirname, "admin-panel/src/lib/apiUrl.ts"),
];

const replacement = `/**

Robust API base URL getter
Priority:
VITE_API_BASE_URL (production)
VITE_API_URL (dev override; HTTP allowed only for localhost)
Same-origin fallback (Vercel proxy) */
export function getApiBaseUrl(): string {
  const baseUrl = import.meta.env.VITE_API_BASE_URL?.trim();
  const overrideUrl = import.meta.env.VITE_API_URL?.trim();

  const normalize = (url: string) => url.replace(/\\/+$/, "");

  if (overrideUrl && overrideUrl.startsWith("http://localhost")) {
    return normalize(overrideUrl);
  }
  if (baseUrl) {
    return normalize(baseUrl);
  }

  return "";
}

export function buildApiUrl(path: string): string {
  const base = getApiBaseUrl();
  if (!path.startsWith("/")) {
    path = "/" + path;
  }
  return \`${"${base}${path}"}\`;
}
`;

console.log("🔹 Updating frontend API files...");

files.forEach((file) => {
  if (fs.existsSync(file)) {
    fs.writeFileSync(file, replacement, "utf8");
    console.log(`✅ Updated: ${file}`);
  } else {
    console.warn(`⚠️ File not found: ${file}`);
  }
});

// Normalize VITE_API_BASE_URL for Vercel
console.log("\n🔹 Normalizing VITE_API_BASE_URL for Vercel...");
const envVar =
  process.env.VITE_API_BASE_URL || "https://hiremebahamas-backend.onrender.com";
const normalized = envVar.replace(/\\/+$/, "");
console.log(`✅ Using: ${normalized}`);

// Optional: set via Vercel CLI
try {
  console.log("\n🔹 Setting Vercel environment variable...");
  execSync(`vercel env add VITE_API_BASE_URL ${normalized} production --yes`, {
    stdio: "inherit",
  });
  console.log("✅ VITE_API_BASE_URL set on Vercel (Production)");
} catch (err) {
  console.warn(
    "⚠️ Vercel CLI env set failed. Make sure Vercel CLI is installed and logged in."
  );
}

// Redeploy frontend
try {
  console.log("\n🔹 Deploying frontend to Vercel...");
  execSync("vercel --prod --confirm", { stdio: "inherit" });
  console.log("🎉 Frontend redeployed successfully!");
} catch (err) {
  console.error(
    "❌ Frontend redeploy failed. Check Vercel CLI login and project directory."
  );
}
