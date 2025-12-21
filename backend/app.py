from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI()


@app.get("/health")
@app.head("/health")
def health():
    return PlainTextResponse("ok", status_code=200)
