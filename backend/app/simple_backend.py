from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI(
    title="HireMeBahamas API",
    description="Job platform API for the Bahamas",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "HireMeBahamas API is running"}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to HireMeBahamas API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Simple auth endpoints for testing
@app.post("/auth/register")
async def register():
    return {"message": "Registration endpoint - ready for implementation"}

@app.post("/auth/login")
async def login():
    return {"message": "Login endpoint - ready for implementation"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)