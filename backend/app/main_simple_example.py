"""
HireMeBahamas API - Simple Structure Example

This demonstrates the IDEAL FastAPI project structure where main.py
ONLY wires things together with NO database logic, NO env reads, NO business logic.

NOTE: This is a simplified example. The actual main.py includes additional
complexity for Pydantic forward reference fixes and production features.

For the working production version, see: main.py
"""
from fastapi import FastAPI

from app.api import auth, users, jobs

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(jobs.router)


@app.get("/health")
def health():
    return {"status": "ok"}
