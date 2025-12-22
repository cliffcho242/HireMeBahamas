#!/usr/bin/env node

/**
 * Full production-proof deploy script
 * - Update frontend API files
 * - Normalize VITE_API_BASE_URL
 * - Set the env variable on Vercel
 * - Redeploy frontend
 * - Check backend CORS for required domains
 */

const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

const fetchImpl =
  typeof fetch !== "undefined"
    ? fetch
    : (() => {
        try {
          return require("node-fetch");
        } catch (err) {
          console.warn(
            "⚠️ node-fetch is not installed. Install with: npm install node-fetch@2"
          );
          return null;
        }
      })();

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

  // Dev override for localhost
  if (overrideUrl && overrideUrl.startsWith("http://localhost")) {
    return normalize(overrideUrl);
  }

  // Production variable
  if (baseUrl) {
    return normalize(baseUrl);
  }

  return "";
}

export function buildApiUrl(path: string): string {
  const base = getApiBaseUrl();
  if (!path.startsWith("/")) path = "/" + path;
  return \`\${base}\${path}\`;
}

// Backward compatibility helpers
export const apiUrl = buildApiUrl;
export const getApiBase = getApiBaseUrl;
export function isApiConfigured(): boolean {
  const base = getApiBaseUrl();
  if (!base) return false;
  return base.startsWith("https://") || base.startsWith("http://localhost");
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

// Normalize VITE_API_BASE_URL
const envVar =
  process.env.VITE_API_BASE_URL ||
  "https://hiremebahamas-backend.onrender.com";
const normalized = envVar.replace(/\/+$/, "");
console.log(`🔹 Normalized VITE_API_BASE_URL: ${normalized}`);

// Set Vercel environment variable
try {
  console.log("🔹 Setting VITE_API_BASE_URL on Vercel...");
  execSync(
    `vercel env add VITE_API_BASE_URL ${JSON.stringify(
      normalized
    )} production --yes`,
    { stdio: "inherit" }
  );
  console.log("✅ VITE_API_BASE_URL set on Vercel (Production)");
} catch (err) {
  console.warn(
    "⚠️ Failed to set Vercel env variable. Make sure Vercel CLI is installed and logged in."
  );
}

// Redeploy frontend
try {
  console.log("🔹 Redeploying frontend...");
  execSync("vercel --prod --confirm", { stdio: "inherit" });
  console.log("🎉 Frontend redeployed successfully!");
} catch (err) {
  console.error(
    "❌ Frontend redeploy failed. Check Vercel CLI login and project directory."
  );
}

// CORS verification
(async () => {
  if (!fetchImpl) {
    console.warn(
      "⚠️ Skipping CORS verification because fetch is unavailable. Install node-fetch@2 if running on Node <18."
    );
    return;
  }

  const corsTargets = [
    `${normalized}/api/health`,
    `${normalized}/openapi.json`,
  ];

  console.log("🔹 Checking backend CORS...");

  for (const corsCheckUrl of corsTargets) {
    try {
      const res = await fetchImpl(corsCheckUrl, { method: "OPTIONS" });
      const allowOrigins = res.headers.get("access-control-allow-origin");

      if (!allowOrigins) {
        console.warn(
          `⚠️ CORS header missing from ${corsCheckUrl}. Safari and iOS may block requests.`
        );
        continue;
      }

      const required = [
        "https://hiremebahamas.com",
        "https://www.hiremebahamas.com",
      ];

      const allowList = allowOrigins
        .split(/[,\s]+/)
        .map((origin) => origin.trim())
        .filter(Boolean);

      const wildcard = allowList.includes("*");

      required.forEach((domain) => {
        if (!wildcard && !allowList.includes(domain)) {
          console.warn(`⚠️ Backend CORS missing domain: ${domain}`);
        }
      });

      console.log(`✅ CORS verified from ${corsCheckUrl}: ${allowOrigins}`);
      return;
    } catch (err) {
      console.warn(
        `⚠️ Could not verify backend CORS at ${corsCheckUrl}.`,
        err?.message || err
      );
    }
  }
})();
