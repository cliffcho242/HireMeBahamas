# Session Management & Post Persistence Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          User Interface                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  PostFeed    │  │  AuthProvider│  │ Components   │              │
│  │  Component   │  │   Context    │  │   (Others)   │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
└─────────┼──────────────────┼──────────────────┼─────────────────────┘
          │                  │                  │
          │                  │                  │
┌─────────┼──────────────────┼──────────────────┼─────────────────────┐
│         │     React Hooks & State Management  │                     │
│         │                  │                  │                     │
│  ┌──────▼───────┐   ┌──────▼────────┐   ┌────▼─────────┐          │
│  │useSessionTimeout│ │  useState     │   │  useEffect   │          │
│  │     Hook      │   │  useCallback  │   │  useContext  │          │
│  └──────┬───────┘   └───────────────┘   └──────────────┘          │
└─────────┼───────────────────────────────────────────────────────────┘
          │
          │
┌─────────┼───────────────────────────────────────────────────────────┐
│         │          Service Layer                                     │
│         │                                                            │
│  ┌──────▼──────────┐  ┌─────────────────┐  ┌──────────────────┐   │
│  │ Session Manager │  │   Post Cache    │  │   API Service    │   │
│  │─────────────────│  │─────────────────│  │──────────────────│   │
│  │• Activity Track │  │• IndexedDB      │  │• HTTP Requests   │   │
│  │• Session Store  │  │• Offline Queue  │  │• Token Mgmt      │   │
│  │• Timeout Mgmt   │  │• Cache Strategy │  │• Retry Logic     │   │
│  │• Token Monitor  │  │• Sync Manager   │  │• Interceptors    │   │
│  └─────┬───────────┘  └────┬────────────┘  └────┬─────────────┘   │
└────────┼────────────────────┼─────────────────────┼─────────────────┘
         │                    │                     │
         │                    │                     │
┌────────┼────────────────────┼─────────────────────┼─────────────────┐
│        │     Browser Storage & APIs               │                 │
│        │                    │                     │                 │
│  ┌─────▼────────┐    ┌─────▼─────────┐    ┌──────▼──────┐         │
│  │ localStorage │    │   IndexedDB   │    │   Network   │         │
│  │──────────────│    │───────────────│    │─────────────│         │
│  │• Token       │    │• Posts Cache  │    │• HTTP/HTTPS │         │
│  │• Session Data│    │• Pending      │    │• WebSocket  │         │
│  │• User Prefs  │    │  Actions      │    │• Fetch API  │         │
│  └──────────────┘    └───────────────┘    └─────┬───────┘         │
└────────────────────────────────────────────────────┼─────────────────┘
                                                     │
                                                     │
┌────────────────────────────────────────────────────┼─────────────────┐
│                         Backend Server             │                 │
│                                                    │                 │
│  ┌─────────────────────────────────────────────────▼──────────────┐ │
│  │                    Flask Application                           │ │
│  │────────────────────────────────────────────────────────────────│ │
│  │  Authentication Endpoints                                      │ │
│  │  • POST /api/auth/login      - User login                     │ │
│  │  • POST /api/auth/register   - User registration              │ │
│  │  • POST /api/auth/refresh    - Token refresh (NEW)            │ │
│  │  • GET  /api/auth/verify     - Session verification (NEW)     │ │
│  │                                                                │ │
│  │  Posts Endpoints                                               │ │
│  │  • GET    /api/posts         - Fetch all posts                │ │
│  │  • POST   /api/posts         - Create post                    │ │
│  │  • PUT    /api/posts/:id     - Update post                    │ │
│  │  • DELETE /api/posts/:id     - Delete post                    │ │
│  │  • POST   /api/posts/:id/like - Like/unlike post              │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    Middleware Stack                            │ │
│  │────────────────────────────────────────────────────────────────│ │
│  │  • CORS Handler      - Cross-origin requests                  │ │
│  │  • Rate Limiter      - Request throttling                     │ │
│  │  • JWT Validator     - Token verification                     │ │
│  │  • Error Handler     - Centralized error handling             │ │
│  │  • Cache Manager     - Response caching                       │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    Database Layer                              │ │
│  │────────────────────────────────────────────────────────────────│ │
│  │  PostgreSQL / SQLite                                           │ │
│  │  • users         - User accounts                               │ │
│  │  • posts         - Post content                                │ │
│  │  • likes         - Post likes                                  │ │
│  │  • comments      - Post comments                               │ │
│  └────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagrams

### 1. User Login Flow with Session Management

