from fastapi import APIRouter

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)

@router.get("/")
def get_health():
    return {"status": "healthy"}
