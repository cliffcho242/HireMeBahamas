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
const { execSync, spawnSync } = require("child_process");

let fetchImpl =
  typeof globalThis.fetch === "function" ? globalThis.fetch : null;
if (!fetchImpl) {
  try {
    fetchImpl = require("node-fetch");
  } catch (err) {
    fetchImpl = null;
    console.warn(
      "⚠️ node-fetch@2 is not installed; install it with `npm install node-fetch@2` or use Node 18+ for built-in fetch. CORS verification will be skipped."
    );
  }
}

const API_FILE_TARGETS = [
  path.join(__dirname, "frontend", "src", "lib", "api.ts"),
  path.join(__dirname, "admin-panel", "src", "lib", "apiUrl.ts"),
];

const CORS_CHECK_PATH = "/openapi.json";

const API_REPLACEMENT_CONTENT = `/**
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

  const normalize = (url: string) => url.replace(/\/+$/, ""); // remove trailing slash

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
  return base + path;
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
API_FILE_TARGETS.forEach((file) => {
  if (fs.existsSync(file)) {
    fs.writeFileSync(file, API_REPLACEMENT_CONTENT, "utf8");
    console.log(`✅ Updated: ${file}`);
  } else {
    console.warn(`⚠️ File not found: ${file}`);
  }
});

const envVar =
  process.env.VITE_API_BASE_URL || "https://hiremebahamas-backend.onrender.com";
const envVarTrimmed = envVar.trim();
const normalized = envVarTrimmed.replace(/\/+$/, "");
console.log(`🔹 Normalized VITE_API_BASE_URL: ${normalized}`);

try {
  console.log("🔹 Setting VITE_API_BASE_URL on Vercel...");
  const result = spawnSync(
    "vercel",
    ["env", "add", "VITE_API_BASE_URL", "production", "--yes"],
    {
      stdio: ["pipe", "pipe", "pipe"],
      input: `${normalized}\n`,
      encoding: "utf-8",
    }
  );

  const combinedOutput = `${result.stdout || ""}${result.stderr || ""}`;

  if (result.status === 0) {
    if (combinedOutput.trim()) {
      process.stdout.write(combinedOutput);
    }
    console.log("✅ VITE_API_BASE_URL set on Vercel (Production)");
  } else if (combinedOutput.toLowerCase().includes("already exists")) {
    console.log("ℹ️ VITE_API_BASE_URL already exists on Vercel. Skipping creation.");
  } else {
    const reason =
      result.error ||
      new Error(
        `vercel env add VITE_API_BASE_URL failed: ${
          combinedOutput || `exit code ${result.status}`
        }`
      );
    throw reason;
  }
} catch (err) {
  console.warn(
    `⚠️ Failed to set Vercel env variable. Make sure Vercel CLI is installed and logged in. ${err?.message || err}`
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

  if (!envVarTrimmed) {
    console.warn(
      "⚠️ Skipping CORS verification because VITE_API_BASE_URL is empty."
    );
    return;
  }

  const corsCheckUrl = `${normalized}${CORS_CHECK_PATH}`;
  console.log("🔹 Checking backend CORS...");

  try {
    const required = [
      "https://hiremebahamas.com",
      "https://www.hiremebahamas.com",
    ];

    const res = await fetchImpl(corsCheckUrl, {
      method: "OPTIONS",
      headers: {
        Origin: required[0],
        "Access-Control-Request-Method": "GET",
      },
    });
    const allowOrigins = res.headers.get("access-control-allow-origin");

    if (!allowOrigins) {
      console.warn("⚠️ CORS header missing. Safari and iOS may block requests.");
      return;
    }

    const allowList = allowOrigins
      .split(",")
      .map((origin) => origin.trim())
      .filter(Boolean);
    const hasWildcard = allowList.includes("*");

    required.forEach((domain) => {
      if (!hasWildcard && !allowList.includes(domain)) {
        console.warn(
          `⚠️ Backend CORS missing domain: ${domain}. Add this origin to your backend CORS allowlist.`
        );
      }
    });

    console.log(`✅ CORS verified: ${allowOrigins}`);
  } catch (err) {
    console.warn("⚠️ Could not verify backend CORS. Check if backend is reachable.");
  }
})();
