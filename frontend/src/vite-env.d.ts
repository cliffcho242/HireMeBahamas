/// <reference types="vite/client" />
/// <reference types="react" />
/// <reference types="react-dom" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_SOCKET_URL: string
  readonly VITE_CLOUDINARY_CLOUD_NAME: string
  readonly VITE_SENDBIRD_APP_ID: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
