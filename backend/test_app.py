from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Test API")

# Test app CORS configuration - for development/testing only
# ⚠️ WARNING: This configuration is permissive for testing purposes
# Production apps should use specific origins, methods, and headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Required when using wildcard origins
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    import os

    port = int(os.getenv('PORT', 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
