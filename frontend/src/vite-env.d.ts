/// <reference types="vite/client" />
/// <reference types="react" />
/// <reference types="react-dom" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string
  readonly VITE_SOCKET_URL?: string
  readonly VITE_CLOUDINARY_CLOUD_NAME?: string
  readonly VITE_SENDBIRD_APP_ID?: string
  readonly DEV?: boolean
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

// Global constant injected by Vite at build time
// Provides safe fallback API URL when VITE_API_BASE_URL is not set
declare const __API_BASE__: string

// Extend Window interface for type-safe access to __API_BASE__
interface Window {
  __API_BASE__?: string
  __HIREME_ENV_INVALID__?: boolean
}
