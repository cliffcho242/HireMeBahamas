# How to Add Serverless Functions to HireMeBahamas

## Overview

HireMeBahamas uses Vercel Serverless Functions to handle backend API requests. Each Python file in the `api/` directory automatically becomes a serverless endpoint.

## Existing Serverless Functions

The project already includes several serverless functions:

### Main Backend API
- **File**: `api/main.py`
- **Endpoint**: `/api/main` (also handles `/api/*` via rewrites)
- **Purpose**: Main FastAPI application with full backend functionality
- **Features**: 
  - Complete REST API (61+ endpoints)
  - Authentication & authorization
  - Database operations
  - User management
  - Job postings
  - Messaging
  - Profile management

### Health Check
- **File**: `api/cron/health.py`
- **Endpoint**: `/api/cron/health`
- **Purpose**: Keep-warm cron job and health monitoring
- **Schedule**: Every 5 minutes

### Hello World Example
- **File**: `api/hello.py`
- **Endpoint**: `/api/hello`
- **Purpose**: Example serverless function demonstrating the pattern
- **Methods**: GET, POST

## How Vercel Serverless Functions Work

### File-Based Routing

Vercel automatically maps files in the `api/` directory to HTTP endpoints:

```
api/hello.py        →  /api/hello
api/custom.py       →  /api/custom
api/foo/bar.py      →  /api/foo/bar
```

### Handler Pattern

Each serverless function must export a `handler` class or function:

#### Simple Handler (HTTP BaseHandler)

```python
from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        
        response = {
            "message": "Hello World",
            "status": "success"
        }
        self.wfile.write(json.dumps(response).encode())
```

#### FastAPI Handler (with Mangum)

```python
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI"}

handler = Mangum(app, lifespan="off")
```

## Step-by-Step: Adding a New Serverless Function

### Example 1: Simple Data API

Create `api/stats.py`:

```python
"""
Statistics API Endpoint
GET /api/stats - Returns platform statistics
"""

from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Set headers
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        
        # Generate response
        stats = {
            "total_users": 1500,
            "active_jobs": 42,
            "platform": "vercel-serverless",
            "region": os.getenv("VERCEL_REGION", "unknown")
        }
        
        self.wfile.write(json.dumps(stats).encode())
```

**Usage:**
```bash
curl https://your-app.vercel.app/api/stats
```

### Example 2: Form Submission Handler

Create `api/contact.py`:

```python
"""
Contact Form Submission Handler
POST /api/contact - Handles contact form submissions
"""

from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self._set_headers(200)
    
    def do_POST(self):
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            # Validate required fields
            name = data.get('name')
            email = data.get('email')
            message = data.get('message')
            
            if not all([name, email, message]):
                self._set_headers(400)
                response = {
                    "status": "error",
                    "message": "Missing required fields"
                }
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Process form submission (example: just return success)
            # In production, you might send email, save to database, etc.
            self._set_headers(200)
            response = {
                "status": "success",
                "message": "Thank you for contacting us!",
                "data": {
                    "name": name,
                    "email": email
                }
            }
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self._set_headers(500)
            response = {
                "status": "error",
                "message": str(e)
            }
            self.wfile.write(json.dumps(response).encode())
```

**Usage:**
```bash
curl -X POST https://your-app.vercel.app/api/contact \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "message": "Hello!"
  }'
```

### Example 3: Data Processing Function

Create `api/process-data.py`:

```python
"""
Data Processing Function
POST /api/process-data - Processes and transforms data
"""

from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Read input data
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            # Process data (example: uppercase transformation)
            items = data.get('items', [])
            processed = [item.upper() for item in items]
            
            # Return result
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            response = {
                "status": "success",
                "original_count": len(items),
                "processed_data": processed
            }
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
```

## Best Practices

### 1. Function Configuration

Add configuration to `vercel.json` or `vercel_immortal.json`:

```json
{
  "functions": {
    "api/custom.py": {
      "maxDuration": 10,
      "memory": 1024
    },
    "api/heavy-task.py": {
      "maxDuration": 30,
      "memory": 3008
    }
  }
}
```

**Options:**
- `maxDuration`: Timeout in seconds (10s free tier, up to 300s on paid plans)
- `memory`: RAM allocation in MB (128-3008)

