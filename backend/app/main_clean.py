"""
HireMeBahamas API - Main Application Entry Point

This file ONLY wires things together:
- Imports FastAPI
- Imports routers from app.api
- Includes routers
- Adds simple health endpoint

NO database logic, NO env reads, NO business logic.
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
