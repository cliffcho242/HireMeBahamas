#!/usr/bin/env node
/**
 * Full dev + prod safe frontend fix & deploy
 *
 * - Auto-detects localhost vs production
 * - Updates frontend API files (api.ts & apiUrl.ts)
 * - Normalizes VITE_API_BASE_URL / VITE_API_URL
 * - Sets env variable on Vercel (production only)
 * - Redeploys frontend
 * - Verifies backend CORS for production domains
 */

const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");
const fetch = require("node-fetch"); // npm install node-fetch@2

// Files to update
const files = [
  path.join(__dirname, "frontend/src/lib/api.ts"),
  path.join(__dirname, "admin-panel/src/lib/apiUrl.ts"),
];

const replacement = `/**
 * Robust API base URL getter (dev + prod safe)
 */
export function getApiBaseUrl(): string {
  const baseUrl = import.meta.env.VITE_API_BASE_URL?.trim();
  const overrideUrl = import.meta.env.VITE_API_URL?.trim();
  const normalize = (url: string) => url.replace(/\\/+$/, "");

  // Dev override for localhost HTTP
  if (overrideUrl && overrideUrl.startsWith("http://localhost")) return normalize(overrideUrl);

  // Production
  if (baseUrl) {
    if (!baseUrl.startsWith("https://")) {
      console.warn(\`[getApiBaseUrl] Warning: VITE_API_BASE_URL must be HTTPS in production: \${baseUrl}\`);
    }
    return normalize(baseUrl);
  }

  // Fallback same-origin (Vercel proxy)
  return "";
};

export function buildApiUrl(path: string): string {
  const base = getApiBaseUrl();
  if (!path.startsWith("/")) path = "/" + path;
  return \`\${base}\${path}\`;
};
`;

// Step 1: Update frontend API files
console.log("🔹 Updating frontend API files...");
files.forEach((file) => {
  if (fs.existsSync(file)) {
    fs.writeFileSync(file, replacement, "utf8");
    console.log(\`✅ Updated: \${file}\`);
  } else {
    console.warn(\`⚠️ File not found: \${file}\`);
  }
});

// Step 2: Determine environment
const isLocal = process.env.NODE_ENV !== "production";
console.log(\`🔹 Environment: \${isLocal ? "development (localhost)" : "production"}\`);

// Step 3: Normalize API URL
const envVar = isLocal
  ? process.env.VITE_API_URL || "http://localhost:5173"
  : process.env.VITE_API_BASE_URL || "https://hiremebahamas-backend.onrender.com";

const normalized = envVar.replace(/\/+$/, "");
console.log(\`🔹 Normalized API URL: \${normalized}\`);

// Step 4: Set Vercel env variable (production only)
if (!isLocal) {
  try {
    console.log("🔹 Setting VITE_API_BASE_URL on Vercel...");
    execSync(\`vercel env add VITE_API_BASE_URL \${normalized} production --yes\`, { stdio: "inherit" });
    console.log("✅ VITE_API_BASE_URL set on Vercel (Production)");
  } catch (err) {
    console.warn("⚠️ Failed to set Vercel env variable. Make sure Vercel CLI is installed and logged in.");
  }
}

// Step 5: Redeploy frontend
if (!isLocal) {
  try {
    console.log("🔹 Redeploying frontend...");
    execSync("vercel --prod --confirm", { stdio: "inherit" });
    console.log("🎉 Frontend redeployed successfully!");
  } catch (err) {
    console.error("❌ Frontend redeploy failed. Check Vercel CLI login and project directory.");
  }
}

// Step 6: Verify backend CORS (production only)
if (!isLocal) {
  (async () => {
    const corsCheckUrl = \`\${normalized}/openapi.json\`;
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
}
