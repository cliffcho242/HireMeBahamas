#!/usr/bin/env node
/**
 * Full production-proof deploy script
 * Update frontend API files
 * Normalize VITE_API_BASE_URL
 * Set env variable on Vercel
 * Redeploy frontend
 * Check backend CORS for required domains
 */
const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

let fetchImpl = globalThis.fetch;
if (!fetchImpl) {
  try {
    fetchImpl = require("node-fetch");
  } catch (err) {
    console.warn(
      "⚠️ node-fetch@2 is not installed; CORS verification will be skipped."
    );
  }
}

const files = [
  path.join(__dirname, "frontend", "src", "lib", "api.ts"),
  path.join(__dirname, "admin-panel", "src", "lib", "apiUrl.ts"),
];

const replacement = `/**
 * Robust API base URL getter
 *
 * Priority:
 * 1. VITE_API_URL when pointing to localhost (for dev overrides)
 * 2. VITE_API_BASE_URL (production)
 * 3. Same-origin fallback (Vercel proxy)
 */
export function getApiBaseUrl(): string {
  const baseUrl = import.meta.env.VITE_API_BASE_URL?.trim();
  const overrideUrl = import.meta.env.VITE_API_URL?.trim();

  const normalize = (url: string) => url.replace(/\\/+$/, ""); // remove trailing slash

  // Dev override for localhost (HTTP allowed)
  if (overrideUrl && overrideUrl.startsWith("http://localhost")) {
    return normalize(overrideUrl);
  }

  // Production environment variable has priority
  if (baseUrl) {
    return normalize(baseUrl);
  }

  // Default fallback: same-origin (Vercel proxy)
  return "";
}

/**
 * Helper to build full endpoint URLs safely
 * Example:
 *   const url = buildApiUrl("/api/auth/login");
 */
export function buildApiUrl(path: string): string {
  const base = getApiBaseUrl();
  if (!path.startsWith("/")) {
    path = "/" + path;
  }
  return \`\${base}\${path}\`;
}

// Backward compatibility for existing imports
export const apiUrl = buildApiUrl;
export const getApiBase = getApiBaseUrl;
export function isApiConfigured(): boolean {
  const base = getApiBaseUrl();
  if (!base) return true; // same-origin fallback
  return (
    base.startsWith("https://") ||
    base.startsWith("http://localhost")
  );
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

const envVar =
  process.env.VITE_API_BASE_URL || "https://hiremebahamas-backend.onrender.com";
const normalized = envVar.trim().replace(/\/+$/, "");
console.log(`🔹 Normalized VITE_API_BASE_URL: ${normalized}`);

try {
  console.log("🔹 Setting VITE_API_BASE_URL on Vercel...");
  execSync("vercel env add VITE_API_BASE_URL production --yes", {
    stdio: ["pipe", "inherit", "inherit"],
    input: normalized,
  });
  console.log("✅ VITE_API_BASE_URL set on Vercel (Production)");
} catch (err) {
  console.warn(
    "⚠️ Failed to set Vercel env variable. Make sure Vercel CLI is installed and logged in."
  );
}

try {
  console.log("🔹 Redeploying frontend...");
  execSync("vercel --prod --confirm", { stdio: "inherit" });
  console.log("🎉 Frontend redeployed successfully!");
} catch (err) {
  console.error(
    "❌ Frontend redeploy failed. Check Vercel CLI login and project directory."
  );
}

(async () => {
  if (!fetchImpl) {
    console.warn("⚠️ Skipping CORS verification (fetch unavailable).");
    return;
  }

  if (!normalized) {
    console.warn(
      "⚠️ Skipping CORS verification because VITE_API_BASE_URL is empty."
    );
    return;
  }

  const corsCheckUrl = `${normalized}/openapi.json`;
  console.log("🔹 Checking backend CORS...");

  try {
    const res = await fetchImpl(corsCheckUrl, { method: "OPTIONS" });
    const allowOrigins = res.headers.get("access-control-allow-origin");

    if (!allowOrigins) {
      console.warn("⚠️ CORS header missing. Safari and iOS may block requests.");
      return;
    }

    const required = [
      "https://hiremebahamas.com",
      "https://www.hiremebahamas.com",
    ];

    required.forEach((domain) => {
      if (!allowOrigins.includes(domain)) {
        console.warn(`⚠️ Backend CORS missing domain: ${domain}`);
      }
    });

    console.log(`✅ CORS verified: ${allowOrigins}`);
  } catch (err) {
    console.warn("⚠️ Could not verify backend CORS. Check if backend is reachable.");
  }
})();
