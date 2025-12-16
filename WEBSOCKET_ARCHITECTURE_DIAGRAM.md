# WebSocket Real-Time Architecture Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   Browser    │  │   Mobile     │  │   Desktop    │              │
│  │   (React)    │  │   (React     │  │   (Electron) │              │
│  │              │  │   Native)    │  │              │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                  │                  │                      │
│         │  Socket.IO       │  Socket.IO       │  Socket.IO          │
│         │  Client          │  Client          │  Client             │
│         └──────────────────┴──────────────────┘                     │
│                            │                                         │
└────────────────────────────┼─────────────────────────────────────────┘
                             │
                             │ WebSocket (WSS)
                             │ JWT Auth in handshake
                             │
┌────────────────────────────┼─────────────────────────────────────────┐
│                            ▼                                          │
│                     LOAD BALANCER                                     │
│                  (Sticky Sessions)                                    │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  • Route based on session cookie                            │   │
│  │  • Enable WebSocket upgrade                                 │   │
│  │  • Timeout: 60+ seconds                                     │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                            │                                          │
└────────────────────────────┼─────────────────────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   Worker 1   │  │   Worker 2   │  │   Worker 3   │              │
│  │              │  │              │  │              │              │
│  │  Flask App   │  │  Flask App   │  │  Flask App   │              │
│  │  + SocketIO  │  │  + SocketIO  │  │  + SocketIO  │              │
│  │              │  │              │  │              │              │
│  │ ┌──────────┐ │  │ ┌──────────┐ │  │ ┌──────────┐ │              │
│  │ │WebSocket │ │  │ │WebSocket │ │  │ │WebSocket │ │              │
│  │ │Manager   │ │  │ │Manager   │ │  │ │Manager   │ │              │
│  │ └────┬─────┘ │  │ └────┬─────┘ │  │ └────┬─────┘ │              │
│  └──────┼───────┘  └──────┼───────┘  └──────┼───────┘              │
│         │                  │                  │                      │
│         └──────────────────┴──────────────────┘                     │
│                            │                                         │
└────────────────────────────┼─────────────────────────────────────────┘
                             │
                             │ Message Queue
                             │
┌────────────────────────────┼─────────────────────────────────────────┐
│                            ▼                                          │
│                     REDIS PUB/SUB                                     │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Channels:                                                   │   │
│  │  • notifications        - Personal notifications             │   │
│  │  • like_updates         - Like count broadcasts              │   │
│  │  • comment_updates      - Comment count broadcasts           │   │
│  │  • user_status          - Online/offline events              │   │
│  │  • conversations:{id}   - Chat messages                      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
                             │
                             │
┌────────────────────────────┼─────────────────────────────────────────┐
│                            ▼                                          │
│                   DATABASE LAYER                                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                     PostgreSQL                                │  │
│  │                                                               │  │
│  │  Tables:                                                      │  │
│  │  • users           - User accounts                           │  │
│  │  • posts           - User posts                              │  │
│  │  • likes           - Post likes                              │  │
│  │  • comments        - Post comments                           │  │
│  │  • follows         - Follow relationships                    │  │
│  │  • messages        - Chat messages                           │  │
│  │  • conversations   - Chat conversations                      │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

## Event Flow Diagrams

### 1. Like Notification Flow

```
User A likes User B's post
         │
         ▼
┌─────────────────────┐
│  Client A           │
│  (Browser)          │
│                     │
│  POST /api/posts/   │
│       123/like      │
└──────────┬──────────┘
           │ HTTP Request
           │ (with JWT)
           ▼
┌─────────────────────┐
│  Flask Backend      │
│                     │
│  1. Verify JWT      │◄─────────────┐
│  2. Insert like     │               │
│  3. Get count       │               │
│  4. Send WebSocket  │               │
└──────────┬──────────┘               │
           │                          │
           ├─────────────┐            │
           │             │            │
           ▼             ▼            │
   ┌─────────────┐ ┌─────────────┐   │
   │ PostgreSQL  │ │   Redis     │   │
   │             │ │  Pub/Sub    │   │
   │ INSERT like │ │ PUBLISH     │   │
   │ COUNT likes │ │ "like_      │   │
   └─────────────┘ │  update"    │   │
                   └──────┬──────┘   │
                          │           │
                          │ Broadcast │
                          │           │
           ┌──────────────┴───────────┴────────┐
           │              │                    │
           ▼              ▼                    ▼
   ┌───────────┐  ┌───────────┐      ┌───────────┐
   │ Client A  │  │ Client B  │      │ Client C  │
   │           │  │           │      │           │
   │ Response  │  │ Notif +   │      │ Count     │
   │ 200 OK    │  │ Count     │      │ Update    │
   └───────────┘  └───────────┘      └───────────┘
                        │
                        └──> Shows: "User A liked your post"
                              + updates like count
```