### 2. Environment Variables

Access environment variables in your function:

```python
import os

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
```

Set them in Vercel Dashboard → Settings → Environment Variables

### 3. Error Handling

Always include proper error handling:

```python
def do_GET(self):
    try:
        # Your code here
        result = do_something()
        
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"data": result}).encode())
        
    except ValueError as e:
        # Client error (400)
        self.send_response(400)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": str(e)}).encode())
        
    except Exception as e:
        # Server error (500)
        self.send_response(500)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": "Internal server error"}).encode())
```

### 4. CORS Headers

For frontend access, include CORS headers:

```python
def _set_headers(self, status=200):
    self.send_response(status)
    self.send_header("Content-Type", "application/json")
    self.send_header("Access-Control-Allow-Origin", "*")
    self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
    self.end_headers()

def do_OPTIONS(self):
    """Handle CORS preflight"""
    self._set_headers(200)
```

### 5. Response Format

Use consistent JSON response format:

```python
# Success
{
    "status": "success",
    "data": {...},
    "message": "Operation completed"
}

# Error
{
    "status": "error",
    "message": "Error description",
    "code": "ERROR_CODE"
}
```

## Testing Serverless Functions

### Local Testing

Test locally before deploying:

```bash
# Install Vercel CLI
npm i -g vercel

# Run local dev server
vercel dev

# Test your function
curl http://localhost:3000/api/hello
```

### Production Testing

After deployment:

```bash
# Test GET endpoint
curl https://your-app.vercel.app/api/hello

# Test POST endpoint
curl -X POST https://your-app.vercel.app/api/hello \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User"}'
```

### Frontend Integration

Call from React/TypeScript frontend:

```typescript
// GET request
const response = await fetch('/api/hello');
const data = await response.json();
console.log(data);

// POST request
const response = await fetch('/api/contact', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    name: 'John Doe',
    email: 'john@example.com',
    message: 'Hello!'
  })
});
const data = await response.json();
```

## Advanced: Using FastAPI

For more complex APIs, use FastAPI with Mangum:

Create `api/advanced.py`:

```python
"""
Advanced API with FastAPI and Database
"""

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from mangum import Mangum
import os

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str
    price: float

@app.get("/")
async def root():
    return {"message": "Advanced API"}

@app.post("/items")
async def create_item(item: Item):
    # Save to database (example)
    return {
        "status": "success",
        "item": item.dict()
    }

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    # Fetch from database (example)
    if item_id not in [1, 2, 3]:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return {
        "id": item_id,
        "name": f"Item {item_id}",
        "price": 10.99
    }

# Wrap for Vercel
handler = Mangum(app, lifespan="off")
```

**Add dependencies** to `api/requirements.txt`:
```txt
fastapi
mangum
pydantic
```

## Limitations

### Vercel Serverless Constraints

- **Timeout**: 10s (free tier), up to 300s (paid plans)
- **Memory**: 1024 MB (free tier), up to 3008 MB (paid plans)
- **Deployment Size**: 50 MB compressed (function code + dependencies)
- **Cold Start**: 1-3 seconds (mitigated by keep-warm cron jobs)

### When to Use Separate Service

Consider using Railway/Render for:
- Long-running tasks (> 30 seconds)
- WebSocket connections
- File processing (> 50 MB)
- Heavy computation
- Background jobs

## Monitoring

### View Function Logs

1. Go to [Vercel Dashboard](https://vercel.com)
2. Select your project
3. Click "Functions" tab
4. View execution logs and metrics

### Add Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def do_GET(self):
    logger.info("Function invoked")
    # Your code
    logger.info("Function completed")
```

## Summary

**To add a new serverless function:**

1. Create a Python file in `api/` directory
2. Define a `handler` class (BaseHTTPRequestHandler) or function
3. Implement `do_GET()`, `do_POST()`, etc.
4. Handle errors and include CORS headers
5. Commit and push to GitHub
6. Vercel automatically deploys it

**Endpoints automatically available at:**
- `/api/<filename>`

**Examples in this project:**
- `/api/hello` - Hello world example (NEW)
- `/api/health` - Health check
- `/api/main` - Full backend API

See `api/hello.py` for a complete working example!
