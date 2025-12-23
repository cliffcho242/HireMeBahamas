/**
 * Safe VITE_API_BASE_URL Getter
 * 
 * ✅ Guarantees builds never fail even if env is missing
 * ✅ Logs a warning but does not block rendering
 * ✅ Provides a default fallback to Render backend
 */
export function getApiBase(): string {
  const url = import.meta.env.VITE_API_BASE_URL;

  if (!url || url.trim() === "") {
    console.warn(
      "⚠️ VITE_API_BASE_URL is missing. Falling back to default."
    );
    // Default fallback: your Render backend
    return "https://hiremebahamas-backend.onrender.com";
  }

  return url.replace(/\/$/, "");
}