### 2. Multi-User Chat Flow

```
User A types in conversation with User B
         │
         ▼
┌─────────────────────┐
│  Client A           │
│                     │
│  socket.emit(       │
│    'typing',        │
│    {is_typing: true}│
│  )                  │
└──────────┬──────────┘
           │ WebSocket
           │
           ▼
┌─────────────────────┐
│  Flask Backend      │
│  (Any Worker)       │
│                     │
│  @sio.on('typing')  │
│  def handle()       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Redis Pub/Sub      │
│                     │
│  PUBLISH            │
│  "conversation_123" │
│  {typing: true}     │
└──────────┬──────────┘
           │
           │ Fanout
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌─────────┐  ┌─────────┐
│ Worker 1│  │ Worker 2│
└────┬────┘  └────┬────┘
     │            │
     ▼            ▼
┌─────────┐  ┌─────────┐
│Client A │  │Client B │
│         │  │         │
│ (self)  │  │ Shows:  │
│         │  │ "A is   │
│         │  │ typing.."│
└─────────┘  └─────────┘
```

### 3. Real-Time Notification Delivery

```
Event Occurs (like, comment, follow)
         │
         ▼
┌─────────────────────────────┐
│  notification_manager       │
│  .send_notification()       │
│                             │
│  Parameters:                │
│  - user_id: "123"          │
│  - data: {                  │
│      type: "like",          │
│      message: "...",        │
│      post_id: 456           │
│    }                        │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Find user's active         │
│  WebSocket connections      │
│                             │
│  user_rooms["123"]          │
│  = ["sid_abc", "sid_xyz"]   │
└──────────┬──────────────────┘
           │
           │ Send to each connection
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌─────────┐  ┌─────────┐
│Browser  │  │ Mobile  │
│Session  │  │ Session │
│         │  │         │
│ Shows   │  │ Shows   │
│ toast   │  │ push    │
│ notif   │  │ notif   │
└─────────┘  └─────────┘
```

## Data Flow

### WebSocket Connection Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                    CONNECTION PHASE                          │
└─────────────────────────────────────────────────────────────┘
  
  Client                     Server                    Database
    │                          │                          │
    │ 1. Connect with JWT      │                          │
    ├─────────────────────────>│                          │
    │                          │                          │
    │                          │ 2. Verify JWT            │
    │                          ├─────────────────────────>│
    │                          │                          │
    │                          │ 3. User valid            │
    │                          │<─────────────────────────┤
    │                          │                          │
    │                          │ 4. Add to active         │
    │                          │    connections           │
    │                          │                          │
    │                          │ 5. Join user room        │
    │                          │                          │
    │ 6. Connection confirmed  │                          │
    │<─────────────────────────┤                          │
    │                          │                          │
    │                          │ 7. Broadcast online      │
    │                          │    status                │
    │                          │                          │

┌─────────────────────────────────────────────────────────────┐
│                     ACTIVE PHASE                            │
└─────────────────────────────────────────────────────────────┘

    │                          │                          │
    │ Heartbeat (ping)         │                          │
    ├─────────────────────────>│                          │
    │                          │                          │
    │ Heartbeat (pong)         │                          │
    │<─────────────────────────┤                          │
    │                          │                          │
    │                          │ Event occurs             │
    │                          │ (like, comment, etc)     │
    │                          │<─────────                │
    │                          │                          │
    │ Receive notification     │                          │
    │<─────────────────────────┤                          │
    │                          │                          │
    │ Receive count update     │                          │
    │<─────────────────────────┤                          │
    │                          │                          │

┌─────────────────────────────────────────────────────────────┐
│                   DISCONNECT PHASE                          │
└─────────────────────────────────────────────────────────────┘

    │                          │                          │
    │ Disconnect               │                          │
    ├─────────────────────────>│                          │
    │                          │                          │
    │                          │ Remove from active       │
    │                          │ connections              │
    │                          │                          │
    │                          │ Leave user room          │
    │                          │                          │
    │                          │ Broadcast offline        │
    │                          │ status (if last session) │
    │                          │                          │