```
User Action          Frontend                  Backend              Storage
    │                   │                        │                    │
    │   Login Form      │                        │                    │
    ├──────────────────>│                        │                    │
    │                   │  POST /api/auth/login  │                    │
    │                   ├───────────────────────>│                    │
    │                   │                        │  Validate          │
    │                   │                        │  Credentials       │
    │                   │                        ├──>DB Query         │
    │                   │                        │<───────────        │
    │                   │    JWT Token + User    │                    │
    │                   │<───────────────────────┤                    │
    │                   │                        │                    │
    │                   │  Save Session          │                    │
    │                   ├───────────────────────────────────────────>│
    │                   │  (sessionManager)      │      localStorage  │
    │                   │                        │      + IndexedDB   │
    │                   │  Start Activity        │                    │
    │                   │  Tracking              │                    │
    │                   │                        │                    │
    │   Logged In       │                        │                    │
    │<──────────────────┤                        │                    │
```

### 2. Post Like with Optimistic Update & Offline Support

```
User Action          Frontend                  Backend              Storage
    │                   │                        │                    │
    │  Click Like       │                        │                    │
    ├──────────────────>│                        │                    │
    │                   │  Update UI             │                    │
    │                   │  (Optimistic)          │                    │
    │   UI Updates      │                        │                    │
    │<──────────────────┤                        │                    │
    │                   │                        │                    │
    │                   │  Online?               │                    │
    │                   ├───>YES                 │                    │
    │                   │     │                  │                    │
    │                   │     │ POST /posts/:id/like                 │
    │                   │     └─────────────────>│                    │
    │                   │                        │  Update DB         │
    │                   │                        ├──>                 │
    │                   │       Success          │                    │
    │                   │<───────────────────────┤                    │
    │                   │  Update Cache          │                    │
    │                   ├───────────────────────────────────────────>│
    │                   │                        │      IndexedDB     │
    │                   │                        │                    │
    │                   ├───>NO (Offline)        │                    │
    │                   │     │                  │                    │
    │                   │     │ Queue Action     │                    │
    │                   │     └─────────────────────────────────────>│
    │                   │                        │   Pending Actions  │
    │                   │                        │                    │
    │                   │  Connection Restored   │                    │
    │                   │<───────────────────────────────────────────┤
    │                   │                        │                    │
    │                   │  Sync Pending          │                    │
    │                   │  Actions               │                    │
    │                   ├───────────────────────>│                    │
```

### 3. Automatic Token Refresh Flow

```
Time                 Frontend                  Backend              Storage
    │                   │                        │                    │
    │  User Active      │                        │                    │
    │  (Any Action)     │                        │                    │
    ├──────────────────>│                        │                    │
    │                   │  Check Token           │                    │
    │                   │  Expiration            │                    │
    │                   ├───>Within 24h?         │                    │
    │                   │     │                  │                    │
    │                   │     YES                │                    │
    │                   │     │                  │                    │
    │                   │  POST /api/auth/refresh│                    │
    │                   ├───────────────────────>│                    │
    │                   │    Bearer <token>      │  Validate Token    │
    │                   │                        ├──>                 │
    │                   │                        │  Generate New      │
    │                   │                        │  Token (7d exp)    │
    │                   │    New Token + User    │                    │
    │                   │<───────────────────────┤                    │
    │                   │                        │                    │
    │                   │  Update Session        │                    │
    │                   ├───────────────────────────────────────────>│
    │                   │  (New Token)           │    localStorage    │
    │                   │                        │                    │
    │   Seamless        │                        │                    │
    │   Continuation    │                        │                    │
    │<──────────────────┤                        │                    │
```

### 4. Session Timeout with Warning Flow

```
Time                 Frontend                  User              Action
    │                   │                        │                 │
    │   25 min idle     │                        │                 │
    ├──────────────────>│                        │                 │
    │                   │  Show Warning          │                 │
    │                   │  Toast                 │                 │
    │                   ├───────────────────────>│                 │
    │                   │ "Session expiring in 5 minutes"          │
    │                   │ [Stay Logged In] [Dismiss]               │
    │                   │                        │                 │
    │                   │                        │  Click          │
    │                   │                        │  "Stay Logged   │
    │                   │                        │   In"           │
    │                   │                        ├────────────────>│
    │                   │                        │                 │
    │                   │  Extend Session        │                 │
    │                   │<───────────────────────┤                 │
    │                   │  (Reset Timer)         │                 │
    │                   │                        │                 │
    │                   │  OR                    │                 │
    │                   │                        │                 │
    │   30 min idle     │                        │  No Action      │
    ├──────────────────>│                        ├────────────────>│
    │                   │  Clear Session         │                 │
    │                   │  Redirect to Login     │                 │
    │                   │                        │                 │
    │                   │  Show Message          │                 │
    │                   ├───────────────────────>│                 │
    │                   │  "Session expired"     │                 │
```

