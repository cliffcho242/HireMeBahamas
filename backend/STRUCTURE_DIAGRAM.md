# HireMeBahamas Backend Structure - Visual Guide

## 📐 Directory Structure

```
backend/
├── app/
│   │
│   ├── main.py                          # 🎯 Application Entry Point
│   │                                     # Wires routers together
│   │                                     # (Production version with necessary features)
│   │
│   ├── main_simple_example.py           # 📘 Example: Ideal Structure
│   │                                     # Shows the minimal main.py pattern
│   │                                     # Only 25 lines - just router wiring!
│   │
│   ├── core/                            # 🏗️  Core Infrastructure
│   │   ├── __init__.py
│   │   ├── config.py                    # ⚙️  Configuration Management
│   │   │                                 # - Settings class
│   │   │                                 # - All env var reads
│   │   │                                 # - Database URL validation
│   │   │
│   │   ├── database.py                  # 🗄️  Database Layer
│   │   │                                 # - Engine creation
│   │   │                                 # - Session management
│   │   │                                 # - Connection pooling
│   │   │                                 # - Initialization with retry
│   │   │
│   │   ├── security.py                  # 🔐 Security & Auth
│   │   ├── metrics.py                   # 📊 Monitoring
│   │   ├── redis_cache.py               # 💾 Caching
│   │   └── ...                          # Other core modules
│   │
│   ├── api/                             # 🛣️  API Routes
│   │   ├── __init__.py
│   │   ├── auth.py                      # 🔑 Authentication endpoints
│   │   ├── users.py                     # 👤 User management
│   │   ├── jobs.py                      # 💼 Job postings
│   │   ├── messages.py                  # 💬 Messaging
│   │   ├── posts.py                     # 📝 Social posts
│   │   └── ...                          # Other API routers
│   │
│   ├── models/                          # 📦 Database Models
│   │   ├── __init__.py
│   │   └── ...                          # SQLAlchemy models
│   │
│   ├── schemas/                         # 📋 Pydantic Schemas
│   │   ├── __init__.py
│   │   ├── auth.py                      # Auth request/response models
│   │   ├── job.py                       # Job models
│   │   └── ...                          # Other schemas
│   │
│   └── database.py                      # 🔄 Re-export Module
│                                         # Simple re-exports from core.database
│                                         # Maintains backward compatibility
│
├── PROJECT_STRUCTURE.md                 # 📖 Architecture Documentation
├── STRUCTURE_REFACTOR_SUMMARY.md        # 📝 Refactoring Summary
└── STRUCTURE_DIAGRAM.md                 # 📐 This file
```

## 🔄 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         main.py                                  │
│                    (Application Entry)                           │
│                                                                   │
│  1. Import FastAPI                                               │
│  2. Import routers from app.api                                  │
│  3. Create FastAPI() instance                                    │
│  4. Include routers                                              │
│  5. Define health endpoint                                       │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │        app.api.*             │
        │      (API Routers)           │
        │                              │
        │  - auth.router               │
        │  - users.router              │
        │  - jobs.router               │
        │  - ...                       │
        └──────┬───────────────────────┘
               │
               ▼
    ┌──────────────────────────┐         ┌────────────────────────┐
    │   Depends(get_db)        │────────▶│   core.database.py     │
    │   (Database Dependency)  │         │   (Database Layer)     │
    └──────────────────────────┘         └────────┬───────────────┘
                                                   │
                                                   ▼
                                         ┌─────────────────────┐
                                         │   core.config.py    │
                                         │   (Configuration)   │
                                         └─────────────────────┘
```

## 🎯 Module Responsibilities

### main.py
```python
Role: Application wiring
Responsibilities:
  - Import FastAPI
  - Import routers
  - Include routers  
  - Define health endpoint
Does NOT:
  - Read environment variables
  - Create database connections
  - Contain business logic
```

### core/config.py
```python
Role: Configuration management
Responsibilities:
  - Define Settings class
  - Read all environment variables
  - Provide configuration values
  - Validate DATABASE_URL
Does NOT:
  - Create connections
  - Handle requests
  - Define routes
```

### core/database.py  
```python
Role: Database layer
Responsibilities:
  - Create async engine
  - Manage connection pool
  - Provide session factory
  - Initialize tables
  - Health checks
Does NOT:
  - Read env vars (uses config.py)
  - Define routes
  - Contain business logic
```

### api/*.py
```python
Role: API route handlers
Responsibilities:
  - Define APIRouter
  - Define endpoints
  - Implement business logic
  - Use Depends(get_db)
Does NOT:
  - Create database connections
  - Read env vars directly
  - Mix concerns
```

## 🚀 Request Flow Example

User makes request to `/api/users/123`:

```
1. Request arrives at FastAPI (main.py)
   │
   ▼
2. Router matches: users.router (/api/users/{user_id})
   │
   ▼
3. Endpoint function called with:
   - user_id: int = 123
   - db: AsyncSession = Depends(get_db)  ──┐
   │                                        │
   ▼                                        │
4. get_db() dependency executed  ◀─────────┘
   │ (from core.database)
   ▼
5. AsyncSessionLocal() creates session
   │ (uses engine from core.database)
   ▼
6. Session used to query database
   │
   ▼
7. Results returned to endpoint
   │
   ▼
8. Pydantic schema validates response
   │
   ▼
9. JSON response sent to user
```

## 📊 Before vs After Comparison

### BEFORE (Problems)

```
main.py (769 lines)
├── Import os, logging, json, uuid, time
├── Read DATABASE_URL from os.getenv()
├── Create database engine
├── Define middleware
├── Configure logging
├── Import routers
├── Include routers  
├── Define health endpoints
└── Socket.IO setup

Issues:
❌ Mixed concerns
❌ Hard to test
❌ Difficult to maintain
❌ No clear structure
```

### AFTER (Solution)

```
core/config.py (95 lines)
├── Settings class
└── All env var reads

core/database.py (564 lines)
├── Engine creation
├── Session management
└── All database logic

main_simple_example.py (25 lines)
├── Import FastAPI
├── Import routers
├── Create app
├── Include routers
└── Health endpoint

Benefits:
✅ Clear separation
✅ Easy to test
✅ Simple to maintain
✅ Obvious structure
```

## 🎓 Key Takeaways

1. **One Module, One Responsibility**
   - Config → config.py
   - Database → database.py
   - Routes → api/*.py
   - Wiring → main.py

2. **Dependency Injection**
   - Use `Depends(get_db)` not direct imports
   - Use `Depends(get_current_user)` for auth
   - Let FastAPI handle dependencies

3. **Import Hierarchy**
   ```
   main.py
     └─▶ api/*.py
          └─▶ database.py (or core.database)
               └─▶ core/config.py
                    └─▶ os.getenv()
   ```

4. **Testing Strategy**
   - Test config.py independently
   - Test database.py with mocks
   - Test routers with test fixtures
   - Test main.py with integration tests

## 📚 Further Reading

- **PROJECT_STRUCTURE.md** - Detailed architecture guide
- **STRUCTURE_REFACTOR_SUMMARY.md** - Complete refactoring story
- **main_simple_example.py** - Clean code example
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