```

## Scaling Architecture

### Single Worker (Development)

```
┌─────────────┐
│  Client 1   │──┐
└─────────────┘  │
                 │
┌─────────────┐  │    ┌──────────────────┐    ┌──────────┐
│  Client 2   │──┼───>│  Flask + SocketIO│───>│PostgreSQL│
└─────────────┘  │    │  (Single Worker) │    └──────────┘
                 │    └──────────────────┘
┌─────────────┐  │
│  Client 3   │──┘
└─────────────┘

• In-memory message passing
• Simple setup
• Up to ~1,000 connections
```

### Multi-Worker (Production)

```
┌─────────────┐      ┌─────────────────┐
│  Client 1   │─────>│   Worker 1      │
└─────────────┘      │  Flask+SocketIO │
                     └────────┬─────────┘
                              │
┌─────────────┐               │         ┌──────────┐
│  Client 2   │─────┐         ├────────>│  Redis   │
└─────────────┘     │         │         │ Pub/Sub  │
                    ├────────>│         └────┬─────┘
┌─────────────┐     │         │              │
│  Client 3   │─────┘    ┌────┴─────────┐   │
└─────────────┘          │   Worker 2   │   │
                         │ Flask+SocketIO│   │
                         └────────┬──────┘   │
                                  │          │
┌─────────────┐          ┌───────┴──────┐   │
│  Client 4   │─────────>│   Worker 3   │   │
└─────────────┘          │ Flask+SocketIO│   │
                         └───────┬───────┘   │
                                 │           │
                                 └───────────┘
                                      │
                              ┌───────▼──────┐
                              │  PostgreSQL  │
                              └──────────────┘

• Redis message queue
• Horizontal scaling
• Load balanced
• 10,000+ connections
```

## Component Interaction

```
┌───────────────────────────────────────────────────────────────┐
│                    WEBSOCKET MANAGER                           │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐ │
│  │ Connection     │  │ Room           │  │ Event          │ │
│  │ Manager        │  │ Manager        │  │ Handler        │ │
│  │                │  │                │  │                │ │
│  │ • Track users  │  │ • User rooms   │  │ • Connect      │ │
│  │ • Track sids   │  │ • Convo rooms  │  │ • Disconnect   │ │
│  │ • Track status │  │ • Join/Leave   │  │ • Ping/Pong    │ │
│  └────────────────┘  └────────────────┘  │ • Typing       │ │
│                                           │ • Messages     │ │
│  ┌────────────────┐  ┌────────────────┐  └────────────────┘ │
│  │ Notification   │  │ Broadcasting   │                     │
│  │ Sender         │  │ Manager        │                     │
│  │                │  │                │                     │
│  │ • Direct msg   │  │ • Broadcast    │                     │
│  │ • Room msg     │  │ • Room cast    │                     │
│  │ • Validation   │  │ • Skip sender  │                     │
│  └────────────────┘  └────────────────┘                     │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

## Security Layers

```
┌───────────────────────────────────────────────────────────────┐
│                      CLIENT REQUEST                            │
└───────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌───────────────────────────────────────────────────────────────┐
│  LAYER 1: Transport Security                                   │
│  • WSS (WebSocket Secure)                                      │
│  • TLS 1.2+                                                    │
└───────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌───────────────────────────────────────────────────────────────┐
│  LAYER 2: Authentication                                       │
│  • JWT token verification                                      │
│  • Token in handshake                                          │
│  • Reject invalid tokens                                       │
└───────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌───────────────────────────────────────────────────────────────┐
│  LAYER 3: Authorization                                        │
│  • User-specific notifications                                 │
│  • Room access control                                         │
│  • Data filtering                                              │
└───────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌───────────────────────────────────────────────────────────────┐
│  LAYER 4: Rate Limiting                                        │
│  • Connection rate limits                                      │
│  • Event rate limits                                           │
│  • Auto-disconnect abuse                                       │
└───────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌───────────────────────────────────────────────────────────────┐
│  LAYER 5: Validation                                           │
│  • Input validation                                            │
│  • Data sanitization                                           │
│  • Type checking                                               │
└───────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌───────────────────────────────────────────────────────────────┐
│                   PROCESS REQUEST                              │
└───────────────────────────────────────────────────────────────┘
```

---

This architecture provides:
- ✅ Real-time communication
- ✅ Horizontal scalability
- ✅ High availability
- ✅ Security at every layer
- ✅ Performance optimization
- ✅ Fault tolerance
