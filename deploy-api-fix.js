#!/usr/bin/env node
/**
 * One-command frontend fix & redeploy
 *
 * - Replaces api.ts and apiUrl.ts with robust API URL handler
 * - Normalizes VITE_API_BASE_URL (removes trailing slash)
 * - Redeploys Vercel frontend
 */

const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");
// Project default backend; override via DEPLOY_API_FIX_DEFAULT_BASE_URL
const DEFAULT_API_BASE_URL =
  process.env.DEPLOY_API_FIX_DEFAULT_BASE_URL ||
  "https://hiremebahamas-backend.onrender.com";
const DEPLOY_TIMEOUT_MS = parseInt(process.env.VERCEL_DEPLOY_TIMEOUT_MS || "300000", 10);

// List of frontend API files to replace
const files = [
  path.join(__dirname, "frontend/src/lib/api.ts"),
  path.join(__dirname, "admin-panel/src/lib/apiUrl.ts"),
];

const replacement = String.raw`
/**
 * Robust API base URL getter
 *
 * Priority:
 * 1. VITE_API_BASE_URL (production)
 * 2. VITE_API_URL (dev override; HTTP allowed only for localhost)
 * 3. Same-origin fallback (Vercel proxy)
 */
export function getApiBaseUrl(): string {
  const baseUrl = import.meta.env.VITE_API_BASE_URL?.trim();
  const overrideUrl = import.meta.env.VITE_API_URL?.trim();
  const normalize = (url: string) => url.replace(/\/+$/, "");

  if (baseUrl) {
    if (!baseUrl.startsWith("https://")) {
      console.warn("[getApiBaseUrl] Warning: VITE_API_BASE_URL must use HTTPS in production: " + baseUrl);
    }
    return normalize(baseUrl);
  }

  if (overrideUrl && overrideUrl.startsWith("http://localhost")) return normalize(overrideUrl);

  return "";
}

export function buildApiUrl(path: string): string {
  const base = getApiBaseUrl();
  if (!path.startsWith("/")) path = "/" + path;
  return base + path;
}

// Backward compatibility for existing imports
export const apiUrl = buildApiUrl;
export const getApiBase = getApiBaseUrl;
export function isApiConfigured(): boolean {
  const base = getApiBaseUrl();
  if (!base) return true;
  return base.startsWith("https://") || base.startsWith("http://localhost");
}
`.trimStart();

console.log("🔹 Updating frontend API files...");

files.forEach((file) => {
  if (fs.existsSync(file)) {
    fs.writeFileSync(file, replacement, "utf8");
    console.log(`✅ Updated: ${file}`);
  } else {
    console.warn(`⚠️ File not found: ${file}`);
  }
});

function setVercelEnvVar(name, value) {
  try {
    execFileSync("vercel", ["env", "rm", name, "production", "--yes"], {
      stdio: "inherit",
    });
  } catch (cleanupError) {
    console.warn(
      `[deploy-api-fix] Env cleanup skipped for ${name}: ${cleanupError.message}`
    );
  }

  execFileSync("vercel", ["env", "add", name, value, "production", "--yes"], {
    stdio: "inherit",
  });
}

// Normalize VITE_API_BASE_URL for Vercel
console.log("\n🔹 Normalizing VITE_API_BASE_URL for Vercel...");
const envVar =
  process.env.VITE_API_BASE_URL || DEFAULT_API_BASE_URL;
const normalized = envVar.replace(/\/+$/, "");
console.log(`✅ Using: ${normalized}`);

// Optional: set via Vercel CLI
try {
  console.log("\n🔹 Setting Vercel environment variable...");
  setVercelEnvVar("VITE_API_BASE_URL", normalized);
  console.log("✅ VITE_API_BASE_URL set on Vercel (Production)");
} catch (err) {
  console.warn(
    "⚠️ Vercel CLI env set failed. Make sure Vercel CLI is installed and logged in."
  );
}

// Redeploy frontend
try {
  console.log("\n🔹 Deploying frontend to Vercel...");
  const autoConfirm = process.env.VERCEL_AUTO_CONFIRM !== "false";
  const deployArgs = ["--prod"];
  if (autoConfirm) deployArgs.push("--confirm");

  execFileSync("vercel", deployArgs, {
    stdio: "inherit",
    timeout: DEPLOY_TIMEOUT_MS,
  });
  console.log("🎉 Frontend redeployed successfully!");
} catch (err) {
  console.error(
    "❌ Frontend redeploy failed. Check Vercel CLI login and project directory."
  );
}
