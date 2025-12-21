from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI()


@app.get("/api/health")
@app.head("/api/health")
def health():
    return PlainTextResponse("ok", status_code=200)
