#!/usr/bin/env node
/**
 * Full production-proof deploy script with health check
 *
 * Features:
 * 1. Updates frontend API files (api.ts & apiUrl.ts)
 * 2. Normalizes VITE_API_BASE_URL / VITE_API_URL
 * 3. Sets env variable on Vercel (production)
 * 4. Redeploys frontend (production only)
 * 5. Verifies backend CORS for production domains
 * 6. Performs post-deploy health check on backend
 */

const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

const DEV_DEFAULT_API = "http://localhost:5173";
const PROD_DEFAULT_API = "https://hiremebahamas-backend.onrender.com";
const REQUIRED_CORS_DOMAINS = ["https://hiremebahamas.com", "https://www.hiremebahamas.com"];

const getFetch = () => {
  if (typeof fetch === "function") return fetch;
  try {
    return require("node-fetch");
  } catch (err) {
    console.error("❌ node-fetch@2 is required when running on Node <18. Install with: npm install node-fetch@2");
    process.exit(1);
  }
};

const fetchFn = getFetch();
let hasError = false;

// Files to replace
const files = [
  path.join(__dirname, "frontend/src/lib/api.ts"),
  path.join(__dirname, "admin-panel/src/lib/apiUrl.ts"),
];

// Replacement content
const replacement = `/**
 * Robust API base URL getter
 * 
 * Priority:
 * 1. VITE_API_URL when pointing to localhost (dev override)
 * 2. VITE_API_BASE_URL (production)
 * 3. Same-origin fallback (Vercel proxy)
 */
export function getApiBaseUrl(): string {
  const baseUrl = import.meta.env.VITE_API_BASE_URL?.trim();
  const overrideUrl = import.meta.env.VITE_API_URL?.trim();

  const normalize = (url: string) => url.replace(/\/+$/, "");

  // Dev override for localhost (HTTP allowed)
  if (overrideUrl && overrideUrl.startsWith("http://localhost")) {
    return normalize(overrideUrl);
  }

  // Production environment variable has priority
  if (baseUrl) {
    if (!baseUrl.startsWith("https://")) {
      console.warn(
        \`[getApiBaseUrl] Warning: VITE_API_BASE_URL must be HTTPS in production: \${baseUrl}\`
      );
    }
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
  ? process.env.VITE_API_URL || DEV_DEFAULT_API
  : process.env.VITE_API_BASE_URL || PROD_DEFAULT_API;

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
    if (err instanceof Error) {
      console.warn(\`⚠️ Details: \${err.message}\`);
    }
    hasError = true;
  }
}

// Step 5: Redeploy frontend (production only)
if (!isLocal) {
  try {
    console.log("🔹 Redeploying frontend...");
    execSync("vercel --prod --confirm", { stdio: "inherit" });
    console.log("🎉 Frontend redeployed successfully!");
  } catch (err) {
    console.error("❌ Frontend redeploy failed. Ensure Vercel CLI is installed, you're logged in, and running from the correct project directory.");
    if (err instanceof Error) {
      console.error(\`❌ Details: \${err.message}\`);
    }
    hasError = true;
  }
}

// Step 6: Verify backend CORS (production only)
if (!isLocal) {
  const runPostDeployChecks = async () => {
    console.log("🔹 Checking backend CORS...");
    try {
      const corsCheckUrl = \`\${normalized}/openapi.json\`;
      const res = await fetchFn(corsCheckUrl, { method: "OPTIONS" });
      const allowOrigins = res.headers.get("access-control-allow-origin");
      if (!allowOrigins) {
        console.warn("⚠️ CORS header missing. Safari and iOS may block requests.");
      } else {
        REQUIRED_CORS_DOMAINS.forEach((domain) => {
          if (!allowOrigins.includes(domain)) {
            console.warn(\`⚠️ Backend CORS missing domain: \${domain}\`);
          }
        });
        console.log(\`✅ CORS verified: \${allowOrigins}\`);
      }
    } catch (err) {
      console.warn("⚠️ Could not verify backend CORS. Check if backend is reachable.");
      if (err instanceof Error) {
        console.warn(\`⚠️ Details: \${err.message}\`);
      }
      hasError = true;
    }

    // Step 7: Post-deploy health check
    console.log("🔹 Performing backend health check...");
    const healthUrl = \`\${normalized}/health\`;
    try {
      const healthRes = await fetchFn(healthUrl);
      if (healthRes.ok) {
        console.log(\`✅ Backend health check passed: \${healthRes.status} \${healthRes.statusText}\`);
      } else {
        console.warn(\`⚠️ Backend health check failed: \${healthRes.status} \${healthRes.statusText}\`);
        hasError = true;
      }
    } catch (err) {
      console.error(\`❌ Backend health check failed: \${err instanceof Error ? err.message : err}\`);
      hasError = true;
    }
  };

  runPostDeployChecks()
    .catch((err) => {
      console.error(\`❌ Post-deploy checks failed: \${err instanceof Error ? err.message : err}\`);
      hasError = true;
    })
    .finally(() => {
      if (hasError) process.exit(1);
    });
}
