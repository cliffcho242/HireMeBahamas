from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

# Minimal health-only FastAPI app for Render/Gunicorn fallback
app = FastAPI()


@app.get("/health", include_in_schema=False)
@app.head("/health", include_in_schema=False)
def health():
    return PlainTextResponse("ok", status_code=200)
