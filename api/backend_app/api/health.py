from fastapi import APIRouter

router = APIRouter()

@router.get("/health/ping")
def ping():
    return {"status": "ok"}