## Key Components Interaction

### Session Manager Interaction
```
┌─────────────────────────────────────────────────┐
│           Session Manager                       │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │  Activity Tracking                       │  │
│  │  • Mouse events                          │  │
│  │  • Keyboard events                       │  │
│  │  • Touch events                          │  │
│  │  • Scroll events                         │  │
│  │  └──> Updates: lastActivity timestamp   │  │
│  └──────────────────────────────────────────┘  │
│                     │                           │
│                     ▼                           │
│  ┌──────────────────────────────────────────┐  │
│  │  Timeout Management                      │  │
│  │  • Warning timer (25 min)                │  │
│  │  • Expiration timer (30 min)             │  │
│  │  • Reset on activity                     │  │
│  └──────────────────────────────────────────┘  │
│                     │                           │
│                     ▼                           │
│  ┌──────────────────────────────────────────┐  │
│  │  Session Storage                         │  │
│  │  • Save to localStorage (encoded)        │  │
│  │  • Load from localStorage                │  │
│  │  • Validate expiration                   │  │
│  │  • Clear on logout/timeout               │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

### Post Cache Interaction
```
┌─────────────────────────────────────────────────┐
│             Post Cache                          │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │  Cache Management                        │  │
│  │  • Store posts in IndexedDB              │  │
│  │  • 5-minute TTL                          │  │
│  │  • Automatic invalidation                │  │
│  └──────────────────────────────────────────┘  │
│                     │                           │
│                     ▼                           │
│  ┌──────────────────────────────────────────┐  │
│  │  Offline Queue                           │  │
│  │  • Store pending actions                 │  │
│  │  • Retry logic (3 attempts)              │  │
│  │  • Auto-sync on reconnect                │  │
│  └──────────────────────────────────────────┘  │
│                     │                           │
│                     ▼                           │
│  ┌──────────────────────────────────────────┐  │
│  │  Sync Manager                            │  │
│  │  • Background sync (30s)                 │  │
│  │  • Fetch fresh data                      │  │
│  │  • Process pending actions               │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## Configuration Summary

```javascript
// Session Configuration
SESSION_TIMEOUT = 30 minutes          // Idle timeout
WARNING_THRESHOLD = 5 minutes         // Warning before timeout
TOKEN_REFRESH_THRESHOLD = 24 hours    // Refresh window
TOKEN_EXPIRATION = 7 days             // JWT expiration

// Cache Configuration
CACHE_DURATION = 5 minutes            // Post cache TTL
SYNC_INTERVAL = 30 seconds            // Background sync
MAX_RETRIES = 3                       // Failed action retries

// Rate Limiting
AUTH_ENDPOINTS = 10 per minute        // Token operations
DEFAULT = 50 per hour, 200 per day    // General API
```

## Browser Storage Usage

```
localStorage (Persistent)
├── token                  // JWT token (backward compat)
├── hireme_session         // Encoded session data
├── hireme_last_activity   // Last activity timestamp
└── hireme_user            // User object cache

IndexedDB (Persistent)
├── HireMeBahamasDB
    ├── posts              // Cached posts (with TTL)
    │   └── { id, content, cachedAt, ... }
    └── pendingActions     // Offline action queue
        └── { id, type, postId, data, retryCount }
```

## Security Model

```
┌─────────────────────────────────────────────────┐
│              Security Layers                    │
├─────────────────────────────────────────────────┤
│ 1. Token-based Authentication (JWT)            │
│    • 7-day expiration                           │
│    • HS256 algorithm                            │
│    • Refresh before expiration                  │
├─────────────────────────────────────────────────┤
│ 2. Session Encoding                             │
│    • Base64 encoding (basic obfuscation)        │
│    • Not encryption (security through HTTPS)    │
├─────────────────────────────────────────────────┤
│ 3. Rate Limiting                                │
│    • Auth endpoints: 10/min                     │
│    • General: 50/hour, 200/day                  │
├─────────────────────────────────────────────────┤
│ 4. Activity-based Timeouts                     │
│    • 30-minute idle timeout                     │
│    • Automatic logout                           │
├─────────────────────────────────────────────────┤
│ 5. CORS Protection                              │
│    • Configured allowed origins                 │
│    • No credentials with wildcard               │
└─────────────────────────────────────────────────┘
```
